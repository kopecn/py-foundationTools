"""
SocketHandlerServer -- single-client server admission and replacement
(plan 25, chunk 11).

Extends the chunk-10 listener half of ``SocketHandlerServer`` with the
active-client half of the single-client server contract: an optional
admission handler invoked on the accept thread outside every lock,
incumbent-safe challenger replacement, level-triggered ``wait_for_connection``,
``kick``, and epoch-safe peer cleanup. See
``.claude/specs/threadedSocketTransport.md#single-client-server`` for the
full behavioral contract.

Deliberately not a ``foundation_abc.PeripheralByteTransport`` -- that ABC is
fully asynchronous and out of scope for this synchronous, threaded design.
"""

from __future__ import annotations

import codecs
import logging
import math
import socket
import threading
import time
import weakref
from collections.abc import Callable
from dataclasses import dataclass

from foundation_tools.socket_transaction.socket_handler import SocketHandler, _finalize_socket


@dataclass
class _ListenerState:
    """One listener epoch's published state, replaced atomically per `listen`.

    Grouping these fields lets `stop` and the accept worker's staleness
    check swap or read the whole epoch in one lock acquisition, so a
    worker can never observe a torn mix of an old socket with a new epoch
    (or vice versa).
    """

    epoch: int
    socket: socket.socket
    address: tuple[str, int]
    stop_event: threading.Event
    thread: threading.Thread


class SocketHandlerServer(SocketHandler):
    """A restartable, single-active-client-capable IPv4 listener.

    The constructor accepts only listener-specific configuration beyond the
    inherited ``logger``/``string_delimiter``/``join_timeout``:
    ``connection_admission_handler`` decides whether an accepted peer is
    admitted, and ``accept_poll_interval`` bounds how often the accept
    worker wakes to observe shutdown even while blocked in ``accept()``.
    """

    def __init__(
        self,
        logger: logging.Logger,
        *,
        connection_admission_handler: Callable[[tuple[str, int]], bool] | None = None,
        string_delimiter: str = "\n",
        join_timeout: float = 1.0,
        accept_poll_interval: float = 0.2,
    ) -> None:
        super().__init__(logger, string_delimiter=string_delimiter, join_timeout=join_timeout)
        if not math.isfinite(accept_poll_interval) or accept_poll_interval <= 0:
            raise ValueError(
                f"accept_poll_interval must be finite and > 0, got {accept_poll_interval!r}"
            )
        self._accept_poll_interval = accept_poll_interval

        self._listener_lock = threading.Lock()
        self._next_listener_epoch = 0
        self._listener_state: _ListenerState | None = None

        # Snapshot-under-lock, invoke-outside-every-lock, per the chunk's
        # admission-isolation constraint. There is no public setter (the
        # handler is constructor-only), but the lock still guards the read
        # so the pattern matches every other callback field in this stack.
        self._admission_lock = threading.Lock()
        self._connection_admission_handler = connection_admission_handler

        # Guarded by the inherited `_state_lock` alongside `_socket`/`_epoch`
        # so the challenger socket, connection epoch, and peer publish (or
        # clear) as one atomic unit for any reader of `active_peer` /
        # `is_connected`.
        self._active_peer: tuple[str, int] | None = None
        self._active_peer_epoch: int | None = None

        # Wakes a `wait_for_connection` waiter on every publish/detach; the
        # waiter always re-checks `is_connected` itself (level-triggered),
        # never trusts the edge alone.
        self._connection_state_changed = threading.Event()

    # -- public surface (threadedSocketTransport.md#single-client-server) ---

    @property
    def is_listening(self) -> bool:
        """Whether a listener epoch currently owns a bound listener socket."""
        with self._listener_lock:
            return self._listener_state is not None

    @property
    def listening_address(self) -> tuple[str, int] | None:
        """The actual bound ``(host, port)`` while listening, else ``None``."""
        with self._listener_lock:
            return self._listener_state.address if self._listener_state is not None else None

    @property
    def active_peer(self) -> tuple[str, int] | None:
        """The connected peer's ``(host, port)`` while a client is active."""
        with self._state_lock:
            return self._active_peer

    def listen(self, port: int) -> None:
        """Start listening on ``port`` (``0`` selects an ephemeral port).

        Creates an ``AF_INET``/``SOCK_STREAM`` listener, enables
        ``SO_REUSEADDR``, binds ``("", port)``, starts listening, publishes
        the actual bound address from ``getsockname``, and starts one named
        daemon accept worker for a freshly allocated listener epoch with its
        own stop event. Calling this while already listening logs a warning
        and changes nothing. A bind/listen failure closes the candidate
        listener and propagates the original ``OSError``.
        """
        with self._listener_lock:
            if self._listener_state is not None:
                self._logger.warning(
                    "socket handler server: already listening on %s; ignoring listen(%d)",
                    self._listener_state.address,
                    port,
                )
                return

        candidate = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            candidate.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            candidate.bind(("", port))
            candidate.listen()
        except OSError:
            candidate.close()
            raise

        address = candidate.getsockname()

        with self._listener_lock:
            if self._listener_state is not None:
                # Lost a race against a concurrent successful `listen()`;
                # the incumbent stands, this candidate never existed.
                candidate.close()
                self._logger.warning(
                    "socket handler server: lost race to a concurrent listen(); "
                    "closing candidate for listen(%d)",
                    port,
                )
                return

            self._next_listener_epoch += 1
            epoch = self._next_listener_epoch
            stop_event = threading.Event()
            thread = threading.Thread(
                target=self._accept_loop,
                args=(epoch, candidate, stop_event),
                name=f"{type(self).__name__}-accept-{epoch}",
                daemon=True,
            )
            self._listener_state = _ListenerState(
                epoch=epoch,
                socket=candidate,
                address=address,
                stop_event=stop_event,
                thread=thread,
            )

            # `thread.start()` runs inside the same critical section that
            # published `_listener_state`, so publication and startup are
            # inseparable as observed by `stop()`: a concurrent `stop()`
            # cannot acquire this lock -- and therefore cannot see or join
            # this thread -- until it has actually started. If `start()`
            # raises, retire only this epoch and close the candidate; the
            # listener was never truly published.
            try:
                thread.start()
            except Exception:
                self._listener_state = None
                candidate.close()
                raise

    def wait_for_connection(self, timeout: float | None = None) -> bool:
        """Block until a client is active, or ``timeout`` elapses.

        ``None`` waits indefinitely; a finite non-negative ``timeout``
        (``0`` performs an immediate check) bounds the wait. Level-triggered:
        returns ``True`` only if an active client epoch exists at the
        instant it returns, and otherwise keeps waiting until the deadline
        rather than trusting a single edge-triggered wake.
        """
        if timeout is not None and (not math.isfinite(timeout) or timeout < 0):
            raise ValueError(
                f"wait_for_connection timeout must be None or finite and >= 0, got {timeout!r}"
            )

        deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            if self.is_connected:
                return True
            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
            else:
                remaining = None
            self._connection_state_changed.wait(remaining)
            self._connection_state_changed.clear()

    def kick(self) -> None:
        """Detach the active connection, if any, leaving the listener running."""
        epoch = self.snapshot_active_epoch()
        if epoch is not None:
            self._detach(epoch, cause="kicked")

    def stop(self) -> None:
        """Idempotent: retire the listener epoch, stop accepting, join, and
        kick the active client.

        Retires the listener epoch (clearing all published listener state)
        before closing the listener socket or joining the accept worker, so
        a stale, still-running worker for a retired epoch can never observe
        or rewrite a restarted listener's state. A still-alive worker after
        ``join_timeout`` is logged, not raised. Kicks the active client only
        after the listener itself is fully retired, per the contract's
        "retire listener then kick" ordering; leaves no listener and no
        active connection.
        """
        with self._listener_lock:
            state = self._listener_state
            self._listener_state = None

        if state is not None:
            state.stop_event.set()
            try:
                state.socket.close()
            except OSError:
                pass

            if state.thread is not threading.current_thread():
                state.thread.join(self._join_timeout)
                if state.thread.is_alive():
                    self._logger.warning(
                        "socket handler server: accept worker for listener epoch %s still "
                        "alive after join_timeout",
                        state.epoch,
                    )

        self.kick()

    # -- accept loop and admission -------------------------------------------

    def _accept_loop(
        self, epoch: int, listener: socket.socket, stop_event: threading.Event
    ) -> None:
        """Accept in a loop, waking at least every ``accept_poll_interval``.

        Revalidates the captured listener epoch after every accept, before
        invoking the admission hook, per the stale-listener recipe: an epoch
        that is no longer active means `stop`/a restart already retired this
        worker's listener, so the candidate is closed and the worker exits
        without touching any newer epoch's state.
        """
        try:
            listener.settimeout(self._accept_poll_interval)
            while not stop_event.is_set():
                try:
                    candidate, peer = listener.accept()
                except TimeoutError:
                    continue
                except OSError:
                    return

                if not self._listener_epoch_is_active(epoch):
                    candidate.close()
                    return

                self._handle_accepted_candidate(epoch, candidate, peer)
        except Exception:
            self._logger.exception(
                "socket handler server: accept loop for listener epoch %s crashed unexpectedly",
                epoch,
            )

    def _listener_epoch_is_active(self, epoch: int) -> bool:
        with self._listener_lock:
            return self._listener_state is not None and self._listener_state.epoch == epoch

    def _handle_accepted_candidate(
        self, epoch: int, candidate: socket.socket, peer: tuple[str, int]
    ) -> None:
        """Admit or reject ``candidate``, and publish it as the active
        connection.

        Runs on the accept thread. No admission handler means admit; a
        handler returning falsy or raising means reject -- either way the
        challenger is closed without touching any incumbent. An admitted
        challenger first detaches the incumbent (a potentially blocking
        operation), then -- in the same critical section ``stop`` uses to
        retire the listener -- performs one final listener-epoch
        revalidation and publishes itself as the active connection. A stale
        worker (whose listener has since been stopped or restarted) closes
        the challenger instead of publishing it. The receive worker starts
        only after publication, once the listener lock has been released.
        """
        if not self._is_admitted(peer):
            try:
                candidate.close()
            except OSError:
                pass
            return

        self._detach_current_client()

        with self._listener_lock:
            if self._listener_state is None or self._listener_state.epoch != epoch:
                try:
                    candidate.close()
                except OSError:
                    pass
                return
            connection_epoch = self._publish_client_locked(candidate, peer)

        self._start_receive_worker(connection_epoch)

    def _is_admitted(self, peer: tuple[str, int]) -> bool:
        """Snapshot the admission handler under its lock, then invoke it
        outside every lock. Missing handler admits; a raised exception
        rejects and is logged."""
        with self._admission_lock:
            handler = self._connection_admission_handler
        if handler is None:
            return True
        try:
            return bool(handler(peer))
        except Exception:
            self._logger.exception(
                "socket handler server: connection admission handler raised for peer %s", peer
            )
            return False

    def _detach_current_client(self) -> None:
        """Detach the current active connection, if any, before publishing
        a challenger."""
        epoch = self.snapshot_active_epoch()
        if epoch is not None:
            self._detach(epoch, cause="replaced by new connection")

    def _publish_client_locked(self, candidate: socket.socket, peer: tuple[str, int]) -> int:
        """Atomically publish ``candidate``/``peer`` as the active
        connection.

        Caller must hold ``_listener_lock`` and must have already
        revalidated the listener epoch in that same critical section.
        Allocates a new connection epoch and publishes the socket, epoch,
        and peer together under ``_state_lock`` -- mirroring
        ``SocketHandler._attach``'s per-connection reset of the incremental
        text decoder and stop signal -- but does not itself start the
        receive worker; ``_start_receive_worker`` does that once the caller
        has released ``_listener_lock``, per the chunk's replacement race
        recipe.
        """
        with self._state_lock:
            self._next_epoch += 1
            epoch = self._next_epoch
            self._socket = candidate
            self._epoch = epoch
            self._active_peer = peer
            self._active_peer_epoch = epoch
            self._text_decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
            self._pending_text = ""
            self._stop_event.clear()

        self._connection_state_changed.set()
        return epoch

    def _start_receive_worker(self, epoch: int) -> None:
        """Start the receive worker for ``epoch``, if it is still current.

        Revalidates under ``_state_lock`` because a concurrent
        ``kick``/``stop``/``disconnect`` may already have detached this
        epoch in the window between ``_publish_client_locked`` and this
        call. Registers the same best-effort GC finalizer as
        ``SocketHandler._attach`` and rolls the epoch back if the thread
        fails to start.
        """
        with self._state_lock:
            if self._epoch != epoch or self._socket is None:
                return
            sock = self._socket
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

        try:
            thread.start()
        except Exception:
            self._logger.exception(
                "socket handler server: receive worker for connection epoch %s failed to start",
                epoch,
            )
            self._rollback_unstarted_worker(epoch)

    def _rollback_unstarted_worker(self, epoch: int) -> None:
        """Undo a publish whose receive worker failed to start.

        Mirrors ``SocketHandler._detach``'s state clearing and
        close-observer notification, but never joins ``thread``: it was
        never actually started, so ``Thread.join`` would raise
        ``RuntimeError``.
        """
        with self._state_lock:
            if self._epoch != epoch or self._socket is None:
                return
            sock = self._socket
            self._socket = None
            self._epoch = None
            self._receive_thread = None
            self._text_decoder = None
            self._pending_text = ""
            if self._active_peer_epoch == epoch:
                self._active_peer = None
                self._active_peer_epoch = None

        self._connection_state_changed.set()
        self._notify_epoch_closed(epoch, cause="receive worker failed to start")

        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        finally:
            try:
                sock.close()
            except OSError:
                pass

    def _detach(self, expected_epoch: int, cause: str = "disconnected") -> bool:
        """As ``SocketHandler._detach``, but also clears ``active_peer``
        for the matching epoch.

        Every teardown path (peer EOF/receive error, ``send`` failure,
        ``disconnect``, ``kick``, incumbent replacement) routes through this
        override, so ``active_peer`` and connection availability always
        clear together for the epoch that actually closed -- never for a
        newer epoch that has since published its own peer. Clears
        ``active_peer`` *before* delegating to ``super()._detach``: that
        base call fires the epoch-closed observer notification partway
        through its own critical section, before it returns, so clearing
        afterward would let an observer (or a caller woken by one) observe
        a connection already reported disconnected but still showing a
        stale ``active_peer``.
        """
        with self._state_lock:
            would_detach = self._epoch == expected_epoch and self._socket is not None
            if would_detach and self._active_peer_epoch == expected_epoch:
                self._active_peer = None
                self._active_peer_epoch = None

        detached = super()._detach(expected_epoch, cause)
        if detached:
            self._connection_state_changed.set()
        return detached
