"""
Threaded transaction core — state half (Action Plan 25, chunk 05).

Implements the internal, non-exported ``PendingTransaction`` mutable state and
the state-management half of ``TransactionCore``: transaction id sequencing,
epoch-bound registration, duplicate rejection, idempotent discard, and
race-safe ACK/completion waits.

Contract: ``.claude/specs/threadedTransactionProtocol.md`` ("Pending
transaction" and "Transaction core" sections, state operations only). Frame
routing, epoch failure, callback dispatch, and outcome finalization
(``route``, ``fail_epoch``, the broadcast/inbound handler setters, and
``finalize_outcome``) are chunk 06's responsibility and are intentionally
absent here. This module is not exported from the package ``__init__.py``.
"""

import logging
import math
import threading
from dataclasses import dataclass, field

from foundation_tools.socket_transaction.transaction_models import (
    AckStatus,
    CompletionStatus,
    TransactionFrame,
)


def _require_positive_int(name: str, value: int) -> None:
    """Raise ``ValueError`` unless ``value`` is a positive integer, not a bool."""
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer, got {value!r}")


def _require_valid_timeout(timeout: float | None) -> None:
    """Raise ``ValueError`` unless ``timeout`` is ``None`` or a finite, non-negative number."""
    if timeout is None:
        return
    if not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout < 0:
        raise ValueError(f"timeout must be None or a finite non-negative number, got {timeout!r}")


@dataclass(eq=False)
class PendingTransaction:
    """Internal mutable state for one in-flight transaction.

    ``ack_status``/``completion_status`` are ``None`` while the corresponding
    stage remains unresolved; a concrete :class:`AckStatus`/
    :class:`CompletionStatus` value means the stage has settled — either by
    routing (chunk 06) or by a timed-out wait (this chunk). Not a package
    export.
    """

    epoch: int
    tx_id: int
    ack_event: threading.Event = field(default_factory=threading.Event)
    done_event: threading.Event = field(default_factory=threading.Event)
    ack_status: AckStatus | None = None
    completion_status: CompletionStatus | None = None
    acked: bool = False
    result: TransactionFrame | None = None
    ack_error: str | None = None
    completion_error: str | None = None
    events: list[TransactionFrame] = field(default_factory=list)


class TransactionCore:
    """Internal, non-exported transaction state.

    ``first_tx_id`` and ``tx_id_step`` MUST be positive integers (booleans are
    rejected). The identifier-space rule (odd sequence for the standard
    client, even sequence for the standard server) is enforced by caller
    configuration, not by this class.
    """

    def __init__(
        self,
        logger: logging.Logger,
        *,
        first_tx_id: int = 1,
        tx_id_step: int = 1,
    ) -> None:
        _require_positive_int("first_tx_id", first_tx_id)
        _require_positive_int("tx_id_step", tx_id_step)
        self._logger = logger
        self._tx_id_step = tx_id_step
        self._next_tx_id = first_tx_id
        self._lock = threading.Lock()
        self._pending: dict[int, PendingTransaction] = {}

    def next_tx_id(self) -> int:
        """Return the next transaction id, advancing the sequence by ``tx_id_step``."""
        with self._lock:
            tx_id = self._next_tx_id
            self._next_tx_id += self._tx_id_step
            return tx_id

    def register(self, epoch: int, tx_id: int) -> PendingTransaction:
        """Register a new pending transaction for ``tx_id`` under ``epoch``.

        Raises:
            RuntimeError: If ``tx_id`` is already registered. The incumbent
                pending record is never replaced or mutated.
        """
        with self._lock:
            if tx_id in self._pending:
                raise RuntimeError(f"transaction id {tx_id!r} is already registered")
            pending = PendingTransaction(epoch=epoch, tx_id=tx_id)
            self._pending[tx_id] = pending
            return pending

    def discard(self, tx_id: int) -> None:
        """Remove a pending transaction if present. Idempotent."""
        with self._lock:
            self._pending.pop(tx_id, None)

    def wait_ack(self, tx_id: int, timeout: float | None = None) -> AckStatus | None:
        """Block for ``tx_id``'s ACK stage to settle, up to ``timeout`` seconds.

        Returns ``None`` for an unknown identifier. The lock is never held
        across the event wait. Immediately after the wait returns, the lock is
        re-acquired: this acquisition is the linearization point versus
        routing (chunk 06), so a racing settlement lands wholly before or
        after it — an unresolved stage found here settles as
        :attr:`AckStatus.TIMED_OUT`, and a stage already settled by that point
        is returned unchanged.
        """
        _require_valid_timeout(timeout)
        with self._lock:
            pending = self._pending.get(tx_id)
        if pending is None:
            return None
        pending.ack_event.wait(timeout)
        with self._lock:
            current = self._pending.get(tx_id)
            if current is None:
                return None
            if current.ack_status is None:
                current.ack_status = AckStatus.TIMED_OUT
            return current.ack_status

    def wait_completion(self, tx_id: int, timeout: float | None = None) -> CompletionStatus | None:
        """Block for ``tx_id``'s completion stage to settle, up to ``timeout`` seconds.

        Mirrors :meth:`wait_ack`'s race-safe settlement for the completion stage.
        """
        _require_valid_timeout(timeout)
        with self._lock:
            pending = self._pending.get(tx_id)
        if pending is None:
            return None
        pending.done_event.wait(timeout)
        with self._lock:
            current = self._pending.get(tx_id)
            if current is None:
                return None
            if current.completion_status is None:
                current.completion_status = CompletionStatus.TIMED_OUT
            return current.completion_status
