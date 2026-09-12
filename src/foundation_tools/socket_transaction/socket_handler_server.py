"""
SocketHandlerServer -- single-client server listener lifecycle (plan 25, chunk 10).

Extends ``SocketHandler`` (chunks 07-08) with the *listener* half of the
single-client server contract: bind/listen, actual bound-address
publication, listener epochs independent from the inherited connection
epoch, a bounded daemon accept worker, repeated-listen warning/no-op, and
idempotent, epoch-safe ``stop``. See
``.claude/specs/threadedSocketTransport.md#single-client-server`` for the
full behavioral contract.

Chunk 11 owns admission decisions, active-client publication, ``kick``, and
incumbent replacement. Until then, ``_handle_accepted_candidate`` closes
every accepted candidate unconditionally -- this chunk never actually
serves a client.

Deliberately not a ``foundation_abc.PeripheralByteTransport`` -- that ABC is
fully asynchronous and out of scope for this synchronous, threaded design.
"""

from __future__ import annotations

import logging
import math
import socket
import threading
from dataclasses import dataclass

from foundation_tools.socket_transaction.socket_handler import SocketHandler


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
    """Adds a restartable, single-client-capable IPv4 listener.

    The constructor accepts only listener-specific configuration beyond
    the inherited ``logger``/``string_delimiter``/``join_timeout``:
    ``accept_poll_interval`` bounds how often the accept worker wakes to
    observe shutdown even while blocked in ``accept()``.
    """

    def __init__(
        self,
        logger: logging.Logger,
        *,
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

        thread.start()

    def stop(self) -> None:
        """Idempotent: retire the listener epoch, stop accepting, and join.

        Retires the listener epoch (clearing all published listener state)
        before closing the listener socket or joining the accept worker, so
        a stale, still-running worker for a retired epoch can never observe
        or rewrite a restarted listener's state. A still-alive worker after
        ``join_timeout`` is logged, not raised.
        """
        with self._listener_lock:
            if self._listener_state is None:
                return
            state = self._listener_state
            self._listener_state = None

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

    # -- accept loop and the chunk-11 admission extension point --------------

    def _accept_loop(
        self, epoch: int, listener: socket.socket, stop_event: threading.Event
    ) -> None:
        """Accept in a loop, waking at least every ``accept_poll_interval``.

        Revalidates the captured listener epoch after every accept, before
        invoking the protected candidate hook, per the stale-listener
        recipe: an epoch that is no longer active means `stop`/a restart
        already retired this worker's listener, so the candidate is closed
        and the worker exits without touching any newer epoch's state.
        """
        listener.settimeout(self._accept_poll_interval)
        try:
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
        """Protected extension point for admission decisions.

        Chunk 11 replaces this with real admission, incumbent replacement,
        and active-peer publication. Until then every accepted candidate is
        closed unconditionally: this chunk implements only the listener
        half and never actually serves a client.
        """
        try:
            candidate.close()
        except OSError:
            pass
