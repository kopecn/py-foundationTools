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
