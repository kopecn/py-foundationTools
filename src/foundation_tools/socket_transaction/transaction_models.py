"""
Threaded transaction protocol values.

Defines the immutable wire-frame and outcome types shared by the codec,
transaction-core, and facade layers of the threaded socket transaction stack:
``TransactionFrame``, the ``SendStatus`` / ``AckStatus`` / ``CompletionStatus``
enums, and the immutable ``TransactionOutcome``.

Contract: ``.claude/specs/threadedTransactionProtocol.md`` ("Transaction
frame" and "Pending transaction" sections). This module intentionally has no
socket or transaction-core behavior: no codec serialization and no mutable
pending transaction state. ``TransactionFrame``, ``TransactionOutcome``, and
the three status enums are exported from the package ``__init__.py``.
"""

from dataclasses import dataclass, field
from enum import Enum, auto


class SendStatus(Enum):
    """Outcome of attempting to place a frame on the wire."""

    SENT = auto()
    NOT_CONNECTED = auto()
    FAILED = auto()


class AckStatus(Enum):
    """Outcome of a requested acknowledgement stage."""

    NOT_REQUESTED = auto()
    ACKNOWLEDGED = auto()
    REJECTED = auto()
    TIMED_OUT = auto()
    CONNECTION_CLOSED = auto()


class CompletionStatus(Enum):
    """Outcome of a requested completion (result/error) stage."""

    NOT_REQUESTED = auto()
    RESULT = auto()
    ERROR = auto()
    TIMED_OUT = auto()
    CONNECTION_CLOSED = auto()


@dataclass(frozen=True)
class TransactionFrame:
    """One transaction wire frame.

    Positive ``tx_id`` values represent peer-correlated transactions; ``-1``
    is the defined broadcast identifier. ``msg_type`` reserves ``ack``,
    ``res``, ``evt``, and ``err`` for control and response routing.
    """

    tx_id: int
    msg_type: str
    code: int
    payload: bytes | str | dict[str, object] | None = None


@dataclass(frozen=True)
class TransactionOutcome:
    """The public, truthful result of one transaction.

    ``events`` is always stored as an immutable tuple, never a caller-owned
    mutable list, regardless of what iterable is passed at construction.
    """

    tx_id: int
    send_status: SendStatus
    ack_status: AckStatus
    completion_status: CompletionStatus
    result: TransactionFrame | None
    ack_error: str | None
    completion_error: str | None
    events: tuple[TransactionFrame, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.events, tuple):
            object.__setattr__(self, "events", tuple(self.events))

    @property
    def success(self) -> bool:
        """True exactly when the send succeeded and every requested stage
        settled with its success status; an unrequested stage is neutral."""
        if self.send_status is not SendStatus.SENT:
            return False

        ack_ok = self.ack_status in (AckStatus.NOT_REQUESTED, AckStatus.ACKNOWLEDGED)
        completion_ok = self.completion_status in (
            CompletionStatus.NOT_REQUESTED,
            CompletionStatus.RESULT,
        )
        return ack_ok and completion_ok
