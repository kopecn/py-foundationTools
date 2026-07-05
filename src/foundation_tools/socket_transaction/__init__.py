"""
Socket Transaction Stack — the stream-transport counterpart to the process family.

Layers as: ``SocketTransact`` (Layer 4 facade) over a transaction router
(tx_id correlation) over framing codecs (``DataModelHelper`` wire
serialization) over ``SocketByteTransport``
(``foundation_abc.PeripheralByteTransport``) over asyncio streams.

See ``.claude/specs/socketTransact.md`` and
``.claude/specs/transport_transaction_architecture.md`` (Stream-Transport Family)
for the full contract. Status: ``SocketByteTransport`` (Layer 1) implemented;
codecs, router, and facade planned.
"""

from foundation_tools.socket_transaction.socket_byte_transport import SocketByteTransport

__all__ = [
    "SocketByteTransport",
]
