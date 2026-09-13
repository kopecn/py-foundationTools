"""
Threaded Socket Transaction Stack -- the synchronous, standard-library
counterpart to the process (CLI) transaction family.

Layers as: ``TransactingSocketHandlerClient`` / ``TransactingSocketHandlerServer``
(the transacting facades) over ``TransactionCore`` (identifiers, pending
state, routing) and a pluggable ``TransactionCodec`` (``JsonTransactionCodec``
or ``AngleBracketTransactionCodec``) over ``SocketHandlerClient`` /
``SocketHandlerServer`` (connection lifecycle, receive/accept threads) over
``SocketHandler`` (epoch-bound socket ownership) over ``socket.socket`` and
``threading``. ``BinaryFramedSocketHandlerClient`` is a parallel transport
specialization for pluggable binary framing.

The package uses only ``socket`` and ``threading`` -- it has no event-loop
dependency and exposes no coroutine-based or compatibility facade.

See ``.claude/specs/threadedSocketTransaction.md`` (architecture and public
surface), ``.claude/specs/threadedSocketTransport.md`` (transport layer),
``.claude/specs/threadedTransactionProtocol.md`` (protocol layer),
``.claude/specs/transactingSocketHandlers.md`` (transacting facades), and
``.claude/specs/transport_transaction_architecture.md`` (Stream-Transport
Family) for the full contract.
"""

from foundation_tools.socket_transaction.binary_framed_socket_handler_client import (
    BinaryFramedSocketHandlerClient,
)
from foundation_tools.socket_transaction.socket_handler import SocketHandler
from foundation_tools.socket_transaction.socket_handler_client import SocketHandlerClient
from foundation_tools.socket_transaction.socket_handler_server import SocketHandlerServer
from foundation_tools.socket_transaction.transacting_socket_handler import InboundTransaction
from foundation_tools.socket_transaction.transacting_socket_handler_client import (
    TransactingSocketHandlerClient,
)
from foundation_tools.socket_transaction.transacting_socket_handler_server import (
    TransactingSocketHandlerServer,
)
from foundation_tools.socket_transaction.transaction_codecs import (
    AngleBracketTransactionCodec,
    JsonTransactionCodec,
    TransactionCodec,
)
from foundation_tools.socket_transaction.transaction_models import (
    AckStatus,
    CompletionStatus,
    SendStatus,
    TransactionFrame,
    TransactionOutcome,
)

__all__ = [
    "AckStatus",
    "AngleBracketTransactionCodec",
    "BinaryFramedSocketHandlerClient",
    "CompletionStatus",
    "InboundTransaction",
    "JsonTransactionCodec",
    "SendStatus",
    "SocketHandler",
    "SocketHandlerClient",
    "SocketHandlerServer",
    "TransactingSocketHandlerClient",
    "TransactingSocketHandlerServer",
    "TransactionCodec",
    "TransactionFrame",
    "TransactionOutcome",
]
