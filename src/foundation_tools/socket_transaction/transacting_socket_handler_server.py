"""
TransactingSocketHandlerServer -- public synchronous transacting server role
(Action Plan 25, chunk 15).

Thin composition of ``SocketHandlerServer`` (chunk 11, the sole listener and
socket owner), a ``TransactionCore`` configured with the standard even server
transaction-identifier sequence (``2, 4, 6, ...``, never reset by
replacement), and the shared ``TransactingSocketHandler`` engine (chunk 13,
the sole codec-lock owner) built over both. This module owns no socket,
listener, codec-encoding, or transaction-state logic of its own -- it only
builds the three collaborators once and delegates every public operation to
them unchanged, mirroring ``TransactingSocketHandlerClient`` (chunk 14) for
the server role.

Contract: ``.claude/specs/transactingSocketHandlers.md`` ("Composition and
roles" section, server facade).

Deliberately not a ``foundation_abc.PeripheralByteTransport`` -- that ABC is
fully asynchronous and out of scope for this synchronous, threaded facade.
No coroutine or async context-manager method is defined here.
"""

from __future__ import annotations

import logging
from collections.abc import Callable

from foundation_tools.socket_transaction.socket_handler_server import SocketHandlerServer
from foundation_tools.socket_transaction.transacting_socket_handler import (
    InboundTransaction,
    TransactingSocketHandler,
)
from foundation_tools.socket_transaction.transaction_codecs import TransactionCodec
from foundation_tools.socket_transaction.transaction_core import TransactionCore
from foundation_tools.socket_transaction.transaction_models import (
    TransactionFrame,
    TransactionOutcome,
)
from foundationTypes.data_model_helper import DataModelHelper

# The standard server identifier sequence per
# ``.claude/specs/transactingSocketHandlers.md#composition-and-roles``: even
# ids starting at 2, never reset across client replacement because the core
# (and its internal sequence counter) is constructed exactly once, here.
_SERVER_FIRST_TX_ID = 2
_SERVER_TX_ID_STEP = 2


class TransactingSocketHandlerServer:
    """Public synchronous transacting server facade.

    Builds exactly one ``SocketHandlerServer``, one even-sequence
    ``TransactionCore``, and one ``TransactingSocketHandler`` engine over
    them at construction time, then exposes the contained server's listener
    and single-active-client lifecycle plus the shared engine's transaction
    surface unchanged. Composition (not inheritance from
    ``SocketHandlerServer``) keeps socket and listener ownership singular:
    this class never touches a socket directly and starts no additional
    worker thread of its own.
    """

    def __init__(
        self,
        logger: logging.Logger,
        codec: TransactionCodec,
        *,
        connection_admission_handler: Callable[[tuple[str, int]], bool] | None = None,
        join_timeout: float = 1.0,
        accept_poll_interval: float = 0.2,
    ) -> None:
        self._socket = SocketHandlerServer(
            logger,
            connection_admission_handler=connection_admission_handler,
            string_delimiter=codec.delimiter,
            join_timeout=join_timeout,
            accept_poll_interval=accept_poll_interval,
        )
        self._core = TransactionCore(
            logger, first_tx_id=_SERVER_FIRST_TX_ID, tx_id_step=_SERVER_TX_ID_STEP
        )
        self._engine = TransactingSocketHandler(logger, self._socket, codec, self._core)

    # -- listener/client lifecycle, delegated to the contained SocketHandlerServer -

    @property
    def is_connected(self) -> bool:
        return self._socket.is_connected

    @property
    def active_peer(self) -> tuple[str, int] | None:
        return self._socket.active_peer

    @property
    def is_listening(self) -> bool:
        return self._socket.is_listening

    @property
    def listening_address(self) -> tuple[str, int] | None:
        return self._socket.listening_address

    def listen(self, port: int) -> None:
        self._socket.listen(port)

    def wait_for_connection(self, timeout: float | None = None) -> bool:
        return self._socket.wait_for_connection(timeout)

    def disconnect(self) -> None:
        self._socket.disconnect()

    def kick(self) -> None:
        self._socket.kick()

    def stop(self) -> None:
        self._socket.stop()

    # -- transaction surface, delegated to the shared engine -------------------

    def send_transaction(
        self,
        msg_type: str,
        code: int,
        payload: DataModelHelper | bytes | str | None = None,
        wait_ack: bool = True,
        wait_result: bool = False,
        timeout: float | None = None,
    ) -> TransactionOutcome:
        return self._engine.send_transaction(
            msg_type,
            code,
            payload,
            wait_ack=wait_ack,
            wait_result=wait_result,
            timeout=timeout,
        )

    def send_broadcast(
        self, payload: DataModelHelper | bytes | str | None = None, code: int = 0
    ) -> bool:
        return self._engine.send_broadcast(payload, code)

    def set_string_message_handler(self, handler: Callable[[str], None] | None) -> None:
        self._engine.set_string_message_handler(handler)

    def set_broadcast_event_handler(
        self, handler: Callable[[TransactionFrame], None] | None
    ) -> None:
        self._engine.set_broadcast_event_handler(handler)

    def set_inbound_transaction_handler(
        self, handler: Callable[[InboundTransaction], None] | None
    ) -> None:
        self._engine.set_inbound_transaction_handler(handler)
