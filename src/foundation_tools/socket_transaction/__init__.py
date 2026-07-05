"""
Socket Transaction Stack — the stream-transport counterpart to the process family.

Layers as: ``SocketTransact`` (Layer 4 facade) over a transaction router
(tx_id correlation) over framing codecs (``DataModelHelper`` wire
serialization) over ``SocketByteTransport``
(``foundation_abc.PeripheralByteTransport``) over asyncio streams.

See ``.claude/specs/socketTransact.md`` and
``.claude/specs/transport_transaction_architecture.md`` (Stream-Transport Family)
for the full contract. Status: ``SocketByteTransport`` (Layer 1), the framing
codecs (Layer 2), ``TransactionRouter`` (Layer 3), and ``SocketTransact``
(Layer 4, client facade) implemented; server facade planned.
"""

from foundation_tools.socket_transaction.framing_codecs import (
    DelimiterCodec,
    FramingCodec,
    LengthPrefixedCodec,
)
from foundation_tools.socket_transaction.socket_byte_transport import SocketByteTransport
from foundation_tools.socket_transaction.socketTransact import (
    SocketTransact,
    SocketTransactResult,
    SocketTransactResultModel,
)
from foundation_tools.socket_transaction.transaction_router import (
    ConnectionClosedError,
    TransactionRouter,
)

__all__ = [
    "ConnectionClosedError",
    "DelimiterCodec",
    "FramingCodec",
    "LengthPrefixedCodec",
    "SocketByteTransport",
    "SocketTransact",
    "SocketTransactResult",
    "SocketTransactResultModel",
    "TransactionRouter",
]
