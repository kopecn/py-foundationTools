"""
TransactingSocketHandlerClient -- public synchronous transacting client role
(Action Plan 25, chunk 14).

Thin composition of ``SocketHandlerClient`` (chunk 09, the sole socket
owner), a ``TransactionCore`` configured with the standard odd client
transaction-identifier sequence (``1, 3, 5, ...``, never reset by
reconnect), and the shared ``TransactingSocketHandler`` engine (chunk 13,
the sole codec-lock owner) built over both. This module owns no socket,
codec-encoding, or transaction-state logic of its own -- it only builds the
three collaborators once and delegates every public operation to them
unchanged.

Contract: ``.claude/specs/transactingSocketHandlers.md`` ("Composition and
roles" section, client facade).

Deliberately not a ``foundation_abc.PeripheralByteTransport`` -- that ABC is
fully asynchronous and out of scope for this synchronous, threaded facade.
No coroutine or async context-manager method is defined here.
"""

from __future__ import annotations

import logging
from collections.abc import Callable

from foundation_tools.socket_transaction.socket_handler_client import SocketHandlerClient
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

# The standard client identifier sequence per
# ``.claude/specs/transactingSocketHandlers.md#composition-and-roles``: odd
# ids starting at 1, never reset across disconnect/reconnect because the
# core (and its internal sequence counter) is constructed exactly once, here.
_CLIENT_FIRST_TX_ID = 1
_CLIENT_TX_ID_STEP = 2


class TransactingSocketHandlerClient:
    """Public synchronous transacting client facade.

    Builds exactly one ``SocketHandlerClient``, one odd-sequence
    ``TransactionCore``, and one ``TransactingSocketHandler`` engine over
    them at construction time, then exposes the contained transport's
    connection lifecycle and the shared engine's transaction surface
    unchanged. Composition (not inheritance from ``SocketHandlerClient``)
    keeps socket ownership singular: this class never touches a socket
    directly.
    """

    def __init__(
        self,
        logger: logging.Logger,
        codec: TransactionCodec,
        *,
        join_timeout: float = 1.0,
    ) -> None:
        self._socket = SocketHandlerClient(
            logger, string_delimiter=codec.delimiter, join_timeout=join_timeout
        )
        self._core = TransactionCore(
            logger, first_tx_id=_CLIENT_FIRST_TX_ID, tx_id_step=_CLIENT_TX_ID_STEP
        )
        self._engine = TransactingSocketHandler(logger, self._socket, codec, self._core)

    # -- transport lifecycle, delegated to the contained SocketHandlerClient -

    @property
    def is_connected(self) -> bool:
        return self._socket.is_connected

    def connect(self, host: str, port: int, timeout: float | None = 1.0) -> None:
        self._socket.connect(host, port, timeout)

    def disconnect(self) -> None:
        self._socket.disconnect()

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
