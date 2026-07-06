"""
Tests for SocketTransact (Action Plan 10): the public Layer-4 facade.

Uses an in-memory fake transport (mirroring chunk 09's fixture) for unit
coverage of containment/timeout/connection-loss behavior, plus one integration
test over the real SocketByteTransport + DelimiterCodec against a local
asyncio server that replies out of order (mirroring the chunk-05/09 fixtures).
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from foundation_abc.peripheralByteTransport import PeripheralByteTransport
from foundation_tools.socket_transaction import (
    DelimiterCodec,
    SocketByteTransport,
    SocketTransact,
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


def _json_inject(payload: bytes, tx_id: str) -> bytes:
    """Stamp tx_id as an extra JSON field — generated models ignore unknown keys
    (see GeoCoordinate.from_dict), so the reply frame stays directly parseable
    by Model.from_wire without stripping."""
    body = json.loads(payload.decode("utf-8"))
    body["tx_id"] = tx_id
    return json.dumps(body).encode("utf-8")


def _json_extract(frame: bytes) -> str | None:
    try:
        body = json.loads(frame.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    tx_id = body.get("tx_id")
    return str(tx_id) if tx_id is not None else None


class _IdentityCodec:
    """No-op codec: each `receive` chunk from the fake transport is one frame."""

    def encode(self, payload: bytes) -> bytes:
        return payload

    def feed(self, data: bytes) -> list[bytes]:
        return [data] if data else []


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


def _make_socket_transact(transport: FakeTransport, **overrides: object) -> SocketTransact:
    defaults: dict[str, object] = {
        "tx_id_injector": _inject,
        "tx_id_extractor": _extract,
        "codec": _IdentityCodec(),
        "transport": transport,
        "poll_timeout": 0.02,
    }
    defaults.update(overrides)
    return SocketTransact("unused-host", 0, **defaults)  # type: ignore[arg-type]


class TestRequestSuccess:
    @pytest.mark.asyncio
    async def test_request_returns_successful_result(self) -> None:
        transport = FakeTransport()
        transport.enable_echo()
        async with _make_socket_transact(transport) as st:
            result = await st.request(b"ping", timeout=1.0)

        assert result.success is True
        assert result.error is None
        assert result.payload is not None
        assert result.payload.endswith(b"ping")


class TestRequestTimeout:
    @pytest.mark.asyncio
    async def test_timeout_yields_failed_result_not_exception(self) -> None:
        transport = FakeTransport()
        async with _make_socket_transact(transport) as st:
            result = await st.request(b"slow", timeout=0.05)

        assert result.success is False
        assert result.payload is None
        assert result.error is not None


class TestConnectionDropMidRequest:
    @pytest.mark.asyncio
    async def test_peer_close_mid_request_yields_failed_result(self) -> None:
        transport = FakeTransport()
        await transport.connect()
        st = _make_socket_transact(transport)
        st._router.start()  # noqa: SLF001 - exercising mid-request drop without connect()

        pending = asyncio.ensure_future(st.request(b"in-flight", timeout=5.0))
        await asyncio.sleep(0.02)
        transport.push_eof()

        result = await pending
        assert result.success is False
        assert result.payload is None
        assert result.error is not None

        await st.disconnect()


class TestDuplicateTxIdContained:
    @pytest.mark.asyncio
    async def test_reusing_inflight_tx_id_returns_failed_result(self) -> None:
        transport = FakeTransport()
        async with _make_socket_transact(transport) as st:
            first = asyncio.ensure_future(st.request(b"one", tx_id="dup", timeout=5.0))
            await asyncio.sleep(0.01)

            second_result = await st.request(b"two", tx_id="dup", timeout=5.0)
            assert second_result.success is False
            assert second_result.error is not None

            first.cancel()
            with pytest.raises(asyncio.CancelledError):
                await first


class TestModelRoundTrip:
    @pytest.mark.asyncio
    async def test_request_with_model_round_trips_a_generated_model(
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

        transport = FakeTransport()
        transport.enable_echo()
        model = GeoCoordinate(latitude=37.7749, longitude=-122.4194)

        async with _make_socket_transact(
            transport, tx_id_injector=_json_inject, tx_id_extractor=_json_extract
        ) as st:
            result = await st.request_with_model(model, GeoCoordinate, timeout=1.0)

        assert result.success is True
        assert result.error is None
        assert result.model == model

    @pytest.mark.asyncio
    async def test_parser_failure_is_advisory_and_does_not_flip_success(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            GeoCoordinate,
            "wire_decode",
            lambda cls, wire_str: (_ for _ in ()).throw(ValueError("bad wire format")),
        )

        transport = FakeTransport()
        transport.enable_echo()

        async with _make_socket_transact(transport) as st:
            result = await st.request_with_model(b"not-a-model", GeoCoordinate, timeout=1.0)

        assert result.success is True
        assert result.model is None
        assert result.error is not None
        assert "Model parsing failed" in result.error

    @pytest.mark.asyncio
    async def test_outbound_to_wire_raising_yields_contained_failure(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A model whose ``to_wire`` raises must yield a contained
        ``success=False`` result from ``request_with_model``, never an
        exception escaping to the caller."""
        monkeypatch.setattr(
            GeoCoordinate,
            "wire_encode",
            lambda instance, **_kwargs: (_ for _ in ()).throw(ValueError("outbound boom")),
        )

        transport = FakeTransport()
        transport.enable_echo()
        model = GeoCoordinate(latitude=1.0, longitude=2.0)

        async with _make_socket_transact(transport) as st:
            result = await st.request_with_model(model, GeoCoordinate, timeout=1.0)

        assert result.success is False
        assert result.model is None
        assert result.error is not None
        assert "outbound boom" in result.error


class TestSendSuccess:
    @pytest.mark.asyncio
    async def test_send_encodes_and_writes_uncorrelated_frame(self) -> None:
        """A successful uncorrelated ``send()`` must run the payload through
        the codec and write the encoded bytes to the transport — only the
        raise-on-failure path was covered before."""
        transport = FakeTransport()
        codec = DelimiterCodec()

        async with _make_socket_transact(transport, codec=codec) as st:
            await st.send(b"broadcast-payload")

        assert transport.sent == [codec.encode(b"broadcast-payload")]


class TestRequestWithModelEmptyPayloadSkipsParser:
    @pytest.mark.asyncio
    async def test_empty_correlated_reply_skips_parser_and_succeeds(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A ``b""`` correlated reply must skip model parsing entirely — the
        parser is never invoked — while still yielding ``success=True`` with
        ``model=None``."""
        parser_mock = MagicMock()
        monkeypatch.setattr(GeoCoordinate, "wire_decode", parser_mock)

        transport = FakeTransport()
        async with _make_socket_transact(transport) as st:
            with patch.object(st._router, "request", new=AsyncMock(return_value=b"")):  # noqa: SLF001
                result = await st.request_with_model(b"query", GeoCoordinate, timeout=1.0)

        assert result.success is True
        assert result.model is None
        assert result.error is None
        parser_mock.assert_not_called()


class TestUnsolicitedIteration:
    @pytest.mark.asyncio
    async def test_unsolicited_frame_reaches_the_iterator(self) -> None:
        transport = FakeTransport()
        async with _make_socket_transact(transport) as st:
            transport.push_inbound(b"no-colon-here")
            frame = await asyncio.wait_for(st.unsolicited().__anext__(), timeout=1.0)

        assert frame == b"no-colon-here"


class TestContextManagerLifecycle:
    @pytest.mark.asyncio
    async def test_aenter_connects_and_aexit_tears_down(self) -> None:
        transport = FakeTransport()
        transport.enable_echo()
        assert not transport.is_connected

        async with _make_socket_transact(transport) as st:
            assert transport.is_connected
            assert st._router.is_running  # noqa: SLF001 - verifying lifecycle wiring
            result = await st.request(b"hello", timeout=1.0)
            assert result.success is True

        assert not transport.is_connected
        assert not st._router.is_running  # noqa: SLF001 - verifying lifecycle wiring


class TestSocketByteTransportIntegration:
    @pytest.mark.asyncio
    async def test_concurrent_requests_against_out_of_order_server(self) -> None:
        received: list[bytes] = []
        release = asyncio.Event()

        async def handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
            # Collect every request frame, then reply in reverse order once all
            # have arrived — a deliberately out-of-order-replying endpoint.
            while len(received) < 3:
                line = await reader.readline()
                if not line:
                    return
                received.append(line)
            await release.wait()
            for line in reversed(received):
                writer.write(line)
                await writer.drain()

        server = await asyncio.start_server(handler, host="127.0.0.1", port=0)
        host, port = server.sockets[0].getsockname()[:2]

        async with server:
            async with SocketTransact(
                host,
                port,
                tx_id_injector=_inject,
                tx_id_extractor=_extract,
                codec=DelimiterCodec(),
                poll_timeout=0.05,
            ) as st:
                tasks = [
                    asyncio.ensure_future(st.request(f"payload-{i}".encode(), timeout=2.0))
                    for i in range(3)
                ]
                await asyncio.sleep(0.1)
                release.set()
                results = await asyncio.gather(*tasks)

        for i, result in enumerate(results):
            assert result.success is True
            assert result.payload is not None
            assert result.payload.endswith(f"payload-{i}".encode())

    @pytest.mark.asyncio
    async def test_send_raises_on_transport_failure(self) -> None:
        transport = SocketByteTransport(host="127.0.0.1", port=1)
        st = SocketTransact(
            "127.0.0.1",
            1,
            tx_id_injector=_inject,
            tx_id_extractor=_extract,
            transport=transport,
        )
        with pytest.raises(RuntimeError):
            await st.send(b"never-sent")
