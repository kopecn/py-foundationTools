"""
SocketByteTransport — asyncio TCP client realizing PeripheralByteTransport.

Layer 1 of the socket-transaction stack. Moves raw bytes only; framing (STX/ETX,
delimiters, length prefixes) is owned by the codecs layered on top (chunk 08). See
``.claude/specs/socketTransact.md`` (Layer 1) for the full contract.
"""

import asyncio
import contextlib

from foundation_abc.peripheralByteTransport import PeripheralByteTransport


class SocketByteTransport(PeripheralByteTransport):
    """Asyncio TCP client transport moving raw bytes over a single connection.

    Host, port, and connect timeout are fixed at construction — no environment
    inspection, no reconnect/keepalive logic (a future policy concern).
    """

    def __init__(self, host: str, port: int, *, connect_timeout: float = 5.0) -> None:
        self._host = host
        self._port = port
        self._connect_timeout = connect_timeout
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

    async def connect(self) -> None:
        """Open the TCP connection.

        Raises:
            ConnectionError: If the connection cannot be established within
                ``connect_timeout``, or the peer refuses/rejects it.
        """
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=self._connect_timeout,
            )
        except (OSError, asyncio.TimeoutError) as error:
            raise ConnectionError(
                f"Failed to connect to {self._host}:{self._port}: {error}"
            ) from error

    async def disconnect(self) -> None:
        """Close the connection cleanly. A no-op if already disconnected."""
        writer = self._writer
        self._writer = None
        self._reader = None
        if writer is None or writer.is_closing():
            return
        writer.close()
        await writer.wait_closed()

    async def send(self, data: bytes) -> None:
        """Write raw bytes and await the drain.

        Raises:
            RuntimeError: If the transport is not connected.
        """
        if self._writer is None:
            raise RuntimeError("Cannot send: transport is not connected")
        self._writer.write(data)
        await self._writer.drain()

    async def receive(self, size: int, timeout: float = 1.0) -> bytes:
        """Receive up to ``size`` bytes.

        A ``timeout`` of zero (or negative) is non-blocking: the read is
        scheduled and given exactly one event-loop tick to consume data already
        buffered on the connection (or an already-pending end-of-stream). If it
        has not completed by then, it is cancelled and ``TimeoutError`` is
        raised — no busy-waiting, no blocking on the event loop.

        Returns ``b""`` immediately when the peer has closed the connection and no
        buffered data remains — the end-of-stream signal upper layers rely on —
        rather than raising ``TimeoutError``. A short read (fewer than ``size``
        bytes) is returned as-is when end-of-stream is reached mid-read.

        Raises:
            RuntimeError: If the transport is not connected.
            TimeoutError: If no data arrives before ``timeout`` elapses.
        """
        if self._reader is None:
            raise RuntimeError("Cannot receive: transport is not connected")
        if timeout <= 0:
            task = asyncio.ensure_future(self._reader.read(size))
            await asyncio.sleep(0)
            if task.done():
                return task.result()
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
            raise TimeoutError("Receive timed out (non-blocking, no data buffered)")
        try:
            return await asyncio.wait_for(self._reader.read(size), timeout=timeout)
        except (asyncio.TimeoutError, TimeoutError) as error:
            raise TimeoutError(f"Receive timed out after {timeout} seconds") from error

    @property
    def is_connected(self) -> bool:
        """Whether the underlying writer is open."""
        return self._writer is not None and not self._writer.is_closing()
