"""
Tests for the Action Plan 01 package restructure: subpackage skeletons and the
cli_transaction public re-export.
"""


def test_cli_transaction_public_import() -> None:
    from foundation_tools.cli_transaction import (
        CLITransact,
        CLITransactResult,
        CLITransactResultModel,
    )

    assert CLITransact is not None
    assert CLITransactResult is not None
    assert CLITransactResultModel is not None


def test_subpackages_importable() -> None:
    import foundation_tools.builders
    import foundation_tools.policies
    import foundation_tools.socket_transaction

    assert foundation_tools.builders is not None
    assert foundation_tools.policies is not None
    assert foundation_tools.socket_transaction is not None


def test_socket_transaction_exports_the_accepted_threaded_public_surface() -> None:
    """Action Plan 25, chunk 16: the package SHALL export exactly the
    accepted threaded surface (``.claude/specs/threadedSocketTransaction.md``
    "Public surface" section) — no old asyncio aliases or compatibility
    wrappers."""
    from foundation_tools.socket_transaction import (
        AckStatus,
        AngleBracketTransactionCodec,
        BinaryFramedSocketHandlerClient,
        CompletionStatus,
        InboundTransaction,
        JsonTransactionCodec,
        SendStatus,
        SocketHandler,
        SocketHandlerClient,
        SocketHandlerServer,
        TransactingSocketHandlerClient,
        TransactingSocketHandlerServer,
        TransactionCodec,
        TransactionFrame,
        TransactionOutcome,
    )

    accepted = [
        SocketHandler,
        SocketHandlerClient,
        SocketHandlerServer,
        BinaryFramedSocketHandlerClient,
        TransactionFrame,
        TransactionCodec,
        JsonTransactionCodec,
        AngleBracketTransactionCodec,
        SendStatus,
        AckStatus,
        CompletionStatus,
        TransactionOutcome,
        InboundTransaction,
        TransactingSocketHandlerClient,
        TransactingSocketHandlerServer,
    ]
    assert all(item is not None for item in accepted)


def test_socket_transaction_exports_none_of_the_removed_asyncio_names() -> None:
    """The removed asyncio socket facade SHALL NOT remain importable from the
    package surface."""
    import foundation_tools.socket_transaction as socket_transaction

    removed_names = [
        "ConnectionClosedError",
        "DelimiterCodec",
        "FramingCodec",
        "LengthPrefixedCodec",
        "SocketByteTransport",
        "SocketTransact",
        "SocketTransactResult",
        "SocketTransactResultModel",
        "SocketTransactServer",
        "TransactionRouter",
    ]
    for name in removed_names:
        assert not hasattr(socket_transaction, name), f"{name} must not remain exported"
