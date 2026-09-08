"""
TransactionRouter — Layer 3 of the socket-transaction stack.

Owns the single background reader task for a connection and correlates
request/response traffic by tx_id. Composes a
``foundation_abc.PeripheralByteTransport`` and a
``foundation_tools.socket_transaction.framing_codecs.FramingCodec`` (dependency
injection — no transport/codec knowledge lives here). See
``.claude/specs/socketTransact.md`` (Layer 3) for the full contract.
"""

import asyncio
from collections.abc import AsyncIterator, Callable
from contextlib import suppress
from itertools import count
from logging import getLogger

from foundation_abc.peripheralByteTransport import PeripheralByteTransport
from foundation_tools.socket_transaction.framing_codecs import FramingCodec

_log = getLogger(__name__)

DEFAULT_READ_SIZE = 4096
DEFAULT_POLL_TIMEOUT = 1.0
DEFAULT_UNSOLICITED_MAXSIZE = 100

TxIdInjector = Callable[[bytes, str], bytes]
TxIdExtractor = Callable[[bytes], str | None]
TxIdGenerator = Callable[[], str]


class ConnectionClosedError(ConnectionError):
    """Raised on every pending request future when the connection is lost.

    Covers both an explicit ``stop()`` and a reader-detected loss (empty read /
    transport-raised ``ConnectionError``, ``RuntimeError``, or ``OSError``).
    """


class TransactionRouter:
    """Correlates request/response frames over one connection via tx_id.

    ``tx_id_injector``/``tx_id_extractor`` are required — a wire format is
    protocol-specific and this stack defines none of its own, so no default
    exists. ``tx_id_generator`` defaults to a monotonically increasing counter
    rendered as ``str``.

    The reader loop, once ``start()``ed, repeatedly calls
    ``transport.receive(read_size, timeout=poll_timeout)``: a ``TimeoutError`` is
    an idle tick (loop continues); an empty read or a transport-raised
    ``ConnectionError``/``RuntimeError``/``OSError`` tears the router down —
    every pending request future fails with :class:`ConnectionClosedError` and
    the unsolicited stream ends.
    """

    def __init__(
        self,
        transport: PeripheralByteTransport,
        codec: FramingCodec,
        *,
        tx_id_injector: TxIdInjector,
        tx_id_extractor: TxIdExtractor,
        tx_id_generator: TxIdGenerator | None = None,
        read_size: int = DEFAULT_READ_SIZE,
        poll_timeout: float = DEFAULT_POLL_TIMEOUT,
        unsolicited_maxsize: int = DEFAULT_UNSOLICITED_MAXSIZE,
    ) -> None:
        self._transport = transport
        self._codec = codec
        self._inject = tx_id_injector
        self._extract = tx_id_extractor
        self._generate = tx_id_generator or self._counting_generator()
        self._read_size = read_size
        self._poll_timeout = poll_timeout
        self._pending: dict[str, asyncio.Future[bytes]] = {}
        self._unsolicited: asyncio.Queue[bytes | None] = asyncio.Queue(maxsize=unsolicited_maxsize)
        self._reader_task: asyncio.Task[None] | None = None
        self._closed = False

    @staticmethod
    def _counting_generator() -> TxIdGenerator:
        counter = count()
        return lambda: str(next(counter))

    @property
    def is_running(self) -> bool:
        """Whether the background reader task is alive."""
        return self._reader_task is not None and not self._reader_task.done()

    def start(self) -> None:
        """Start the single background reader task. Idempotent."""
        if self._reader_task is not None:
            return
        self._reader_task = asyncio.ensure_future(self._reader_loop())

    async def stop(self) -> None:
        """Cancel the reader task and tear down all in-flight state."""
        if self._reader_task is not None:
            self._reader_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._reader_task
            self._reader_task = None
        self._teardown(ConnectionClosedError("router stopped"))

    async def request(
        self, payload: bytes, *, tx_id: str | None = None, timeout: float | None = None
    ) -> bytes:
        """Send ``payload``, awaiting the correlated reply frame.

        ``tx_id=None`` (the common path) generates an id and injects it into
        ``payload`` via ``tx_id_injector``. An explicit ``tx_id`` means ``payload``
        already embeds it; it is sent verbatim and the injector is skipped.

        Raises:
            RuntimeError: If ``tx_id`` (explicit or generated) is already in-flight.
            TimeoutError: If no reply arrives within ``timeout``.
        """
        if tx_id is not None:
            resolved_tx_id = tx_id
            needs_injection = False
        else:
            resolved_tx_id = self._generate()
            needs_injection = True

        # Order preserved from the contract: generate -> register future ->
        # inject -> encode -> send. Frame preparation (inject + encode) and the
        # pending registration are one rollback-safe unit: registration happens
        # before the first awaited send so a fast reply cannot race ahead of
        # correlation, and any failure before the reply-await (a raising
        # injector/codec, a transport send failure, or cancellation) removes the
        # pending entry completely rather than orphaning a future in ``_pending``.
        future = self._register(resolved_tx_id)
        try:
            frame = self._inject(payload, resolved_tx_id) if needs_injection else payload
            await self._transport.send(self._codec.encode(frame))
        except BaseException:
            self._pending.pop(resolved_tx_id, None)
            raise

        try:
            if timeout is not None:
                return await asyncio.wait_for(future, timeout=timeout)
            return await future
        except (TimeoutError, asyncio.TimeoutError):
            self._pending.pop(resolved_tx_id, None)
            raise TimeoutError(
                f"request timed out waiting for reply to tx_id {resolved_tx_id!r}"
            ) from None
        except BaseException:
            # Covers cancellation (asyncio.CancelledError is a BaseException, not an
            # Exception): the pending entry must not outlive the caller that's no
            # longer waiting on it.
            self._pending.pop(resolved_tx_id, None)
            raise

    def unsolicited(self) -> AsyncIterator[bytes]:
        """Async iterator of frames with no matching pending request (server
        pushes, broadcasts). Ends when the router tears down."""
        return self._unsolicited_iterator()

    def _register(self, resolved_tx_id: str) -> "asyncio.Future[bytes]":
        if resolved_tx_id in self._pending:
            raise RuntimeError(f"tx_id {resolved_tx_id!r} is already in-flight")
        future: asyncio.Future[bytes] = asyncio.get_running_loop().create_future()
        self._pending[resolved_tx_id] = future
        return future

    async def _unsolicited_iterator(self) -> AsyncIterator[bytes]:
        while True:
            if self._closed and self._unsolicited.empty():
                return
            item = await self._unsolicited.get()
            if item is None:
                return
            yield item

    async def _reader_loop(self) -> None:
        while True:
            try:
                data = await self._transport.receive(self._read_size, timeout=self._poll_timeout)
            except TimeoutError:
                continue  # idle tick — no data yet, not an error
            except (RuntimeError, OSError) as error:
                self._teardown(ConnectionClosedError(f"transport error: {error}"))
                return

            if data == b"":
                self._teardown(ConnectionClosedError("peer closed the connection"))
                return

            try:
                for frame in self._codec.feed(data):
                    self._dispatch(frame)
            except Exception as error:
                # Codec feeding or tx_id extraction failures (both invoked above)
                # must not escape the reader task uncontained — route through the
                # same teardown path as a transport-level connection loss. `Exception`
                # (not `BaseException`) deliberately excludes `asyncio.CancelledError`
                # so task cancellation still propagates instead of being swallowed.
                self._teardown(ConnectionClosedError(f"frame processing error: {error}"))
                return

    def _dispatch(self, frame: bytes) -> None:
        tx_id = self._extract(frame)
        future = self._pending.pop(tx_id, None) if tx_id is not None else None
        if future is not None and not future.done():
            future.set_result(frame)
            return
        self._enqueue_unsolicited(frame)

    def _enqueue_unsolicited(self, frame: bytes) -> None:
        try:
            self._unsolicited.put_nowait(frame)
        except asyncio.QueueFull:
            dropped = self._unsolicited.get_nowait()
            _log.warning(
                "unsolicited queue overflow — dropping oldest frame",
                extra={"dropped_frame_length": len(dropped) if dropped is not None else 0},
            )
            self._unsolicited.put_nowait(frame)

    def _teardown(self, error: Exception) -> None:
        if self._closed:
            return
        self._closed = True
        for pending_tx_id in list(self._pending):
            future = self._pending.pop(pending_tx_id)
            if not future.done():
                future.set_exception(error)
        self._close_unsolicited_stream()

    def _close_unsolicited_stream(self) -> None:
        try:
            self._unsolicited.put_nowait(None)
        except asyncio.QueueFull:
            self._unsolicited.get_nowait()
            self._unsolicited.put_nowait(None)
