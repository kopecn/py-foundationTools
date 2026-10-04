"""
Deterministic threading test support for the threaded socket-transaction chunks
(plan 25: ``.claude/plans/25-threaded-socket-transaction/``).

Every coordination primitive here uses ``threading.Event``/bounded joins only —
never a fixed or nondeterministic delay — per the "Race recipe" in
``01-threaded-test-support.md`` and the concurrency model in
``.claude/specs/threadedSocketTransaction.md#concurrency-model``.

Exposes:

- ``WorkerHandle`` / ``start_worker``: a named daemon thread that captures any
  exception it raises and re-raises it from a bounded ``join`` (also usable as a
  context manager for the "owning context manager" surfacing pattern).
- ``ThreadedLoopbackListener``: a context-managed IPv4 listener on
  ``127.0.0.1:0`` for tests that need real connect/accept behavior.
- ``socketpair_context``: a ``socket.socketpair()`` context manager for
  base-handler tests that do not need IPv4 connect/listen behavior.
"""

from __future__ import annotations

import socket
import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from types import TracebackType

TEST_TIMEOUT = 5.0


class WorkerTimeoutError(AssertionError):
    """A helper-owned thread did not reach the expected state within its bound."""


class WorkerHandle:
    """A named daemon thread whose exception is captured for re-raise, not swallowed.

    Construct via :func:`start_worker`. ``join`` blocks up to ``timeout`` seconds,
    asserts the thread is dead (raising :class:`WorkerTimeoutError` naming the
    worker if not), then re-raises any exception the worker raised. Also usable
    directly as a context manager: entering returns the already-started handle,
    and exiting calls ``join`` with the default timeout.
    """

    def __init__(self, name: str, target: Callable[[], None]) -> None:
        self.name = name
        self.exception: BaseException | None = None
        self._thread = threading.Thread(target=self._wrap(target), name=name, daemon=True)

    def _wrap(self, target: Callable[[], None]) -> Callable[[], None]:
        def _runner() -> None:
            try:
                target()
            except Exception as exc:  # captured for re-raise from join(), not swallowed
                self.exception = exc

        return _runner

    def start(self) -> WorkerHandle:
        self._thread.start()
        return self

    def is_alive(self) -> bool:
        return self._thread.is_alive()

    def join(self, timeout: float = TEST_TIMEOUT) -> None:
        """Join with a bounded timeout, assert death, then re-raise a captured exception."""

        self._thread.join(timeout)
        if self._thread.is_alive():
            raise WorkerTimeoutError(f"worker {self.name!r} did not finish within {timeout}s")
        if self.exception is not None:
            raise self.exception

    def __enter__(self) -> WorkerHandle:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.join()


def start_worker(name: str, target: Callable[[], None]) -> WorkerHandle:
    """Start ``target`` on a named daemon thread, capturing any exception it raises."""

    return WorkerHandle(name, target).start()


class ThreadedLoopbackListener:
    """Context-managed IPv4 listener bound to ``127.0.0.1:0``.

    Runs one background accept thread (via :class:`WorkerHandle`) and exposes the
    listener's actual bound address as ``address``. Coordinates with the caller
    via four ``threading.Event`` gates instead of fixed or nondeterministic delays:

    - ``ready``: set once the socket is bound, listening, and the accept thread
      is about to block in ``accept()``.
    - ``accepted``: set once a client connection has been accepted; the accepted
      socket is then available as ``accepted_socket``.
    - ``release``: the caller sets this to let the accept thread finish. The
      caller must always set this before the ``with`` block exits — the accept
      thread will not proceed past it on its own, and ``__exit__`` will surface
      a bounded ``WorkerTimeoutError`` (naming the worker) if it never runs.
    - ``stopped``: set once the accept thread has run to completion after being
      released.

    Any exception raised inside the accept thread is captured and re-raised from
    ``__exit__`` after both the accepted socket and the listening socket are
    closed.
    """

    def __init__(self, timeout: float = TEST_TIMEOUT) -> None:
        self.timeout = timeout
        self.ready = threading.Event()
        self.accepted = threading.Event()
        self.release = threading.Event()
        self.stopped = threading.Event()
        self.accepted_socket: socket.socket | None = None

        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_socket.bind(("127.0.0.1", 0))
        self.listen_socket.listen(1)
        self.address: tuple[str, int] = self.listen_socket.getsockname()

        self._worker = WorkerHandle("threaded-loopback-listener", self._accept_loop)

    def _accept_loop(self) -> None:
        self.ready.set()
        connection, _ = self.listen_socket.accept()
        self.accepted_socket = connection
        self.accepted.set()
        if not self.release.wait(self.timeout):
            raise WorkerTimeoutError(
                f"threaded-loopback-listener: test did not set release within {self.timeout}s"
            )
        self.stopped.set()

    def __enter__(self) -> ThreadedLoopbackListener:
        self._worker.start()
        if not self.ready.wait(self.timeout):
            raise WorkerTimeoutError("threaded-loopback-listener: listener never became ready")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        try:
            self._worker.join(self.timeout)
        finally:
            if self.accepted_socket is not None:
                self.accepted_socket.close()
            self.listen_socket.close()


@contextmanager
def socketpair_context() -> Iterator[tuple[socket.socket, socket.socket]]:
    """Yield a connected ``socket.socketpair()``, closing both ends on exit.

    For base-handler tests that need a live, already-connected byte stream
    without exercising IPv4 connect/listen behavior.
    """

    left, right = socket.socketpair()
    try:
        yield left, right
    finally:
        left.close()
        right.close()
