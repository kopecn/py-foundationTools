"""
Tests for SocketTransactServer (Action Plan 13): the server role, plus the
stack's end-to-end proof — our own SocketTransact client talking to our own
SocketTransactServer over real sockets.

Unit-level tests drive ``_on_connect`` directly against fake reader/writer
objects satisfying the structural subset this module depends on (no real
sockets needed, mirroring the fake-transport convention used elsewhere in this
test suite). End-to-end tests use real `asyncio.start_server` sockets via the
public `SocketTransact` / `SocketTransactServer` facades.
"""

import asyncio
import json

import pytest

from foundation_tools.socket_transaction import (
    DelimiterCodec,
    SocketTransact,
    SocketTransactServer,
)
from foundationTypes.commonTypes.GeoCoordinate import GeoCoordinate


def _inject(payload: bytes, tx_id: str) -> bytes:
    """Stamp `tx_id:` onto payload, overwriting any prior stamp (never duplicating)."""
    _before, sep, after = payload.partition(b":")
    body = after if sep else payload
    return f"{tx_id}:".encode() + body


def _extract(frame: bytes) -> str | None:
    prefix, sep, _ = frame.partition(b":")
    if not sep:
        return None
    try:
        return prefix.decode("ascii")
    except UnicodeDecodeError:
        return None


class _IdentityCodec:
    """No-op codec: each `receive` chunk is treated as one frame."""

    def encode(self, payload: bytes) -> bytes:
        return payload

    def feed(self, data: bytes) -> list[bytes]:
        return [data] if data else []


class FakeStreamReader:
    """Minimal async-`read`-only stand-in for `asyncio.StreamReader`."""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[bytes] = asyncio.Queue()

    async def read(self, n: int) -> bytes:
        return await self._queue.get()

    def push(self, data: bytes) -> None:
        self._queue.put_nowait(data)

    def push_eof(self) -> None:
        self._queue.put_nowait(b"")


class FakeStreamWriter:
    """Minimal stand-in for `asyncio.StreamWriter`: records writes, tracks
    closing state, never touches a real socket."""

    def __init__(self) -> None:
        self.written = bytearray()
        self._closing = False

    def write(self, data: bytes) -> None:
        self.written.extend(data)

    async def drain(self) -> None:
        return None

    def close(self) -> None:
        self._closing = True

    async def wait_closed(self) -> None:
        return None

    def is_closing(self) -> bool:
        return self._closing


def _make_server(handler: object, **overrides: object) -> SocketTransactServer:
    defaults: dict[str, object] = {
        "tx_id_injector": _inject,
        "tx_id_extractor": _extract,
        "codec_factory": _IdentityCodec,
    }
    defaults.update(overrides)
    return SocketTransactServer("unused-host", 0, handler, **defaults)  # type: ignore[arg-type]


def _run_connection(
    server: SocketTransactServer, reader: FakeStreamReader, writer: FakeStreamWriter
) -> "asyncio.Task[None]":
    return asyncio.ensure_future(server._on_connect(reader, writer))  # noqa: SLF001


class TestPerConnectionCodecIsolation:
    @pytest.mark.asyncio
    async def test_fragmented_frame_on_one_connection_does_not_affect_the_other(self) -> None:
        received: list[bytes] = []

        async def handler(request: bytes) -> bytes | None:
            received.append(request)
            return None

        server = _make_server(handler, codec_factory=DelimiterCodec)

        reader_a, writer_a = FakeStreamReader(), FakeStreamWriter()
        reader_b, writer_b = FakeStreamReader(), FakeStreamWriter()
        task_a = _run_connection(server, reader_a, writer_a)
        task_b = _run_connection(server, reader_b, writer_b)

        # Connection A sends its frame split byte-by-byte; connection B sends a
        # complete frame in one shot. B's frame must be dispatched without
        # waiting on A's reassembly.
        reader_b.push(b"whole-frame-on-b\n")
        await asyncio.sleep(0.02)
        assert received == [b"whole-frame-on-b"]

        for byte in b"fragmented-on-a\n":
            reader_a.push(bytes([byte]))
        await asyncio.sleep(0.02)
        assert received == [b"whole-frame-on-b", b"fragmented-on-a"]

        reader_a.push_eof()
        reader_b.push_eof()
        await asyncio.gather(task_a, task_b)


class TestHandlerContainment:
    @pytest.mark.asyncio
    async def test_handler_exception_does_not_kill_the_connection_loop(self) -> None:
        call_count = 0

        async def flaky_handler(request: bytes) -> bytes | None:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("boom")
            return request

        server = _make_server(flaky_handler)
        reader, writer = FakeStreamReader(), FakeStreamWriter()
        task = _run_connection(server, reader, writer)

        reader.push(b"1:first")
        await asyncio.sleep(0.02)
        assert bytes(writer.written) == b""  # dropped: no error_reply_factory

        reader.push(b"2:second")
        await asyncio.sleep(0.02)
        assert bytes(writer.written) == b"2:second"

        reader.push_eof()
        await task

    @pytest.mark.asyncio
    async def test_none_return_means_no_reply(self) -> None:
        async def silent_handler(request: bytes) -> bytes | None:
            return None

        server = _make_server(silent_handler)
        reader, writer = FakeStreamReader(), FakeStreamWriter()
        task = _run_connection(server, reader, writer)

        reader.push(b"1:hello")
        await asyncio.sleep(0.02)
        assert bytes(writer.written) == b""

        reader.push_eof()
        await task

    @pytest.mark.asyncio
    async def test_error_reply_factory_converts_handler_exception_to_a_reply(self) -> None:
        async def raising_handler(request: bytes) -> bytes | None:
            raise RuntimeError("handler exploded")

        def error_reply_factory(request: bytes, error: Exception) -> bytes | None:
            # No colon in the body — the test's `_inject`/`_extract` convention
            # treats the first colon as the tx_id separator.
            return f"error-{error}".encode()

        server = _make_server(raising_handler, error_reply_factory=error_reply_factory)
        reader, writer = FakeStreamReader(), FakeStreamWriter()
        task = _run_connection(server, reader, writer)

        reader.push(b"7:trigger")
        await asyncio.sleep(0.02)
        # tx_id "7" injected into the error reply exactly once (overwrite semantics).
        assert bytes(writer.written) == b"7:error-handler exploded"

        reader.push_eof()
        await task

    @pytest.mark.asyncio
    async def test_echo_handler_reply_carries_request_tx_id_exactly_once(self) -> None:
        async def echo_handler(request: bytes) -> bytes | None:
            return request  # already tx_id-prefixed by the "client"

        server = _make_server(echo_handler)
        reader, writer = FakeStreamReader(), FakeStreamWriter()
        task = _run_connection(server, reader, writer)

        reader.push(b"42:payload")
        await asyncio.sleep(0.02)
        assert bytes(writer.written) == b"42:payload"
        assert bytes(writer.written).count(b"42:") == 1

        reader.push_eof()
        await task


class TestMaxConcurrent:
    @pytest.mark.asyncio
    async def test_max_concurrent_bounds_active_handlers(self) -> None:
        active = 0
        peak = 0

        async def slow_handler(request: bytes) -> bytes | None:
            nonlocal active, peak
            active += 1
            peak = max(peak, active)
            await asyncio.sleep(0.05)
            active -= 1
            return None

        server = _make_server(slow_handler, max_concurrent=1)
        reader, writer = FakeStreamReader(), FakeStreamWriter()
        task = _run_connection(server, reader, writer)

        reader.push(b"1:a")
        reader.push(b"2:b")
        reader.push(b"3:c")
        await asyncio.sleep(0.2)

        assert peak == 1

        reader.push_eof()
        await task


class TestTeardown:
    @pytest.mark.asyncio
    async def test_stop_cancels_in_flight_handler_tasks(self) -> None:
        started = asyncio.Event()
        cancelled = False

        async def hanging_handler(request: bytes) -> bytes | None:
            nonlocal cancelled
            started.set()
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                cancelled = True
                raise
            return None

        server = _make_server(hanging_handler)
        reader, writer = FakeStreamReader(), FakeStreamWriter()
        _run_connection(server, reader, writer)

        reader.push(b"1:slow")
        await asyncio.wait_for(started.wait(), timeout=1.0)

        await server.stop()

        assert cancelled is True
        assert writer.is_closing()


class TestReaderTaskLifecycle:
    """Chunk 17: `stop()` must cancel per-connection reader loops (`_on_connect`
    tasks), not just handler-dispatch tasks — otherwise a still-connected client
    leaves its reader loop running forever after teardown."""

    @pytest.mark.asyncio
    async def test_stop_with_live_connection_returns_promptly(self) -> None:
        async def silent_handler(request: bytes) -> bytes | None:
            return None

        server = _make_server(silent_handler)
        reader, writer = FakeStreamReader(), FakeStreamWriter()
        connection_task = _run_connection(server, reader, writer)
        await asyncio.sleep(0.02)  # let _on_connect register the connection

        # No EOF is ever pushed on `reader` — if stop() didn't cancel the
        # reader loop, both stop() and the connection task would hang forever.
        await asyncio.wait_for(server.stop(), timeout=1.0)
        done, pending = await asyncio.wait([connection_task], timeout=1.0)

        assert connection_task in done
        assert not pending
        assert connection_task.cancelled()
        assert writer.is_closing()

    @pytest.mark.asyncio
    async def test_stop_leaves_no_lingering_tasks(self) -> None:
        async def silent_handler(request: bytes) -> bytes | None:
            return None

        server = _make_server(silent_handler)
        reader, writer = FakeStreamReader(), FakeStreamWriter()

        before = asyncio.all_tasks()
        connection_task = _run_connection(server, reader, writer)
        await asyncio.sleep(0.02)

        await asyncio.wait_for(server.stop(), timeout=1.0)
        await asyncio.wait([connection_task], timeout=1.0)

        after = asyncio.all_tasks()
        leaked = after - before
        assert leaked == set()


class TestEndToEnd:
    @pytest.mark.asyncio
    async def test_concurrent_requests_with_random_delay_resolve_out_of_order(self) -> None:
        import random

        async def randomized_delay_echo(request: bytes) -> bytes | None:
            await asyncio.sleep(random.uniform(0, 0.03))
            return request

        async with SocketTransactServer(
            "127.0.0.1",
            0,
            randomized_delay_echo,
            tx_id_injector=_inject,
            tx_id_extractor=_extract,
            codec_factory=DelimiterCodec,
        ) as server:
            host, port = server.address
            async with SocketTransact(
                host,
                port,
                tx_id_injector=_inject,
                tx_id_extractor=_extract,
                codec=DelimiterCodec(),
                poll_timeout=0.02,
            ) as client:
                tasks = [
                    asyncio.ensure_future(client.request(f"payload-{i}".encode(), timeout=2.0))
                    for i in range(10)
                ]
                results = await asyncio.gather(*tasks)

        for i, result in enumerate(results):
            assert result.success is True
            assert result.payload is not None
            assert result.payload.endswith(f"payload-{i}".encode())

    @pytest.mark.asyncio
    async def test_two_concurrent_client_connections_served_simultaneously(self) -> None:
        async def echo_handler(request: bytes) -> bytes | None:
            return request

        async with SocketTransactServer(
            "127.0.0.1",
            0,
            echo_handler,
            tx_id_injector=_inject,
            tx_id_extractor=_extract,
            codec_factory=DelimiterCodec,
        ) as server:
            host, port = server.address
            async with (
                SocketTransact(
                    host,
                    port,
                    tx_id_injector=_inject,
                    tx_id_extractor=_extract,
                    codec=DelimiterCodec(),
                    poll_timeout=0.02,
                ) as client_a,
                SocketTransact(
                    host,
                    port,
                    tx_id_injector=_inject,
                    tx_id_extractor=_extract,
                    codec=DelimiterCodec(),
                    poll_timeout=0.02,
                ) as client_b,
            ):
                result_a, result_b = await asyncio.gather(
                    client_a.request(b"from-a", timeout=2.0),
                    client_b.request(b"from-b", timeout=2.0),
                )

        assert result_a.success is True and result_a.payload is not None
        assert result_a.payload.endswith(b"from-a")
        assert result_b.success is True and result_b.payload is not None
        assert result_b.payload.endswith(b"from-b")

    @pytest.mark.asyncio
    async def test_broadcast_arrives_on_client_unsolicited_stream(self) -> None:
        async def silent_handler(request: bytes) -> bytes | None:
            return None

        async with SocketTransactServer(
            "127.0.0.1",
            0,
            silent_handler,
            tx_id_injector=_inject,
            tx_id_extractor=_extract,
            codec_factory=DelimiterCodec,
        ) as server:
            host, port = server.address
            async with SocketTransact(
                host,
                port,
                tx_id_injector=_inject,
                tx_id_extractor=_extract,
                codec=DelimiterCodec(),
                poll_timeout=0.02,
            ) as client:
                # Give the server a moment to register the accepted connection
                # before broadcasting to it.
                await asyncio.sleep(0.05)
                await server.broadcast(b"server-push")

                frame = await asyncio.wait_for(client.unsolicited().__anext__(), timeout=1.0)

        assert frame == b"server-push"

    @pytest.mark.asyncio
    async def test_model_round_trip_through_both_facades(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            GeoCoordinate,
            "wire_encode",
            lambda instance, **_kwargs: json.dumps(instance.to_dict()),
        )
        monkeypatch.setattr(
            GeoCoordinate,
            "wire_decode",
            lambda cls, wire_str: cls.from_dict(json.loads(wire_str)),
        )

        def json_inject(payload: bytes, tx_id: str) -> bytes:
            body = json.loads(payload.decode("utf-8"))
            body["tx_id"] = tx_id
            return json.dumps(body).encode("utf-8")

        def json_extract(frame: bytes) -> str | None:
            try:
                body = json.loads(frame.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return None
            tx_id = body.get("tx_id")
            return str(tx_id) if tx_id is not None else None

        async def echo_handler(request: bytes) -> bytes | None:
            return request

        model = GeoCoordinate(latitude=48.8566, longitude=2.3522)

        async with SocketTransactServer(
            "127.0.0.1",
            0,
            echo_handler,
            tx_id_injector=json_inject,
            tx_id_extractor=json_extract,
            codec_factory=DelimiterCodec,
        ) as server:
            host, port = server.address
            async with SocketTransact(
                host,
                port,
                tx_id_injector=json_inject,
                tx_id_extractor=json_extract,
                codec=DelimiterCodec(),
                poll_timeout=0.02,
            ) as client:
                result = await client.request_with_model(model, GeoCoordinate, timeout=2.0)

        assert result.success is True
        assert result.error is None
        assert result.model == model


async def _echo(request: bytes) -> bytes | None:
    return request


class TestServerLifecycleOwnership:
    """fix-12: the server enforces a re-usable IDLE<->ACTIVE lifecycle, refuses
    to silently replace a live server, distinguishes `max_concurrent=None` from
    an explicit `0`, and validates numeric config at construction."""

    @pytest.mark.parametrize("bad", [0, -1])
    def test_max_concurrent_below_one_raises(self, bad: int) -> None:
        with pytest.raises(ValueError, match="max_concurrent"):
            _make_server(_echo, max_concurrent=bad)

    def test_max_concurrent_none_is_unbounded(self) -> None:
        server = _make_server(_echo, max_concurrent=None)
        assert server._semaphore is None

    @pytest.mark.parametrize("bad", [0, -5])
    def test_non_positive_read_size_raises(self, bad: int) -> None:
        with pytest.raises(ValueError, match="read_size"):
            _make_server(_echo, read_size=bad)

    @pytest.mark.asyncio
    async def test_start_while_running_raises(self) -> None:
        server = SocketTransactServer(
            "127.0.0.1", 0, _echo, tx_id_injector=_inject, tx_id_extractor=_extract
        )
        await server.start()
        try:
            with pytest.raises(RuntimeError, match="already running"):
                await server.start()
        finally:
            await server.stop()

    @pytest.mark.asyncio
    async def test_restart_after_stop_succeeds(self) -> None:
        server = SocketTransactServer(
            "127.0.0.1", 0, _echo, tx_id_injector=_inject, tx_id_extractor=_extract
        )
        await server.start()
        await server.stop()
        await server.start()  # re-use: configuration retained
        try:
            assert server.address[0] == "127.0.0.1"
        finally:
            await server.stop()
