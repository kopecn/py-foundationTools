"""
SocketHandlerClient -- synchronous IPv4 client connect (plan 25, chunk 09).

Extends ``SocketHandler`` (chunks 07-08) with ``connect(host, port,
timeout)``: connection-timeout validation ordered before any incumbent
teardown, incumbent-safe reconnect, blocking-mode restoration after a
successful connect, and candidate-socket cleanup with the original
``OSError`` propagated on failure. See
``.claude/specs/threadedSocketTransport.md#client`` for the full behavioral
contract.

Deliberately not a ``foundation_abc.PeripheralByteTransport`` -- that ABC is
fully asynchronous and out of scope for this synchronous, threaded chunk.
"""

from __future__ import annotations

import math
import socket

from foundation_tools.socket_transaction.socket_handler import SocketHandler


class SocketHandlerClient(SocketHandler):
    """Adds synchronous IPv4 client connect to the common socket handler.

    The constructor is inherited unchanged from ``SocketHandler``: it
    accepts only ``logger``, ``string_delimiter``, and ``join_timeout``.
    ``host``, ``port``, and the connection ``timeout`` belong to each
    ``connect`` call, not to construction.
    """

    def connect(self, host: str, port: int, timeout: float | None = 1.0) -> None:
        """Connect to ``(host, port)``, replacing any incumbent connection.

        Validates ``timeout`` (``None`` or finite and strictly positive)
        before disconnecting an incumbent connection, so an invalid timeout
        leaves an existing connection untouched. Creates a new
        ``AF_INET``/``SOCK_STREAM`` socket, applies ``timeout``, connects to
        ``(host, port)``, restores blocking mode on success, then attaches
        it. A failed connect closes the candidate socket and re-raises the
        original ``OSError`` without disturbing an already-completed
        incumbent disconnect, leaving no receive thread or attached socket.
        """
        self._validate_connect_timeout(timeout)
        self.disconnect()

        candidate = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            candidate.settimeout(timeout)
            candidate.connect((host, port))
        except OSError:
            candidate.close()
            raise

        candidate.settimeout(None)
        self._attach(candidate)

    @staticmethod
    def _validate_connect_timeout(timeout: float | None) -> None:
        if timeout is None:
            return
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError(f"connect timeout must be None or finite and > 0, got {timeout!r}")
