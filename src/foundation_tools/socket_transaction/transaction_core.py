"""
Threaded transaction core — state and routing (Action Plan 25, chunks 05-06).

Implements the internal, non-exported ``PendingTransaction`` mutable state and
the full ``TransactionCore``: transaction id sequencing, epoch-bound
registration, duplicate rejection, idempotent discard, race-safe ACK/
completion waits (chunk 05), plus frame routing, epoch-scoped failure,
isolated broadcast/inbound callbacks, and atomic outcome finalization
(chunk 06).

Contract: ``.claude/specs/threadedTransactionProtocol.md`` ("Pending
transaction", "Transaction core", and "Routing" sections). This module is not
exported from the package ``__init__.py``.
"""

import logging
import math
import threading
from collections.abc import Callable
from dataclasses import dataclass, field

from foundation_tools.socket_transaction.transaction_models import (
    AckStatus,
    CompletionStatus,
    SendStatus,
    TransactionFrame,
    TransactionOutcome,
)

_CONTROL_MESSAGE_TYPES = frozenset({"ack", "res", "err", "evt"})


def _payload_text(payload: bytes | str | dict[str, object] | None) -> str:
    """Render a non-``None`` frame payload as text for a diagnostic message.

    ``bytes`` is decoded as UTF-8 with replacement rather than embedded via
    ``str()``/an f-string, which would otherwise render its ``repr`` (e.g.
    ``"b'abc'"``) instead of the payload's text.
    """
    if isinstance(payload, bytes):
        return payload.decode("utf-8", errors="replace")
    return str(payload)


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
        self._broadcast_handler: Callable[[TransactionFrame], None] | None = None
        self._inbound_handler: Callable[[int, TransactionFrame], None] | None = None

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

    def set_broadcast_event_handler(
        self, handler: Callable[[TransactionFrame], None] | None
    ) -> None:
        """Set (or clear, with ``None``) the handler invoked for broadcast ``evt`` frames."""
        with self._lock:
            self._broadcast_handler = handler

    def set_inbound_transaction_handler(
        self, handler: Callable[[int, TransactionFrame], None] | None
    ) -> None:
        """Set (or clear, with ``None``) the handler invoked for application-defined
        request frames with no owning pending transaction."""
        with self._lock:
            self._inbound_handler = handler

    def route(self, epoch: int, frame: TransactionFrame) -> None:
        """Route one inbound frame per the routing table.

        State mutation always finishes under the transaction lock before any
        callback runs; the selected callback (if any) is invoked after the
        lock is released, and its exceptions are logged and contained so
        routing stays usable for a later frame.
        """
        if frame.msg_type == "evt" and frame.tx_id < 0:
            with self._lock:
                broadcast_handler = self._broadcast_handler
            self._invoke_broadcast(broadcast_handler, frame)
            return

        inbound_handler: Callable[[int, TransactionFrame], None] | None = None
        with self._lock:
            pending = self._pending.get(frame.tx_id)
            if pending is None or pending.epoch != epoch:
                if frame.msg_type in _CONTROL_MESSAGE_TYPES:
                    self._logger.warning(
                        "dropping orphan %s frame for tx_id=%s epoch=%s "
                        "(no matching pending transaction)",
                        frame.msg_type,
                        frame.tx_id,
                        epoch,
                    )
                else:
                    inbound_handler = self._inbound_handler
            elif frame.msg_type == "ack":
                self._route_ack(pending, frame)
            elif frame.msg_type == "res":
                self._route_res(pending, frame)
            elif frame.msg_type == "evt":
                self._route_evt(pending, frame)
            elif frame.msg_type == "err":
                self._route_err(pending, frame)
            else:
                inbound_handler = self._inbound_handler

        if inbound_handler is not None:
            self._invoke_inbound(inbound_handler, epoch, frame)

    def _route_ack(self, pending: PendingTransaction, frame: TransactionFrame) -> None:
        """Settle the ACK stage (and, on failure, an unresolved completion stage).

        Must be called while holding ``self._lock``. A second ACK arriving
        after the ACK stage has already settled is normally a losing/late
        frame: logged and ignored rather than overwriting the first
        settlement. The one exception is a failed ACK arriving after the ACK
        wait already timed out (``AckStatus.TIMED_OUT``): ACK and completion
        are independent stages, so that late failure must still be able to
        settle an independently unresolved completion stage as ``ERROR`` --
        without ever overwriting ``TIMED_OUT`` itself, and without touching
        completion if a result, protocol error, completion timeout, or
        connection closure already settled it first. A late *successful* ACK
        after timeout stays non-terminal for completion either way.
        """
        if pending.ack_status is None:
            if frame.code == 0:
                pending.acked = True
                pending.ack_status = AckStatus.ACKNOWLEDGED
                pending.ack_event.set()
                return

            error_text = self._failed_ack_error_text(frame)
            pending.ack_status = AckStatus.REJECTED
            pending.ack_error = error_text
            pending.ack_event.set()
            self._settle_completion_from_failed_ack(pending, error_text)
            return

        if pending.ack_status is AckStatus.TIMED_OUT and frame.code != 0:
            self._settle_completion_from_failed_ack(pending, self._failed_ack_error_text(frame))
            return

        self._logger.debug(
            "dropping late/duplicate ack for tx_id=%s (ack already settled)", frame.tx_id
        )

    @staticmethod
    def _failed_ack_error_text(frame: TransactionFrame) -> str:
        """Build the exact failed-ACK diagnostic text for ``frame``."""
        return (
            f"ack code {frame.code}: {_payload_text(frame.payload)}"
            if frame.payload is not None
            else f"ack code {frame.code}"
        )

    def _settle_completion_from_failed_ack(
        self, pending: PendingTransaction, error_text: str
    ) -> None:
        """Settle completion as ``ERROR`` from a failed ACK, only while
        completion remains unresolved. Must be called while holding
        ``self._lock``. Never overwrites a result/error/timeout/connection-
        closed status that already settled completion first.
        """
        if pending.completion_status is not None:
            self._logger.debug(
                "dropping late failed-ack completion settlement for tx_id=%s "
                "(completion already settled)",
                pending.tx_id,
            )
            return
        pending.completion_status = CompletionStatus.ERROR
        pending.completion_error = error_text
        pending.done_event.set()

    def _route_res(self, pending: PendingTransaction, frame: TransactionFrame) -> None:
        """Settle the completion stage with a result. Must be called under ``self._lock``."""
        if pending.completion_status is not None:
            self._logger.debug(
                "dropping late/duplicate res for tx_id=%s (completion already settled)",
                frame.tx_id,
            )
            return
        pending.result = frame
        pending.completion_status = CompletionStatus.RESULT
        pending.done_event.set()

    def _route_evt(self, pending: PendingTransaction, frame: TransactionFrame) -> None:
        """Append a transaction event. Must be called under ``self._lock``.

        Events are appended only while completion is unresolved; a late event
        arriving after completion has settled is logged and dropped rather
        than appended, and never signals completion.
        """
        if pending.completion_status is not None:
            self._logger.debug(
                "dropping late event for tx_id=%s (completion already settled)", frame.tx_id
            )
            return
        pending.events.append(frame)

    def _route_err(self, pending: PendingTransaction, frame: TransactionFrame) -> None:
        """Settle the completion stage with an error. Must be called under ``self._lock``."""
        if pending.completion_status is not None:
            self._logger.debug(
                "dropping late/duplicate err for tx_id=%s (completion already settled)",
                frame.tx_id,
            )
            return
        error_text = (
            _payload_text(frame.payload)
            if frame.payload is not None
            else f"error code {frame.code}"
        )
        pending.completion_status = CompletionStatus.ERROR
        pending.completion_error = error_text
        pending.done_event.set()

    def _invoke_broadcast(
        self,
        handler: Callable[[TransactionFrame], None] | None,
        frame: TransactionFrame,
    ) -> None:
        """Invoke the broadcast handler outside the lock; exceptions are logged and contained."""
        if handler is None:
            return
        try:
            handler(frame)
        except Exception:
            self._logger.exception("broadcast event handler raised for tx_id=%s", frame.tx_id)

    def _invoke_inbound(
        self,
        handler: Callable[[int, TransactionFrame], None],
        epoch: int,
        frame: TransactionFrame,
    ) -> None:
        """Invoke the inbound handler outside the lock; exceptions are logged and contained."""
        try:
            handler(epoch, frame)
        except Exception:
            self._logger.exception(
                "inbound transaction handler raised for tx_id=%s epoch=%s", frame.tx_id, epoch
            )

    def fail_epoch(self, epoch: int, error: str) -> None:
        """Settle every still-unresolved stage belonging to ``epoch`` as
        ``CONNECTION_CLOSED``, signal both events on each affected entry, and
        leave every entry registered (removal is ``finalize_outcome``'s job).

        A stage already settled by another event (an ACK, a result, an
        error, or a prior timeout) is left untouched; only its event is
        (re-)signaled, which is a no-op if it was already set.
        """
        with self._lock:
            for pending in self._pending.values():
                if pending.epoch != epoch:
                    continue
                if pending.ack_status is None:
                    pending.ack_status = AckStatus.CONNECTION_CLOSED
                    pending.ack_error = error
                pending.ack_event.set()
                if pending.completion_status is None:
                    pending.completion_status = CompletionStatus.CONNECTION_CLOSED
                    pending.completion_error = error
                pending.done_event.set()

    def finalize_outcome(
        self,
        tx_id: int,
        send_status: SendStatus,
        *,
        ack_requested: bool,
        completion_requested: bool,
    ) -> TransactionOutcome | None:
        """Snapshot ``tx_id``'s immutable outcome and remove its pending entry,
        in one lock acquisition. Returns ``None`` for an unknown identifier.

        Unrequested stages map to ``NOT_REQUESTED``. Once this removes the
        entry, a later control frame for ``tx_id`` follows orphan-frame
        routing.
        """
        with self._lock:
            pending = self._pending.pop(tx_id, None)
            if pending is None:
                return None

            ack_status = AckStatus.NOT_REQUESTED
            if ack_requested:
                ack_status = pending.ack_status or AckStatus.NOT_REQUESTED

            completion_status = CompletionStatus.NOT_REQUESTED
            if completion_requested:
                completion_status = pending.completion_status or CompletionStatus.NOT_REQUESTED

            return TransactionOutcome(
                tx_id=tx_id,
                send_status=send_status,
                ack_status=ack_status,
                completion_status=completion_status,
                result=pending.result,
                ack_error=pending.ack_error,
                completion_error=pending.completion_error,
                events=tuple(pending.events),
            )
