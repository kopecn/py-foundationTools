"""
Shared lifecycle primitives for the socket-transaction stack (fix-12).

A single, minimal source of the state representation and construction-time
numeric validation used consistently across ``SocketByteTransport``,
``TransactionRouter``, ``SocketTransact``, and ``SocketTransactServer``.

This is the bare-bones state model only: a re-usable ``IDLE`` <-> ``ACTIVE``
lifecycle whose illegal transitions are rejected rather than silently replacing
live resources. Automatic reconnect and cross-dropout upper-layer continuity are
intentionally out of scope, deferred to a future scoping effort.
"""

from enum import Enum, auto


class LifecycleState(Enum):
    """The two states a re-usable socket-transaction component occupies.

    ``IDLE`` — not connected/running: never started, or torn down by an explicit
    disconnect/stop and available to be activated again.
    ``ACTIVE`` — connected/running: holds a live resource that must not be
    silently replaced.
    """

    IDLE = auto()
    ACTIVE = auto()


def require_positive(name: str, value: float) -> None:
    """Raise ``ValueError`` unless ``value`` is strictly greater than zero."""
    if value <= 0:
        raise ValueError(f"{name} must be > 0, got {value!r}")


def require_min(name: str, value: int, minimum: int) -> None:
    """Raise ``ValueError`` unless ``value`` is at least ``minimum``."""
    if value < minimum:
        raise ValueError(f"{name} must be >= {minimum}, got {value!r}")
