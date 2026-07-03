"""Canonical abstract interface for asynchronous byte-level peripheral transport.

Scope
-----
This module defines the interface contract for all byte-level peripheral
transports consumed by device handlers. A transport moves raw bytes between a
device handler and a physical communication mechanism; it knows nothing about
the protocol framing that rides on top of those bytes.

Existing implementation
-----------------------
Serial communication is implemented elsewhere on top of an asyncio serial
backend, exposing an RS485/USB byte stream through this interface.

Planned implementation
----------------------
An EtherCAT implementation is expected to expose PDO process-image
communication through an adapter that satisfies this interface, translating
between PDO process-image offsets and the byte-stream contract defined here.

Promotion
---------
This interface is intended to become the canonical transport ABC within the
shared automation foundation package once it has stabilized.

Design constraints
------------------
Fully asynchronous
    Every I/O operation is asynchronous. Implementations must never block the
    asyncio event loop.

Byte-stream abstraction
    The interface intentionally exposes only raw bytes. Transport
    implementations know nothing about protocol framing. Framing concerns such
    as STX/ETX delimiters, checksums, BCC, and request/response protocols
    belong to higher layers (the device handlers).

Transport independence
    Device handlers operate identically regardless of whether the underlying
    implementation is serial, EtherCAT, or another transport.

EtherCAT adapter model
    EtherCAT transports are expected to translate between PDO process-image
    offsets and this byte-stream interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class PeripheralByteTransport(ABC):
    """Abstract base for byte-level peripheral communication.

    Implementations of this interface:

    * are safe for use with asyncio,
    * never perform blocking I/O, and
    * provide a transport consumed by device handlers.

    The transport moves raw bytes only; protocol framing (STX/ETX, checksums,
    BCC, request/response protocols) is owned by the device handler layered on
    top of it. Device handlers depend solely on this abstract interface, which
    keeps them portable across serial, TCP socket, USB, EtherCAT adapter,
    simulated, and mock transports.

    Example
    -------
    Dependency-inject a transport into a device handler and exchange bytes
    using the asynchronous methods::

        class DeviceHandler:
            def __init__(self, transport: PeripheralByteTransport) -> None:
                self._transport = transport

            async def ping(self) -> bytes:
                await self._transport.connect()
                try:
                    await self._transport.send(b"\\x02PING\\x03")
                    return await self._transport.receive(size=8, timeout=1.0)
                finally:
                    await self._transport.disconnect()

        # transport is any concrete implementation of the ABC
        handler = DeviceHandler(transport)
        reply = await handler.ping()
    """

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------
    @abstractmethod
    async def connect(self) -> None:
        """Open the underlying communication channel.

        Raises:
            ConnectionError: If the channel cannot be opened.
        """
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the communication channel cleanly."""
        ...

    # ------------------------------------------------------------------
    # I/O
    # ------------------------------------------------------------------
    @abstractmethod
    async def send(self, data: bytes) -> None:
        """Transmit raw bytes.

        Args:
            data: The raw bytes to send.

        Raises:
            RuntimeError: If the transport is not connected.
            OSError: On hardware transmission failure.
        """
        ...

    @abstractmethod
    async def receive(self, size: int, timeout: float = 1.0) -> bytes:
        """Receive up to ``size`` bytes.

        A ``timeout`` of zero is non-blocking. Fewer than ``size`` bytes may be
        returned if end-of-stream occurs before the request is satisfied.

        Args:
            size: Maximum number of bytes to receive.
            timeout: Maximum time to wait, in seconds. Zero is non-blocking.

        Returns:
            The bytes received, possibly fewer than ``size``.

        Raises:
            RuntimeError: If the transport is disconnected.
            TimeoutError: If the timeout expires before any data arrives.
        """
        ...

    # ------------------------------------------------------------------
    # Connection state
    # ------------------------------------------------------------------
    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Whether the transport is open and ready for I/O."""
        ...

    # ------------------------------------------------------------------
    # Async context manager
    # ------------------------------------------------------------------
    async def __aenter__(self) -> PeripheralByteTransport:
        """Open the transport on entry and return ``self``.

        Subclasses may override this if they need custom entry behavior.
        """
        await self.connect()
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        """Close the transport on exit.

        Subclasses may override this if they need custom exit behavior.
        """
        await self.disconnect()
