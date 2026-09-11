"""
Tests for TransactionRouter (Action Plan 09): the tx_id correlation layer.

Uses an in-memory fake transport (no real sockets) for unit coverage, plus one
integration test over the real SocketByteTransport + DelimiterCodec against a
local asyncio echo server (mirroring the chunk-05 test fixture).
"""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import pytest

from foundation_abc.peripheralByteTransport import PeripheralByteTransport
from foundation_tools.socket_transaction import DelimiterCodec, SocketByteTransport
from foundation_tools.socket_transaction.transaction_router import (
    ConnectionClosedError,
    TransactionRouter,
)
from tests.asyncio_server import running_server


class _IdentityCodec:
    """No-op codec: each `receive` chunk from the fake transport is one frame."""

    def encode(self, payload: bytes) -> bytes:
        return payload

    def feed(self, data: bytes) -> list[bytes]:
        return [data] if data else []


def _inject(payload: bytes, tx_id: str) -> bytes:
    """Stamp `tx_id:` onto payload, overwriting any prior stamp (never duplicating)."""
    before, sep, after = payload.partition(b":")
    body = after if sep else payload
    del before
    return f"{tx_id}:".encode() + body


def _extract(frame: bytes) -> str | None:
    prefix, sep, _ = frame.partition(b":")
    if not sep:
        return None
    try:
        return prefix.decode("ascii")
    except UnicodeDecodeError:
        return None


class FakeTransport(PeripheralByteTransport):
    """In-memory PeripheralByteTransport: an inbound queue driven entirely by the
    test (or by echo mode), with no real I/O."""

    def __init__(self) -> None:
        self._connected = False
        self._inbound: asyncio.Queue[bytes | BaseException] = asyncio.Queue()
        self.sent: list[bytes] = []
        self._echo = False

    async def connect(self) -> None:
        self._connected = True

    async def disconnect(self) -> None:
        self._connected = False

    async def send(self, data: bytes) -> None:
        if not self._connected:
            raise RuntimeError("Cannot send: transport is not connected")
        self.sent.append(data)
        if self._echo:
            self._inbound.put_nowait(data)

    async def receive(self, size: int, timeout: float = 1.0) -> bytes:
        if not self._connected:
            raise RuntimeError("Cannot receive: transport is not connected")
        try:
            item = await asyncio.wait_for(self._inbound.get(), timeout=timeout)
        except (asyncio.TimeoutError, TimeoutError):
            raise TimeoutError("receive timed out") from None
        if isinstance(item, BaseException):
            raise item
        return item

    @property
    def is_connected(self) -> bool:
        return self._connected

    def enable_echo(self) -> None:
        self._echo = True

    def push_inbound(self, frame: bytes) -> None:
        self._inbound.put_nowait(frame)

    def push_eof(self) -> None:
        self._inbound.put_nowait(b"")

    def push_error(self, error: BaseException) -> None:
        self._inbound.put_nowait(error)


def _make_router(transport: PeripheralByteTransport, **overrides: object) -> TransactionRouter:
    defaults: dict[str, object] = {
        "tx_id_injector": _inject,
        "tx_id_extractor": _extract,
        "poll_timeout": 0.02,
    }
    defaults.update(overrides)
    return TransactionRouter(transport, _IdentityCodec(), **defaults)  # type: ignore[arg-type]


@asynccontextmanager
async def _running_router(
    transport: FakeTransport, **overrides: object
) -> AsyncIterator[TransactionRouter]:
    await transport.connect()
    router = _make_router(transport, **overrides)
    router.start()
    try:
        yield router
    finally:
        await router.stop()


class SynchronousReplyTransport(FakeTransport):
    """A transport whose ``send`` synchronously delivers the correlated reply
    to the reader loop before ``send`` itself returns — engineered await-point
    interleaving (not sleeps/timing luck) that proves the response future is
    registered in the pending map before ``send`` completes, not after. The
    current ``FakeTransport.send`` has no await point, so this race can never
    interleave with the plain fixture; this subclass exists to make it
    deterministic."""

    async def send(self, data: bytes) -> None:
        await super().send(data)
        self.push_inbound(data)  # echo the frame back as the correlated reply
        await asyncio.sleep(0)  # reader task runs here
        await asyncio.sleep(0)  # ... and resolves the future


class TestRegisterBeforeSendRace:
    @pytest.mark.asyncio
    async def test_future_registered_before_send_completes(self) -> None:
        """Regression test for the exact register-before-send ordering the
        chunk-09 implementation notes describe: if the future were registered
        AFTER ``send`` instead of before, this reply would arrive with no
        pending future to resolve (misrouted to the unsolicited stream), and
        ``request`` would time out instead of returning the reply.
        """
        transport = SynchronousReplyTransport()
        async with _running_router(transport) as router:
            reply = await router.request(b"race-ping", timeout=1.0)
        assert reply.endswith(b"race-ping")


class _FlakyInjector:
    """A ``tx_id_injector`` that raises on its first ``fail_times`` calls, then
    delegates to the working ``_inject``. Models an injector that fails while
    stamping a generated tx_id into the payload (fix candidate 09)."""

    def __init__(self, fail_times: int) -> None:
        self._remaining = fail_times
        self.calls = 0

    def __call__(self, payload: bytes, tx_id: str) -> bytes:
        self.calls += 1
        if self._remaining > 0:
            self._remaining -= 1
            raise RuntimeError("injector boom")
        return _inject(payload, tx_id)


class TestRequestRegistrationAtomicity:
    """Fix candidate 09: frame preparation and pending registration are one
    rollback-safe unit. An injector failure must leave no orphan future in
    ``_pending``, and the generated tx_id must remain reusable by a later
    request."""

    @pytest.mark.asyncio
    async def test_injector_failure_rolls_back_registration(self) -> None:
        transport = FakeTransport()
        transport.enable_echo()
        injector = _FlakyInjector(fail_times=1)
        async with _running_router(
            transport,
            tx_id_injector=injector,
            tx_id_generator=lambda: "regen-1",
        ) as router:
            with pytest.raises(RuntimeError, match="injector boom"):
                await router.request(b"first", timeout=1.0)

            # (a) no orphan future left behind, and nothing was ever written to
            # the transport (failure happened before the first awaited send).
            assert router._pending == {}
            assert transport.sent == []

            # (b) the same generated id ("regen-1") is reusable: a leaked pending
            # entry would make this raise RuntimeError("... already in-flight").
            reply = await router.request(b"second", timeout=1.0)
            assert reply.endswith(b"second")
            assert _extract(transport.sent[0]) == "regen-1"

        assert router._pending == {}


class TestRequestReplyCorrelation:
    @pytest.mark.asyncio
    async def test_single_request_reply_round_trip(self) -> None:
        transport = FakeTransport()
        transport.enable_echo()
        async with _running_router(transport) as router:
            reply = await router.request(b"ping", timeout=1.0)
        assert reply.endswith(b"ping")

    @pytest.mark.asyncio
    async def test_concurrent_requests_out_of_order_resolve_correctly(self) -> None:
        transport = FakeTransport()
        async with _running_router(transport) as router:
            tasks = [
                asyncio.ensure_future(router.request(f"payload-{i}".encode(), timeout=2.0))
                for i in range(5)
            ]
            await asyncio.sleep(0.05)  # let all sends land in transport.sent

            # Reply out of order, deliberately reversed relative to send order.
            for sent_frame in reversed(transport.sent):
                transport.push_inbound(sent_frame)

            results = await asyncio.gather(*tasks)
        # gather() preserves input order regardless of reply arrival order; each
        # task must resolve to its own request's echoed frame, not another's.
        assert results == transport.sent


class TestTxIdMechanics:
    @pytest.mark.asyncio
    async def test_injector_round_trip_survives_echo(self) -> None:
        transport = FakeTransport()
        transport.enable_echo()
        async with _running_router(transport) as router:
            reply = await router.request(b"hello", timeout=1.0)
        sent_frame = transport.sent[0]
        tx_id = _extract(sent_frame)
        assert tx_id is not None
        assert reply == sent_frame
        assert _extract(reply) == tx_id

    @pytest.mark.asyncio
    async def test_explicit_tx_id_skips_injector(self) -> None:
        transport = FakeTransport()
        transport.enable_echo()
        async with _running_router(transport) as router:
            await router.request(b"already-tagged:body", tx_id="already-tagged", timeout=1.0)
        assert transport.sent[0] == b"already-tagged:body"

    def test_injector_overwrites_does_not_duplicate(self) -> None:
        once = _inject(b"hello", "a")
        twice = _inject(once, "b")
        assert once == b"a:hello"
        assert twice == b"b:hello"
        assert _extract(twice) == "b"

    @pytest.mark.asyncio
    async def test_duplicate_inflight_tx_id_raises_immediately(self) -> None:
        transport = FakeTransport()
        async with _running_router(transport) as router:
            first = asyncio.ensure_future(router.request(b"one", tx_id="dup", timeout=5.0))
            await asyncio.sleep(0.01)
            with pytest.raises(RuntimeError, match="dup"):
                await router.request(b"two", tx_id="dup", timeout=5.0)
            first.cancel()
            with pytest.raises(asyncio.CancelledError):
                await first


class TestUnsolicitedStream:
    @pytest.mark.asyncio
    async def test_unsolicited_frame_reaches_stream(self) -> None:
        transport = FakeTransport()
        async with _running_router(transport) as router:
            transport.push_inbound(b"no-colon-here")
            stream = router.unsolicited()
            frame = await asyncio.wait_for(stream.__anext__(), timeout=1.0)
        assert frame == b"no-colon-here"

    @pytest.mark.asyncio
    async def test_late_reply_after_timeout_becomes_unsolicited(self) -> None:
        transport = FakeTransport()
        async with _running_router(transport) as router:
            with pytest.raises(TimeoutError):
                await router.request(b"slow", tx_id="late", timeout=0.05)

            # The "late" reply arrives after the request already timed out.
            transport.push_inbound(b"late:reply")
            stream = router.unsolicited()
            frame = await asyncio.wait_for(stream.__anext__(), timeout=1.0)
        assert frame == b"late:reply"

    @pytest.mark.asyncio
    async def test_overflow_drops_oldest_without_stalling_correlated_replies(self) -> None:
        transport = FakeTransport()
        async with _running_router(transport, unsolicited_maxsize=2) as router:
            transport.push_inbound(b"unsolicited-1")
            transport.push_inbound(b"unsolicited-2")
            transport.push_inbound(b"unsolicited-3")
            await asyncio.sleep(0.05)

            # A correlated request made right after must still resolve — the
            # reader loop never blocked on the full unsolicited queue.
            transport.enable_echo()
            reply = await router.request(b"still-works", timeout=1.0)
            assert reply.endswith(b"still-works")

            stream = router.unsolicited()
            first = await asyncio.wait_for(stream.__anext__(), timeout=1.0)
            second = await asyncio.wait_for(stream.__anext__(), timeout=1.0)
        assert {first, second} == {b"unsolicited-2", b"unsolicited-3"}


class TestReaderLoopResilience:
    @pytest.mark.asyncio
    async def test_receive_timeout_idle_tick_does_not_kill_reader(self) -> None:
        transport = FakeTransport()
        async with _running_router(transport, poll_timeout=0.01) as router:
            await asyncio.sleep(0.05)  # several idle ticks with nothing inbound
            assert router.is_running
            transport.enable_echo()
            reply = await router.request(b"still-alive", timeout=1.0)
        assert reply.endswith(b"still-alive")

    @pytest.mark.asyncio
    async def test_empty_read_tears_down_and_fails_pending_futures(self) -> None:
        transport = FakeTransport()
        await transport.connect()
        router = _make_router(transport)
        router.start()
        pending = asyncio.ensure_future(router.request(b"in-flight", timeout=5.0))
        await asyncio.sleep(0.02)

        transport.push_eof()

        with pytest.raises(ConnectionClosedError):
            await pending

        stream = router.unsolicited()
        with pytest.raises(StopAsyncIteration):
            await asyncio.wait_for(stream.__anext__(), timeout=1.0)

        await router.stop()

    @pytest.mark.asyncio
    async def test_transport_error_tears_down_and_fails_pending_futures(self) -> None:
        transport = FakeTransport()
        await transport.connect()
        router = _make_router(transport)
        router.start()
        pending = asyncio.ensure_future(router.request(b"in-flight", timeout=5.0))
        await asyncio.sleep(0.02)

        transport.push_error(ConnectionError("simulated transport failure"))

        with pytest.raises(ConnectionClosedError):
            await pending

        await router.stop()


class _RaisingCodec:
    """``feed`` raises to simulate a malformed inbound frame — codec-feeding
    failures must not escape the reader task uncontained."""

    def encode(self, payload: bytes) -> bytes:
        return payload

    def feed(self, data: bytes) -> list[bytes]:
        if data == b"boom":
            raise ValueError("malformed frame")
        return [data] if data else []


def _raising_extract(frame: bytes) -> str | None:
    raise ValueError("simulated tx_id extraction failure")


class TestReaderLoopFailureContainment:
    """Fix candidate 03: codec-feeding or tx_id-extraction exceptions must be
    routed through the router's existing teardown path, not escape the reader
    task uncontained (which orphans pending requests and makes ``stop()``
    re-raise)."""

    @pytest.mark.asyncio
    async def test_codec_feed_exception_fails_pending_and_closes_unsolicited(self) -> None:
        transport = FakeTransport()
        await transport.connect()
        router = TransactionRouter(
            transport,
            _RaisingCodec(),
            tx_id_injector=_inject,
            tx_id_extractor=_extract,
            poll_timeout=0.02,
        )
        router.start()
        pending = asyncio.ensure_future(router.request(b"in-flight", timeout=1.0))
        await asyncio.sleep(0.02)

        transport.push_inbound(b"boom")

        with pytest.raises(ConnectionClosedError):
            await pending

        stream = router.unsolicited()
        with pytest.raises(StopAsyncIteration):
            await asyncio.wait_for(stream.__anext__(), timeout=1.0)

        await router.stop()  # must not re-raise the frame-processing exception

    @pytest.mark.asyncio
    async def test_tx_id_extraction_exception_fails_pending_request(self) -> None:
        transport = FakeTransport()
        await transport.connect()
        router = _make_router(transport, tx_id_extractor=_raising_extract)
        router.start()
        pending = asyncio.ensure_future(router.request(b"in-flight", timeout=1.0))
        await asyncio.sleep(0.02)

        transport.push_inbound(b"any-frame")

        with pytest.raises(ConnectionClosedError):
            await pending

        await router.stop()

    @pytest.mark.asyncio
    async def test_stop_after_frame_processing_exception_is_idempotent(self) -> None:
        transport = FakeTransport()
        await transport.connect()
        router = TransactionRouter(
            transport,
            _RaisingCodec(),
            tx_id_injector=_inject,
            tx_id_extractor=_extract,
            poll_timeout=0.02,
        )
        router.start()
        transport.push_inbound(b"boom")
        await asyncio.sleep(0.05)  # let the reader task hit the fault and tear down

        assert not router.is_running

        await router.stop()
        await router.stop()  # must not raise


class TestTeardownAndLifecycle:
    @pytest.mark.asyncio
    async def test_stop_cancels_pending_futures(self) -> None:
        transport = FakeTransport()
        await transport.connect()
        router = _make_router(transport)
        router.start()
        pending = asyncio.ensure_future(router.request(b"in-flight", timeout=5.0))
        await asyncio.sleep(0.02)

        await router.stop()

        with pytest.raises(ConnectionClosedError):
            await pending

    @pytest.mark.asyncio
    async def test_reader_task_does_not_leak_after_stop(self) -> None:
        transport = FakeTransport()
        await transport.connect()
        router = _make_router(transport)
        router.start()
        await asyncio.sleep(0)
        assert router.is_running

        await router.stop()

        assert not router.is_running

    @pytest.mark.asyncio
    async def test_stop_is_idempotent(self) -> None:
        transport = FakeTransport()
        await transport.connect()
        router = _make_router(transport)
        router.start()
        await router.stop()
        await router.stop()  # must not raise
        assert not router.is_running


class TestSocketByteTransportIntegration:
    @pytest.mark.asyncio
    async def test_request_reply_over_real_transport_and_delimiter_codec(self) -> None:
        async def echo_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
            # Echo each delimiter-terminated frame back as it arrives, without
            # waiting for the client to close the connection (it won't — the
            # router holds the connection open for further requests).
            while True:
                line = await reader.readline()
                if not line:
                    return
                writer.write(line)
                await writer.drain()

        async with running_server(echo_handler) as (host, port):
            transport = SocketByteTransport(host=host, port=port)
            await transport.connect()
            router = TransactionRouter(
                transport,
                DelimiterCodec(),
                tx_id_injector=_inject,
                tx_id_extractor=_extract,
                poll_timeout=0.05,
            )
            router.start()
            try:
                reply = await router.request(b"integration-ping", timeout=2.0)
            finally:
                await router.stop()
                await transport.disconnect()

        assert reply.endswith(b"integration-ping")


class TestRouterRestart:
    """fix-12: the router is re-usable — a finished reader (explicit stop or
    detected loss) can be restarted into a fresh epoch. start() stays idempotent
    while a reader is actually running. Construction validates numeric config and
    uses `is None` for the generator default."""

    @pytest.mark.asyncio
    async def test_start_after_stop_restarts_into_fresh_epoch(self) -> None:
        transport = FakeTransport()
        transport.enable_echo()
        await transport.connect()
        router = _make_router(transport)
        router.start()
        await router.stop()
        assert not router.is_running
        assert router._closed is True

        router.start()  # re-use
        try:
            assert router.is_running
            assert router._closed is False
            reply = await router.request(b"after-restart", timeout=1.0)
            assert reply.endswith(b"after-restart")
        finally:
            await router.stop()
            await transport.disconnect()

    @pytest.mark.asyncio
    async def test_start_while_running_is_noop(self) -> None:
        transport = FakeTransport()
        await transport.connect()
        router = _make_router(transport)
        router.start()
        first_task = router._reader_task
        try:
            router.start()  # idempotent while running — no duplicate task
            assert router._reader_task is first_task
        finally:
            await router.stop()
            await transport.disconnect()

    @pytest.mark.asyncio
    async def test_start_after_detected_loss_restarts(self) -> None:
        transport = FakeTransport()
        await transport.connect()
        router = _make_router(transport)
        router.start()
        transport.push_eof()  # reader detects loss and tears down
        await asyncio.sleep(0.05)
        assert not router.is_running
        assert router._closed is True

        router.start()
        try:
            assert router.is_running
            assert router._closed is False
        finally:
            await router.stop()
            await transport.disconnect()

    @pytest.mark.parametrize(
        ("kwarg", "value"),
        [
            ("read_size", 0),
            ("read_size", -1),
            ("poll_timeout", 0),
            ("poll_timeout", -0.5),
            ("unsolicited_maxsize", 0),
            ("unsolicited_maxsize", -3),
        ],
    )
    def test_non_positive_numeric_config_raises(self, kwarg: str, value: float) -> None:
        with pytest.raises(ValueError, match=kwarg):
            _make_router(FakeTransport(), **{kwarg: value})

    def test_generator_default_used_when_none(self) -> None:
        router = _make_router(FakeTransport(), tx_id_generator=None)
        assert [router._generate(), router._generate()] == ["0", "1"]
