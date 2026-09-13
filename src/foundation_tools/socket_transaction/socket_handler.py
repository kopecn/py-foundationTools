"""
SocketHandler — common threaded socket transport (plan 25, chunk 07).

Owns an attached ``socket.socket`` by composition and gives it a monotonically
increasing connection epoch on every attach. Provides epoch-safe sending
(serialized ``sendall``, never blocking while holding the state lock), and
idempotent, epoch-conditional teardown that never joins its own receive
thread. See ``.claude/specs/threadedSocketTransport.md#common-handler`` for
the full behavioral contract.

Socket composition, epochs, epoch-safe sending, and receive-thread
start/stop plumbing were implemented in chunk 07. This chunk (08) fills in
``_process_received_chunk``: raw-byte dispatch, per-epoch incremental UTF-8
reconstruction, delimiter-token splitting, and the internal connection
observer notification. Client connect, server listen, and binary framing are
later chunks; this module intentionally has no package export yet.
"""

from __future__ import annotations

import atexit
import codecs
import logging
import math
import socket
import threading
import weakref
from collections.abc import Callable
from enum import Enum, auto
from typing import Protocol


class EpochSendStatus(Enum):
    """Outcome of an internal epoch-scoped send attempt."""

    SENT = auto()
    NOT_ACTIVE = auto()
    IO_FAILED = auto()


class ConnectionObserver(Protocol):
    """Internal observer of epoch-tagged string tokens and epoch closure.

    Calls execute outside all internal locks and may overlap a concurrent
    close; epoch identity makes either ordering safe for the observer to
    handle. ``on_string_token`` is invoked by the receive-dispatch extension
    point added in chunk 08 — this chunk only defines the contract and never
    calls it.
    """

    def on_string_token(self, epoch: int, token: str) -> None: ...

    def on_epoch_closed(self, epoch: int, cause: str) -> None: ...


def _finalize_socket(
    sock: socket.socket,
    thread: threading.Thread | None,
    stop_event: threading.Event,
    join_timeout: float,
    logger: logging.Logger,
) -> None:
    """Best-effort, idempotent socket teardown used by GC finalization.

    Deliberately takes no reference to the owning ``SocketHandler`` (only the
    plain resources needed) so registering this finalizer can never keep the
    handler alive past its last real reference. It also does not invoke the
    connection observer: running arbitrary callback code during garbage
    collection or interpreter shutdown is unsafe, and this path exists purely
    to guarantee the file descriptor is closed. Must never raise.
    """
    try:
        stop_event.set()
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            sock.close()
        except OSError:
            pass
        if (
            thread is not None
            and thread.ident is not None
            and thread is not threading.current_thread()
        ):
            thread.join(join_timeout)
            if thread.is_alive():
                logger.warning("socket handler: receive worker still alive after finalization")
    except Exception:  # pragma: no cover - defensive: finalizers must never raise
        try:
            logger.debug("socket handler: finalizer cleanup raised", exc_info=True)
        except Exception:
            pass


class SocketHandler:
    """Owns one attached ``socket.socket`` and its connection epoch.

    ``join_timeout`` bounds every join this handler performs on its own
    receive thread and must be finite and strictly positive. ``string_delimiter``
    must be non-empty (used by the chunk-08 text-dispatch extension point, not
    by this chunk).

    State, send, callback, and observer synchronization are kept on four
    distinct locks so a slow callback or a blocking ``sendall`` can never
    stall an unrelated concern (e.g. a state read).
    """

    def __init__(
        self,
        logger: logging.Logger,
        *,
        string_delimiter: str = "\n",
        join_timeout: float = 1.0,
    ) -> None:
        if not string_delimiter:
            raise ValueError("string_delimiter must be non-empty")
        if not math.isfinite(join_timeout) or join_timeout <= 0:
            raise ValueError(f"join_timeout must be finite and > 0, got {join_timeout!r}")

        self._logger = logger
        self._string_delimiter = string_delimiter
        self._join_timeout = join_timeout

        self._state_lock = threading.Lock()
        self._send_lock = threading.Lock()
        self._callback_lock = threading.Lock()
        self._observer_lock = threading.Lock()

        self._next_epoch = 0
        self._socket: socket.socket | None = None
        self._epoch: int | None = None
        self._receive_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

        self._data_message_handler: Callable[[bytes], None] | None = None
        self._string_message_handler: Callable[[str], None] | None = None
        self._connection_observer: ConnectionObserver | None = None

        # Per-epoch text reconstruction state, reset on attach and discarded
        # on detach. Guarded by `_state_lock` alongside the epoch identity
        # check so a lingering worker from a superseded epoch can never read
        # or mutate a newer epoch's decoder/buffer (see `_tokenize_for_epoch`).
        self._text_decoder: codecs.IncrementalDecoder | None = None
        self._pending_text: str = ""

        self._finalizer: weakref.finalize[..., SocketHandler] | None = None
        atexit.register(self._atexit_cleanup)

    # -- public surface (threadedSocketTransport.md#common-handler) --------

    @property
    def is_connected(self) -> bool:
        """Whether the current connection epoch owns an attached socket."""
        with self._state_lock:
            return self._socket is not None

    @property
    def string_delimiter(self) -> str:
        return self._string_delimiter

    def send(self, data: bytes) -> bool:
        """Send ``data`` on the active connection.

        Returns ``True`` only when every byte was accepted by the same epoch
        that was active when the call began. When disconnected this logs a
        warning, drops the bytes, and returns ``False`` without raising.
        """
        epoch = self.snapshot_active_epoch()
        if epoch is None:
            self._logger.warning(
                "socket handler: send while disconnected; dropping %d byte(s)", len(data)
            )
            return False
        return self.send_for_epoch(epoch, data) is EpochSendStatus.SENT

    def send_string(self, data: str) -> bool:
        """UTF-8 encode ``data`` (no delimiter appended) and send it."""
        return self.send(data.encode("utf-8"))

    def set_data_message_handler(self, handler: Callable[[bytes], None] | None) -> None:
        with self._callback_lock:
            self._data_message_handler = handler

    def set_string_message_handler(self, handler: Callable[[str], None] | None) -> None:
        with self._callback_lock:
            self._string_message_handler = handler

    def disconnect(self) -> None:
        """Detach the active connection, if any. Idempotent."""
        epoch = self.snapshot_active_epoch()
        if epoch is None:
            return
        self._detach(epoch, cause="explicit disconnect")

    # -- internal operations exposed to composing facades -------------------

    def snapshot_active_epoch(self) -> int | None:
        """Atomically read the currently active epoch, or ``None`` if detached."""
        with self._state_lock:
            if self._socket is None:
                return None
            return self._epoch

    def send_for_epoch(self, epoch: int, data: bytes) -> EpochSendStatus:
        """Send ``data`` only if ``epoch`` is still the active connection.

        Snapshots the socket and epoch under the state lock, releases it
        before the blocking ``sendall``, serializes ``sendall`` calls under a
        distinct send lock, and — only after releasing that send lock —
        conditionally detaches the captured epoch on ``OSError``. Never
        propagates the socket error.
        """
        with self._state_lock:
            if self._epoch != epoch or self._socket is None:
                return EpochSendStatus.NOT_ACTIVE
            sock = self._socket

        io_failed = False
        with self._send_lock:
            try:
                sock.sendall(data)
            except OSError as error:
                self._logger.error("socket handler: send failed on epoch %s: %s", epoch, error)
                io_failed = True

        if io_failed:
            self._detach(epoch, cause="send failure")
            return EpochSendStatus.IO_FAILED
        return EpochSendStatus.SENT

    def set_connection_observer(self, observer: ConnectionObserver | None) -> None:
        with self._observer_lock:
            self._connection_observer = observer

    # -- receive-thread start/stop plumbing (dispatch itself is chunk 08) ---

    def _attach(self, sock: socket.socket) -> int:
        """Attach a connected socket, allocate the next epoch, and start the
        daemon receive thread. Returns the newly allocated epoch.

        Does not detach any currently active connection first — composing an
        incumbent-safe reconnect (e.g. client ``connect``, server admission)
        is the responsibility of the facade calling this primitive.
        """
        with self._state_lock:
            self._next_epoch += 1
            epoch = self._next_epoch
            self._socket = sock
            self._epoch = epoch
            self._text_decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
            self._pending_text = ""
            self._stop_event.clear()
            thread = threading.Thread(
                target=self._receive_loop,
                args=(epoch, sock, self._stop_event),
                name=f"{type(self).__name__}-receive-{epoch}",
                daemon=True,
            )
            self._receive_thread = thread

        if self._finalizer is not None:
            self._finalizer.detach()
        self._finalizer = weakref.finalize(
            self, _finalize_socket, sock, thread, self._stop_event, self._join_timeout, self._logger
        )

        thread.start()
        return epoch

    def _detach(self, expected_epoch: int, cause: str = "disconnected") -> bool:
        """Idempotent, epoch-conditional teardown.

        No-ops (returns ``False``) unless ``expected_epoch`` is still the
        active epoch. Never joins the calling thread and never joins while
        holding a lock. Logs, rather than raises, a worker still alive after
        ``join_timeout``.
        """
        with self._state_lock:
            if self._epoch != expected_epoch or self._socket is None:
                return False
            sock = self._socket
            thread = self._receive_thread
            stop_event = self._stop_event
            self._socket = None
            self._epoch = None
            self._receive_thread = None
            # Discard rather than flush: an incomplete code point or token
            # belongs only to the connection that produced it.
            self._text_decoder = None
            self._pending_text = ""

        stop_event.set()
        self._notify_epoch_closed(expected_epoch, cause)

        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        finally:
            try:
                sock.close()
            except OSError:
                pass

        # ``thread.ident is None`` means the receive worker was published (via
        # _attach / server admission) but its ``Thread.start()`` had not yet run
        # when this detach ran; joining an unstarted thread raises RuntimeError,
        # so skip the join in that pre-start window.
        if (
            thread is not None
            and thread.ident is not None
            and thread is not threading.current_thread()
        ):
            thread.join(self._join_timeout)
            if thread.is_alive():
                self._logger.warning(
                    "socket handler: receive worker for epoch %s still alive after join_timeout",
                    expected_epoch,
                )
        return True

    def _receive_loop(self, epoch: int, sock: socket.socket, stop_event: threading.Event) -> None:
        try:
            while True:
                try:
                    data = sock.recv(4096)
                except OSError:
                    if stop_event.is_set():
                        return
                    self._detach(epoch, cause="receive error")
                    return

                if stop_event.is_set():
                    return

                if not data:
                    self._detach(epoch, cause="peer closed connection")
                    return

                self._process_received_chunk(epoch, data)
        except Exception:
            self._logger.exception(
                "socket handler: receive loop for epoch %s crashed unexpectedly", epoch
            )

    def _process_received_chunk(self, epoch: int, data: bytes) -> None:
        """Extension point for received-byte dispatch.

        Default behavior: dispatch the raw chunk unchanged to the raw-data
        handler, then feed it through this epoch's incremental UTF-8 decoder
        and deliver complete delimiter-split tokens to the string handler and
        the connection observer, in that order, for each token.

        A specialization (e.g. chunk 12's binary-framed client) MAY extend
        this but SHALL preserve these default channels unless its own public
        contract says otherwise.

        Dropped entirely, before either channel runs, when ``epoch`` is no
        longer the active epoch: a lingering worker from a superseded
        connection (e.g. mid-flight when a replacement attaches) must not
        deliver stale bytes or mutate a newer epoch's decoder/buffer state.
        """
        if not self._epoch_is_current(epoch):
            return

        self._invoke_raw_handler(data)

        for token in self._tokenize_for_epoch(epoch, data):
            self._invoke_string_handler(token)
            self._notify_string_token(epoch, token)

    def _epoch_is_current(self, epoch: int) -> bool:
        with self._state_lock:
            return self._socket is not None and self._epoch == epoch

    def _tokenize_for_epoch(self, epoch: int, data: bytes) -> list[str]:
        """Decode ``data`` and split off complete delimiter-terminated tokens.

        Re-checks epoch identity under the same lock that guards the
        decoder/buffer so a superseded worker can neither read nor mutate a
        newer epoch's text-reconstruction state, even if it raced past the
        earlier ``_epoch_is_current`` check in ``_process_received_chunk``.
        """
        with self._state_lock:
            if self._socket is None or self._epoch != epoch or self._text_decoder is None:
                return []
            text = self._text_decoder.decode(data)
            combined = self._pending_text + text
            pieces = combined.split(self._string_delimiter)
            self._pending_text = pieces[-1]
            return pieces[:-1]

    def _invoke_raw_handler(self, data: bytes) -> None:
        with self._callback_lock:
            handler = self._data_message_handler
        if handler is None:
            return
        try:
            handler(data)
        except Exception:
            self._logger.exception("socket handler: raw data handler raised")

    def _invoke_string_handler(self, token: str) -> None:
        with self._callback_lock:
            handler = self._string_message_handler
        if handler is None:
            return
        try:
            handler(token)
        except Exception:
            self._logger.exception("socket handler: string message handler raised")

    def _notify_string_token(self, epoch: int, token: str) -> None:
        with self._observer_lock:
            observer = self._connection_observer
        if observer is None:
            return
        try:
            observer.on_string_token(epoch, token)
        except Exception:
            self._logger.exception(
                "socket handler: connection observer on_string_token raised for epoch %s", epoch
            )

    def _notify_epoch_closed(self, epoch: int, cause: str) -> None:
        with self._observer_lock:
            observer = self._connection_observer
        if observer is None:
            return
        try:
            observer.on_epoch_closed(epoch, cause)
        except Exception:
            self._logger.exception(
                "socket handler: connection observer on_epoch_closed raised for epoch %s", epoch
            )

    # -- best-effort process-exit cleanup ------------------------------------

    def _atexit_cleanup(self) -> None:
        try:
            self.disconnect()
        except Exception:  # pragma: no cover - defensive: atexit must never raise
            try:
                self._logger.debug("socket handler: atexit cleanup raised", exc_info=True)
            except Exception:
                pass
