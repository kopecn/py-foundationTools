"""
Shared threaded transacting engine.

Composes an already-constructed epoch-aware socket transport (a
``SocketHandler`` or role subclass), an injected ``TransactionCodec``, and a
role-configured ``TransactionCore`` into the receive pipeline (decode, route,
dispatch) and the synchronous ``send_transaction``/``send_broadcast``
operations shared by the client and server facades
(``TransactingSocketHandlerClient``/``TransactingSocketHandlerServer``). This
module never constructs or owns a socket itself -- the transport is supplied
fully formed by its caller.

Contract: ``.claude/specs/transactingSocketHandlers.md`` ("Composition and
roles", "Receive pipeline", "Synchronous transaction operation", and
"Lifecycle coupling" sections). ``TransactingSocketHandler`` itself is not a
package export; ``InboundTransaction``, also defined in this module, is
exported directly, and ``TransactingSocketHandlerClient``/
``TransactingSocketHandlerServer`` compose this engine as their public
facades.
"""

import logging
import math
import threading
from collections.abc import Callable
from typing import Protocol

from foundation_tools.socket_transaction.socket_handler import ConnectionObserver, EpochSendStatus
from foundation_tools.socket_transaction.transaction_codecs import TransactionCodec
from foundation_tools.socket_transaction.transaction_core import TransactionCore
from foundation_tools.socket_transaction.transaction_models import (
    AckStatus,
    CompletionStatus,
    SendStatus,
    TransactionFrame,
    TransactionOutcome,
)
from foundationTypes.data_model_helper import DataModelHelper

_RESERVED_REPLY_TYPES = frozenset({"ack", "res", "err", "evt"})


class TransactionTransport(Protocol):
    """Structural surface the engine needs from its socket transport.

    Deliberately narrower than the full ``SocketHandler`` public surface: the
    engine never connects, listens, or disconnects the transport it is given
    -- it only snapshots the active epoch, sends within an epoch, sends a
    fire-and-forget broadcast, and registers itself as the transport's
    internal connection observer. Any ``SocketHandler`` (or role subclass)
    satisfies this structurally.
    """

    def snapshot_active_epoch(self) -> int | None: ...

    def send_for_epoch(self, epoch: int, data: bytes) -> EpochSendStatus: ...

    def send(self, data: bytes) -> bool: ...

    def set_connection_observer(self, observer: ConnectionObserver | None) -> None: ...


def _validate_timeout(timeout: float | None) -> None:
    """Raise ``ValueError`` unless ``timeout`` is ``None`` or a finite, non-negative number.

    Mirrors ``TransactionCore``'s own (private) timeout validation exactly,
    including not special-casing ``bool`` -- neither the accepted
    ``threadedTransactionProtocol.md``/``transactingSocketHandlers.md`` specs
    nor the existing core implementation reject a boolean timeout, unlike the
    codec's `tx_id`/`code` fields, which explicitly do.
    """
    if timeout is None:
        return
    if not isinstance(timeout, int | float) or not math.isfinite(timeout) or timeout < 0:
        raise ValueError(f"timeout must be None or a finite non-negative number, got {timeout!r}")


class InboundTransaction:
    """Epoch-bound responder for one remote-initiated request frame.

    Constructed by :class:`TransactingSocketHandler` for every frame routed
    to the application-level inbound handler and handed to that handler.
    ``reply`` is bound to the epoch that was active when the inbound frame
    was routed: a later replacement connection can never receive this
    responder's frames, even if the callback retains the instance.
    """

    def __init__(
        self, frame: TransactionFrame, epoch: int, engine: "TransactingSocketHandler"
    ) -> None:
        self.frame = frame
        self._epoch = epoch
        self._engine = engine

    def reply(
        self,
        msg_type: str,
        code: int,
        payload: DataModelHelper | bytes | str | None = None,
    ) -> bool:
        """Encode and send a reply on the originating epoch.

        Raises:
            ValueError: If ``msg_type`` is not one of ``ack``, ``res``,
                ``err``, or ``evt`` -- raised before any encoding is
                attempted.

        Returns:
            ``True`` only when ``EpochSendStatus.SENT`` is returned for the
            originating epoch; ``False`` (with no bytes emitted) if that
            epoch is no longer the active connection.
        """
        if msg_type not in _RESERVED_REPLY_TYPES:
            raise ValueError(
                f"reply msg_type must be one of {sorted(_RESERVED_REPLY_TYPES)}, got {msg_type!r}"
            )
        wire = self._engine._encode(self.frame.tx_id, msg_type, code, payload)
        status = self._engine._transport.send_for_epoch(self._epoch, wire)
        return status is EpochSendStatus.SENT


class TransactingSocketHandler:
    """Internal shared synchronous transacting engine.

    Receives an already-constructed transport, codec, and role-configured
    core; it never owns or creates another socket. Registers itself as the
    transport's internal connection observer at construction time -- the
    caller MUST NOT separately register another observer on the same
    transport instance.

    One codec lock serializes each individual ``encode``/``decode`` call. It
    is always released before routing a decoded frame or invoking any
    application callback, so an inbound responder's own encode call cannot
    reenter and deadlock on the same lock.
    """

    def __init__(
        self,
        logger: logging.Logger,
        transport: TransactionTransport,
        codec: TransactionCodec,
        core: TransactionCore,
    ) -> None:
        self._logger = logger
        self._transport = transport
        self._codec = codec
        self._core = core

        self._codec_lock = threading.Lock()
        self._callback_lock = threading.Lock()
        self._string_handler: Callable[[str], None] | None = None
        self._inbound_handler: Callable[[InboundTransaction], None] | None = None

        self._core.set_inbound_transaction_handler(self._on_inbound_frame)
        self._transport.set_connection_observer(self)

    # -- public transaction surface (transactingSocketHandlers.md) ----------

    def send_transaction(
        self,
        msg_type: str,
        code: int,
        payload: DataModelHelper | bytes | str | None = None,
        wait_ack: bool = True,
        wait_result: bool = False,
        timeout: float | None = None,
    ) -> TransactionOutcome:
        """Perform one synchronous transaction; see the "Transaction recipe".

        ``timeout`` is validated before any identifier is allocated. Every
        valid call consumes an identifier, including while disconnected. A
        disconnected call returns a directly constructed ``NOT_CONNECTED``
        outcome without registering pending state. Otherwise the active
        epoch is snapshotted, pending state is registered under it before
        encoding or sending (so an immediate peer reply cannot outrun
        correlation), the frame is sent only if that epoch remains active,
        requested waits settle independently, and the outcome is produced
        through the core's atomic finalize-and-remove operation on every
        path -- including an exception, which discards the pending entry
        instead.
        """
        _validate_timeout(timeout)
        tx_id = self._core.next_tx_id()
        epoch = self._transport.snapshot_active_epoch()
        if epoch is None:
            return self._not_connected_outcome(tx_id, wait_ack, wait_result)

        self._core.register(epoch, tx_id)
        try:
            wire = self._encode(tx_id, msg_type, code, payload)
            send_status = self._transport.send_for_epoch(epoch, wire)
            resolved_send_status = self._settle_requested_waits(
                epoch, tx_id, send_status, wait_ack, wait_result, timeout
            )
            outcome = self._core.finalize_outcome(
                tx_id,
                resolved_send_status,
                ack_requested=wait_ack,
                completion_requested=wait_result,
            )
            if outcome is None:  # pragma: no cover - defensive: tx_id was just registered above
                raise RuntimeError(f"transaction {tx_id!r} vanished before finalization")
            return outcome
        except BaseException:
            self._core.discard(tx_id)
            raise

    def send_broadcast(
        self, payload: DataModelHelper | bytes | str | None = None, code: int = 0
    ) -> bool:
        """Encode and send a fire-and-forget broadcast on the current epoch.

        Uses ``tx_id=-1`` and ``msg_type="evt"`` without registering any
        pending state. On a single-active-client server this targets only
        the active client, by construction of the underlying transport.
        """
        wire = self._encode(-1, "evt", code, payload)
        return self._transport.send(wire)

    def set_string_message_handler(self, handler: Callable[[str], None] | None) -> None:
        """Set (or clear, with ``None``) the raw-token application handler.

        Invoked from the receive pipeline with each token's original text,
        after codec decoding and routing have both been attempted.
        """
        with self._callback_lock:
            self._string_handler = handler

    def set_broadcast_event_handler(
        self, handler: Callable[[TransactionFrame], None] | None
    ) -> None:
        """Set (or clear, with ``None``) the unsolicited broadcast handler."""
        self._core.set_broadcast_event_handler(handler)

    def set_inbound_transaction_handler(
        self, handler: Callable[[InboundTransaction], None] | None
    ) -> None:
        """Set (or clear, with ``None``) the remote-request handler.

        Invoked with an epoch-bound :class:`InboundTransaction` for every
        application-defined request frame the core routes as inbound.
        """
        with self._callback_lock:
            self._inbound_handler = handler

    # -- ConnectionObserver protocol (socket_handler.py) ---------------------

    def on_string_token(self, epoch: int, token: str) -> None:
        """Decode, route, then deliver one complete epoch-tagged token.

        Codec decoding is attempted first, under the codec lock only for the
        duration of the ``decode`` call itself. A ``ValueError`` decode
        failure is logged, transaction routing is skipped, and the original
        token still reaches the application string handler unchanged. A
        successfully decoded frame is routed through the core for this same
        epoch before the string handler runs. Both decode failure and
        application-handler failure are contained here and never escape the
        receive thread.
        """
        frame: TransactionFrame | None
        try:
            frame = self._decode(token)
        except ValueError as error:
            self._logger.warning(
                "transacting engine: failed to decode token on epoch %s: %s", epoch, error
            )
            frame = None

        if frame is not None:
            self._core.route(epoch, frame)

        with self._callback_lock:
            handler = self._string_handler
        if handler is None:
            return
        try:
            handler(token)
        except Exception:
            self._logger.exception("transacting engine: string message handler raised")

    def on_epoch_closed(self, epoch: int, cause: str) -> None:
        """Fail only the closing epoch's still-unresolved pending transactions."""
        self._core.fail_epoch(epoch, cause)

    # -- internal helpers -----------------------------------------------------

    def _encode(
        self,
        tx_id: int,
        msg_type: str,
        code: int,
        payload: DataModelHelper | bytes | str | None,
    ) -> bytes:
        with self._codec_lock:
            return self._codec.encode(tx_id, msg_type, code, payload)

    def _decode(self, token: str) -> TransactionFrame:
        with self._codec_lock:
            return self._codec.decode(token)

    def _on_inbound_frame(self, epoch: int, frame: TransactionFrame) -> None:
        """Adapter registered with the core; constructs the responder handed
        to the application inbound handler. The core already isolates this
        callback's exceptions (including one raised by the application
        handler it invokes) and contains them without disturbing routing."""
        with self._callback_lock:
            handler = self._inbound_handler
        if handler is None:
            return
        handler(InboundTransaction(frame, epoch, self))

    def _settle_requested_waits(
        self,
        epoch: int,
        tx_id: int,
        send_status: EpochSendStatus,
        wait_ack: bool,
        wait_result: bool,
        timeout: float | None,
    ) -> SendStatus:
        """Wait for requested stages on a successful send, or settle them via
        epoch failure on a failed one, and return the resulting ``SendStatus``.

        A failed send never waits. Calling ``fail_epoch`` here (rather than
        only relying on the observer notification a socket-level failure may
        already have triggered) closes a narrow registration race: if the
        epoch died between this call's own epoch snapshot and its
        registration, the transport's own close notification could have run
        before this transaction existed to be settled by it. ``fail_epoch``
        is idempotent per entry, so calling it again here is always safe and
        is the only path that correctly settles that race's pending entry as
        ``CONNECTION_CLOSED`` instead of leaving it to fall back to
        ``NOT_REQUESTED`` in ``finalize_outcome``.
        """
        if send_status is not EpochSendStatus.SENT:
            self._core.fail_epoch(epoch, f"transaction send failed: {send_status.name}")
            return SendStatus.FAILED

        if wait_ack:
            self._core.wait_ack(tx_id, timeout)
        if wait_result:
            self._core.wait_completion(tx_id, timeout)
        return SendStatus.SENT

    @staticmethod
    def _not_connected_outcome(tx_id: int, wait_ack: bool, wait_result: bool) -> TransactionOutcome:
        """Directly construct the unregistered outcome for a disconnected call."""
        explanation = "not connected"
        return TransactionOutcome(
            tx_id=tx_id,
            send_status=SendStatus.NOT_CONNECTED,
            ack_status=AckStatus.CONNECTION_CLOSED if wait_ack else AckStatus.NOT_REQUESTED,
            completion_status=(
                CompletionStatus.CONNECTION_CLOSED
                if wait_result
                else CompletionStatus.NOT_REQUESTED
            ),
            result=None,
            ack_error=explanation if wait_ack else None,
            completion_error=explanation if wait_result else None,
        )
