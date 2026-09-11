"""
Tests for SocketByteTransport (Action Plan 05): the asyncio TCP client realizing
foundation_abc.PeripheralByteTransport.
"""

import asyncio

import pytest

from foundation_abc.peripheralByteTransport import PeripheralByteTransport
from foundation_tools.socket_transaction import SocketByteTransport
from tests.asyncio_server import running_server


async def _echo_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    data = await reader.read(4096)
    writer.write(data)
    await writer.drain()
    writer.close()


async def _silent_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    # Never writes a reply; blocks reading until the client disconnects (EOF), so
    # the handler task completes naturally instead of leaving a server-side task
    # hanging past the test (a fixed sleep would stall teardown, which awaits
    # in-flight connection handlers).
    await reader.read(-1)


async def _close_immediately_handler(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter
) -> None:
    writer.close()
    await writer.wait_closed()


async def _partial_then_close_handler(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter
) -> None:
    writer.write(b"ab")
    await writer.drain()
    writer.close()
    await writer.wait_closed()


async def _find_unused_port() -> int:
    server = await asyncio.start_server(lambda r, w: None, host="127.0.0.1", port=0)
    port: int = server.sockets[0].getsockname()[1]
    server.close()
    await server.wait_closed()
    return port


class TestSocketByteTransportLifecycle:
    def test_is_abc_instance(self) -> None:
        transport = SocketByteTransport(host="127.0.0.1", port=1)
        assert isinstance(transport, PeripheralByteTransport)

    @pytest.mark.asyncio
    async def test_connect_and_disconnect(self) -> None:
        async with running_server(_silent_handler) as (host, port):
            transport = SocketByteTransport(host=host, port=port)
            await transport.connect()
            assert transport.is_connected
            await transport.disconnect()
            assert not transport.is_connected

    @pytest.mark.asyncio
    async def test_double_disconnect_is_noop(self) -> None:
        async with running_server(_silent_handler) as (host, port):
            transport = SocketByteTransport(host=host, port=port)
            await transport.connect()
            await transport.disconnect()
            await transport.disconnect()
            assert not transport.is_connected

    @pytest.mark.asyncio
    async def test_disconnect_without_connect_is_noop(self) -> None:
        transport = SocketByteTransport(host="127.0.0.1", port=1)
        await transport.disconnect()
        assert not transport.is_connected

    @pytest.mark.asyncio
    async def test_async_context_manager(self) -> None:
        async with running_server(_silent_handler) as (host, port):
            transport = SocketByteTransport(host=host, port=port)
            async with transport as entered:
                assert entered is transport
                assert transport.is_connected
            assert not transport.is_connected

    @pytest.mark.asyncio
    async def test_connect_refused(self) -> None:
        unused_port = await _find_unused_port()
        transport = SocketByteTransport(host="127.0.0.1", port=unused_port)
        with pytest.raises(ConnectionError):
            await transport.connect()

    @pytest.mark.asyncio
    async def test_connect_timeout(self) -> None:
        transport = SocketByteTransport(host="127.0.0.1", port=1, connect_timeout=0.001)

        async def _hang(*_args: object, **_kwargs: object) -> tuple[object, object]:
            await asyncio.sleep(10)
            raise AssertionError("should have timed out")

        import unittest.mock

        with unittest.mock.patch("asyncio.open_connection", side_effect=_hang):
            with pytest.raises(ConnectionError):
                await transport.connect()


class TestSocketByteTransportIO:
    @pytest.mark.asyncio
    async def test_send_receive_round_trip(self) -> None:
        async with running_server(_echo_handler) as (host, port):
            transport = SocketByteTransport(host=host, port=port)
            await transport.connect()
            try:
                await transport.send(b"hello")
                received = await transport.receive(size=1024, timeout=2.0)
                assert received == b"hello"
            finally:
                await transport.disconnect()

    @pytest.mark.asyncio
    async def test_receive_timeout_raises(self) -> None:
        async with running_server(_silent_handler) as (host, port):
            transport = SocketByteTransport(host=host, port=port)
            await transport.connect()
            try:
                with pytest.raises(TimeoutError):
                    await transport.receive(size=1024, timeout=0.05)
            finally:
                await transport.disconnect()

    @pytest.mark.asyncio
    async def test_receive_timeout_zero_non_blocking(self) -> None:
        async with running_server(_silent_handler) as (host, port):
            transport = SocketByteTransport(host=host, port=port)
            await transport.connect()
            try:
                with pytest.raises(TimeoutError):
                    await transport.receive(size=1024, timeout=0)
            finally:
                await transport.disconnect()

    @pytest.mark.asyncio
    async def test_receive_timeout_zero_returns_buffered_data(self) -> None:
        async with running_server(_echo_handler) as (host, port):
            transport = SocketByteTransport(host=host, port=port)
            await transport.connect()
            try:
                await transport.send(b"hello")
                # Give the event loop a chance to deliver the echoed bytes into
                # the StreamReader's internal buffer before requesting a
                # non-blocking read, so the fast path has data to return.
                await asyncio.sleep(0.05)
                received = await transport.receive(size=1024, timeout=0)
                assert received == b"hello"
            finally:
                await transport.disconnect()

    @pytest.mark.asyncio
    async def test_receive_timeout_zero_at_eof_returns_empty_bytes(self) -> None:
        async with running_server(_close_immediately_handler) as (host, port):
            transport = SocketByteTransport(host=host, port=port)
            await transport.connect()
            try:
                await asyncio.sleep(0.05)
                received = await transport.receive(size=1024, timeout=0)
                assert received == b""
            finally:
                await transport.disconnect()

    @pytest.mark.asyncio
    async def test_send_while_disconnected_raises(self) -> None:
        transport = SocketByteTransport(host="127.0.0.1", port=1)
        with pytest.raises(RuntimeError):
            await transport.send(b"data")

    @pytest.mark.asyncio
    async def test_receive_while_disconnected_raises(self) -> None:
        transport = SocketByteTransport(host="127.0.0.1", port=1)
        with pytest.raises(RuntimeError):
            await transport.receive(size=1024)

    @pytest.mark.asyncio
    async def test_peer_closed_no_data_returns_empty_bytes(self) -> None:
        async with running_server(_close_immediately_handler) as (host, port):
            transport = SocketByteTransport(host=host, port=port)
            await transport.connect()
            try:
                received = await transport.receive(size=1024, timeout=2.0)
                assert received == b""
            finally:
                await transport.disconnect()

    @pytest.mark.asyncio
    async def test_short_read_at_eof(self) -> None:
        async with running_server(_partial_then_close_handler) as (host, port):
            transport = SocketByteTransport(host=host, port=port)
            await transport.connect()
            try:
                received = await transport.receive(size=1024, timeout=2.0)
                assert received == b"ab"
            finally:
                await transport.disconnect()


class TestSocketByteTransportLifecycleOwnership:
    """fix-12: re-usable IDLE<->ACTIVE lifecycle, no silent replacement of a
    live socket, and construction-time numeric validation."""

    @pytest.mark.asyncio
    async def test_connect_while_connected_raises(self) -> None:
        async with running_server(_silent_handler) as (host, port):
            transport = SocketByteTransport(host=host, port=port)
            await transport.connect()
            try:
                with pytest.raises(RuntimeError, match="already connected"):
                    await transport.connect()
            finally:
                await transport.disconnect()

    @pytest.mark.asyncio
    async def test_connect_after_disconnect_succeeds(self) -> None:
        async with running_server(_silent_handler) as (host, port):
            transport = SocketByteTransport(host=host, port=port)
            await transport.connect()
            await transport.disconnect()
            assert not transport.is_connected
            await transport.connect()  # re-usable: fresh handle
            try:
                assert transport.is_connected
            finally:
                await transport.disconnect()

    @pytest.mark.parametrize("bad", [0, -1.0])
    def test_non_positive_connect_timeout_raises(self, bad: float) -> None:
        with pytest.raises(ValueError, match="connect_timeout"):
            SocketByteTransport(host="127.0.0.1", port=1, connect_timeout=bad)
