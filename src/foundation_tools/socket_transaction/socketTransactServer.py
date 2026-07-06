"""
SocketTransactServer — Layer 4b (server role) of the socket-transaction stack.

The server-side counterpart of ``SocketTransact``: accepts connections, services
plural inbound requests simultaneously, and replies tagged with each request's
tx_id via the same injector/extractor correlation pair the client router uses
(mirrored in direction — extract from requests, inject into replies). See
``.claude/specs/socketTransact.md`` (Layer 4b) for the full contract.
"""

import asyncio
from collections.abc import Awaitable, Callable
from contextlib import suppress
from logging import getLogger
from typing import Protocol

from foundation_tools.socket_transaction.framing_codecs import DelimiterCodec, FramingCodec
from foundation_tools.socket_transaction.transaction_router import TxIdExtractor, TxIdInjector

_log = getLogger(__name__)

DEFAULT_READ_SIZE = 4096

Handler = Callable[[bytes], Awaitable[bytes | None]]
ErrorReplyFactory = Callable[[bytes, Exception], bytes | None]
CodecFactory = Callable[[], FramingCodec]


async def _wait_closed_quietly(writer: "_StreamWriterLike") -> None:
    """Await ``writer.wait_closed()``, swallowing any exception — used in a
    teardown ``gather(..., return_exceptions=True)`` where a per-connection
    failure must never block the rest of teardown."""
    with suppress(Exception):
        await writer.wait_closed()


class _StreamWriterLike(Protocol):
    """Structural subset of ``asyncio.StreamWriter`` this module depends on —
    lets tests substitute a fake writer without a real socket."""

    def write(self, data: bytes) -> None: ...
    async def drain(self) -> None: ...
    def close(self) -> None: ...
    async def wait_closed(self) -> None: ...
    def is_closing(self) -> bool: ...


class _StreamReaderLike(Protocol):
    """Structural subset of ``asyncio.StreamReader`` this module depends on."""

    async def read(self, n: int) -> bytes: ...


class SocketTransactServer:
    """Server-side counterpart of ``SocketTransact``.

    Wraps ``asyncio.start_server``. One handler services every accepted
    connection; each complete inbound frame dispatches as its own task (a slow
    handler never blocks other requests), optionally bounded by
    ``max_concurrent``. Lifecycle operations (``start``/``stop``) raise —
    infrastructure semantics, mirroring the client facade's ``send``/connect
    path.

    Example:
        async with SocketTransactServer(
            host, port,
            handler=my_handler,
            tx_id_injector=my_injector,
            tx_id_extractor=my_extractor,
        ) as server:
            await server.serve_forever()
    """

    def __init__(
        self,
        host: str,
        port: int,
        handler: Handler,
        *,
        tx_id_injector: TxIdInjector,
        tx_id_extractor: TxIdExtractor,
        codec_factory: CodecFactory = DelimiterCodec,
        max_concurrent: int | None = None,
        error_reply_factory: ErrorReplyFactory | None = None,
        read_size: int = DEFAULT_READ_SIZE,
    ) -> None:
        self._host = host
        self._port = port
        self._handler = handler
        self._inject = tx_id_injector
        self._extract = tx_id_extractor
        self._codec_factory = codec_factory
        self._semaphore = asyncio.Semaphore(max_concurrent) if max_concurrent else None
        self._error_reply_factory = error_reply_factory
        self._read_size = read_size
        self._server: asyncio.base_events.Server | None = None
        self._connections: dict[_StreamWriterLike, FramingCodec] = {}
        self._request_tasks: set[asyncio.Task[None]] = set()
        self._reader_tasks: set[asyncio.Task[None]] = set()

    # -----------------------------------------------------------------------
    # MARK: - Lifecycle
    # -----------------------------------------------------------------------

    async def start(self) -> None:
        """Start accepting connections. ``asyncio.start_server`` serves
        immediately on return — no separate call is required to begin
        accepting; ``serve_forever`` is only a convenience blocking call."""
        self._server = await asyncio.start_server(
            self._on_connect, host=self._host, port=self._port
        )

    async def stop(self) -> None:
        """Stop accepting new connections, cancel in-flight handler tasks,
        cancel per-connection reader loops, and close all connections."""
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

        for task in list(self._request_tasks):
            task.cancel()
        if self._request_tasks:
            await asyncio.gather(*self._request_tasks, return_exceptions=True)

        # Cancel the per-connection reader loops (`_on_connect` tasks) after
        # handler-dispatch tasks so a still-connected client's reader loop
        # doesn't outlive teardown. `return_exceptions=True` bounds this even
        # if a reader task is already finishing on its own.
        for task in list(self._reader_tasks):
            task.cancel()

        awaitables: list[asyncio.Task[None]] = list(self._reader_tasks)
        for writer in list(self._connections):
            self._close_writer(writer)
            awaitables.append(asyncio.ensure_future(_wait_closed_quietly(writer)))
        if awaitables:
            await asyncio.gather(*awaitables, return_exceptions=True)

        self._connections.clear()
        self._reader_tasks.clear()

    async def serve_forever(self) -> None:
        """Block until ``stop()`` closes the server (or the task is
        cancelled). Purely a convenience for scripts — connections are already
        being accepted once ``start()``/``__aenter__`` returns."""
        if self._server is None:
            raise RuntimeError("start the server (or use `async with`) before serve_forever")
        await self._server.serve_forever()

    async def __aenter__(self) -> "SocketTransactServer":
        await self.start()
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        await self.stop()

    @property
    def address(self) -> tuple[str, int]:
        """The bound ``(host, port)`` — useful when constructed with
        ``port=0`` to discover the ephemeral port actually bound."""
        if self._server is None or not self._server.sockets:
            raise RuntimeError("server is not started")
        host, port = self._server.sockets[0].getsockname()[:2]
        return (host, port)

    # -----------------------------------------------------------------------
    # MARK: - Public — server push
    # -----------------------------------------------------------------------

    async def broadcast(self, payload: bytes) -> None:
        """Send an uncorrelated frame to every connected client (arrives on
        each client's unsolicited stream). Best-effort per connection — a
        failure on one connection does not stop the fan-out to the rest."""
        for writer, codec in list(self._connections.items()):
            try:
                writer.write(codec.encode(payload))
                await writer.drain()
            except (ConnectionError, RuntimeError, OSError) as error:
                _log.warning(
                    "broadcast failed on one connection — continuing",
                    extra={"error": str(error)},
                )

    # -----------------------------------------------------------------------
    # MARK: - Private — connection handling
    # -----------------------------------------------------------------------

    async def _on_connect(
        self, reader: "_StreamReaderLike", writer: "_StreamWriterLike"
    ) -> None:
        # Track this connection's reader-loop task so `stop()` can cancel and
        # await it — without this, the loop below outlives teardown for any
        # client that hasn't sent EOF (Server Compliance Requirement 7).
        reader_task = asyncio.current_task()
        if reader_task is not None:
            self._reader_tasks.add(reader_task)

        codec = self._codec_factory()
        self._connections[writer] = codec
        connection_tasks: set[asyncio.Task[None]] = set()
        try:
            while True:
                try:
                    data = await reader.read(self._read_size)
                except (ConnectionError, OSError):
                    break
                if data == b"":
                    break
                for frame in codec.feed(data):
                    self._spawn_dispatch(frame, codec, writer, connection_tasks)
        finally:
            self._connections.pop(writer, None)
            if reader_task is not None:
                self._reader_tasks.discard(reader_task)
            for task in list(connection_tasks):
                task.cancel()
            if connection_tasks:
                await asyncio.gather(*connection_tasks, return_exceptions=True)
            self._close_writer(writer)
            with suppress(Exception):
                await writer.wait_closed()

    def _spawn_dispatch(
        self,
        frame: bytes,
        codec: FramingCodec,
        writer: "_StreamWriterLike",
        connection_tasks: set["asyncio.Task[None]"],
    ) -> None:
        task = asyncio.ensure_future(self._dispatch(frame, codec, writer))
        connection_tasks.add(task)
        self._request_tasks.add(task)

        def _on_done(finished: "asyncio.Task[None]") -> None:
            connection_tasks.discard(finished)
            self._request_tasks.discard(finished)

        task.add_done_callback(_on_done)

    async def _dispatch(
        self, request_frame: bytes, codec: FramingCodec, writer: "_StreamWriterLike"
    ) -> None:
        if self._semaphore is not None:
            async with self._semaphore:
                await self._dispatch_unbounded(request_frame, codec, writer)
        else:
            await self._dispatch_unbounded(request_frame, codec, writer)

    async def _dispatch_unbounded(
        self, request_frame: bytes, codec: FramingCodec, writer: "_StreamWriterLike"
    ) -> None:
        reply_payload = await self._invoke_handler(request_frame)
        if reply_payload is None:
            return

        tx_id = self._extract(request_frame)
        if tx_id is not None:
            reply_payload = self._inject(reply_payload, tx_id)

        try:
            writer.write(codec.encode(reply_payload))
            await writer.drain()
        except (ConnectionError, RuntimeError, OSError) as error:
            _log.warning(
                "failed to send reply — connection likely closed",
                extra={"error": str(error)},
            )

    async def _invoke_handler(self, request_frame: bytes) -> bytes | None:
        try:
            return await self._handler(request_frame)
        except Exception as error:  # pylint: disable=broad-exception-caught
            return self._build_error_reply(request_frame, error)

    def _build_error_reply(self, request_frame: bytes, error: Exception) -> bytes | None:
        if self._error_reply_factory is None:
            _log.error("handler raised — dropping reply", exc_info=error)
            return None
        try:
            return self._error_reply_factory(request_frame, error)
        except Exception:  # pylint: disable=broad-exception-caught
            _log.error("error_reply_factory itself raised — dropping reply", exc_info=True)
            return None

    def _close_writer(self, writer: "_StreamWriterLike") -> None:
        if writer.is_closing():
            return
        writer.close()
