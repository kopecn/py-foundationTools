"""
SocketHandlerClient -- synchronous IPv4 client connect (plan 25, chunk 09),
with serialized connect/disconnect lifecycle (plan 25, chunk 17).

Extends ``SocketHandler`` (chunks 07-08) with ``connect(host, port,
timeout)``: connection-timeout validation ordered before any incumbent
teardown, incumbent-safe reconnect, blocking-mode restoration after a
successful connect, and candidate-socket cleanup with the original
``OSError`` propagated on failure. See
``.claude/specs/threadedSocketTransport.md#client`` for the full behavioral
contract.

``connect()`` and public ``disconnect()`` share one non-reentrant
``_lifecycle_lock`` so concurrent callers cannot orphan a socket or receive
worker (PA25-01): the lock is held across incumbent teardown, candidate
connect, blocking-mode restoration, and attachment, and it is distinct from
the state/send locks a blocking ``connect()`` must not hold. Internal
teardown goes through ``_disconnect_locked`` (which calls
``SocketHandler.disconnect`` directly, bypassing the overridden public
``disconnect``) so ``connect()`` never recursively acquires its own lock.

Deliberately not a ``foundation_abc.PeripheralByteTransport`` -- that ABC is
fully asynchronous and out of scope for this synchronous, threaded chunk.
"""

from __future__ import annotations

import logging
import math
import socket
import threading

from foundation_tools.socket_transaction.socket_handler import SocketHandler


class SocketHandlerClient(SocketHandler):
    """Adds synchronous IPv4 client connect to the common socket handler.

    The constructor signature is unchanged from ``SocketHandler``: it
    accepts only ``logger``, ``string_delimiter``, and ``join_timeout``.
    ``host``, ``port``, and the connection ``timeout`` belong to each
    ``connect`` call, not to construction. It adds one client-lifecycle
    lock (see module docstring) that ``SocketHandler`` does not have.
    """

    def __init__(
        self,
        logger: logging.Logger,
        *,
        string_delimiter: str = "\n",
        join_timeout: float = 1.0,
    ) -> None:
        super().__init__(logger, string_delimiter=string_delimiter, join_timeout=join_timeout)
        self._lifecycle_lock = threading.Lock()

    def connect(self, host: str, port: int, timeout: float | None = 1.0) -> None:
        """Connect to ``(host, port)``, replacing any incumbent connection.

        Validates ``timeout`` (``None`` or finite and strictly positive)
        before waiting for or changing an incumbent connection, so an
        invalid timeout leaves an existing connection untouched and never
        contends for the lifecycle lock. Once validated, this call holds
        the lifecycle lock for the remainder of the operation -- incumbent
        teardown, candidate creation and connect, blocking-mode restoration,
        and attachment -- so a concurrent ``connect()`` or ``disconnect()``
        call serializes behind it rather than interleaving. Creates a new
        ``AF_INET``/``SOCK_STREAM`` socket, applies ``timeout``, connects to
        ``(host, port)``, restores blocking mode on success, then attaches
        it. A failed connect closes the candidate socket and re-raises the
        original ``OSError`` without disturbing an already-completed
        incumbent disconnect, leaving no receive thread or attached socket.
        """
        self._validate_connect_timeout(timeout)

        with self._lifecycle_lock:
            self._disconnect_locked()

            candidate = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                candidate.settimeout(timeout)
                candidate.connect((host, port))
            except OSError:
                candidate.close()
                raise

            candidate.settimeout(None)
            self._attach(candidate)

    def disconnect(self) -> None:
        """Detach the active connection, if any. Idempotent.

        Participates in the same lifecycle serialization as ``connect()``:
        a ``disconnect()`` racing an in-flight ``connect()`` waits for that
        ``connect()`` to finish (rather than no-op against a not-yet-attached
        candidate) and then tears down whatever it attached.
        """
        with self._lifecycle_lock:
            self._disconnect_locked()

    def _disconnect_locked(self) -> None:
        """Tear down the incumbent connection. Caller must hold ``_lifecycle_lock``.

        Calls ``SocketHandler.disconnect`` directly (not ``self.disconnect``)
        so this never recursively acquires the non-reentrant lifecycle lock.
        """
        super().disconnect()

    @staticmethod
    def _validate_connect_timeout(timeout: float | None) -> None:
        if timeout is None:
            return
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError(f"connect timeout must be None or finite and > 0, got {timeout!r}")
