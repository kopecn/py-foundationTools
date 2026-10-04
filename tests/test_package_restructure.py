"""
Tests for the Action Plan 01 package restructure: subpackage skeletons and the
cli_transaction public re-export.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path


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


# Design constraint (plan 25, chunk 24): "Run cutover verification in a fresh
# interpreter" -- an already-imported pytest process cannot prove a clean
# cutover (e.g. a name left importable only because some other test module
# imported the removed submodule first). Every check below runs in a
# subprocess with an explicit `PYTHONPATH=<repo>/src`, matching this repo's
# pytest `pythonpath` convention rather than trusting the calling process's
# already-populated `sys.path`/`sys.modules`.

_EXPECTED_PUBLIC_ALL = [
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

# The asyncio-era submodules removed by the threaded cutover (plan 25); each
# must fail to import, not merely be absent from the package's __all__.
_REMOVED_SUBMODULES = [
    "foundation_tools.socket_transaction.socketTransact",
    "foundation_tools.socket_transaction.socketTransactServer",
    "foundation_tools.socket_transaction.framing_codecs",
    "foundation_tools.socket_transaction.socket_byte_transport",
    "foundation_tools.socket_transaction.transaction_router",
    "foundation_tools.socket_transaction._lifecycle",
]

_REMOVED_NAMES = [
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


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _run_fresh_interpreter(script: str) -> subprocess.CompletedProcess[str]:
    """Run ``script`` in a brand-new interpreter process.

    Sets ``PYTHONPATH`` explicitly to ``<repo>/src`` (this project's `src/`
    layout, per ``pyproject.toml``'s ``[tool.pytest.ini_options] pythonpath``)
    rather than inheriting whatever ``sys.path`` the calling pytest process
    already built -- the whole point of a fresh-process check is to not
    trust that process.
    """
    repo_root = _repo_root()
    return subprocess.run(
        [sys.executable, "-c", textwrap.dedent(script)],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(repo_root),
        env={"PATH": os.environ.get("PATH", ""), "PYTHONPATH": str(repo_root / "src")},
        timeout=30,
    )


class TestFreshProcessCutoverVerification:
    """Action Plan 25, chunk 24 (PA25-08): chunk 16's public-surface/removed-
    name checks above run inside the already-imported pytest process. These
    run the same claims in a fresh interpreter, per the chunk's "Fresh-process
    recipe"."""

    def test_exact_all_and_every_accepted_name_imports_in_a_fresh_interpreter(self) -> None:
        script = f"""
            import foundation_tools.socket_transaction as package

            expected_all = {_EXPECTED_PUBLIC_ALL!r}
            actual_all = list(package.__all__)
            assert actual_all == expected_all, (actual_all, expected_all)
            for name in expected_all:
                assert getattr(package, name) is not None, name
            print("OK")
            """
        completed = _run_fresh_interpreter(script)
        assert completed.returncode == 0, completed.stderr
        assert completed.stdout.strip() == "OK"

    def test_removed_submodules_fail_to_import_in_a_fresh_interpreter(self) -> None:
        script = f"""
            import importlib

            for module_name in {_REMOVED_SUBMODULES!r}:
                try:
                    importlib.import_module(module_name)
                except ModuleNotFoundError:
                    continue
                raise AssertionError(f"{{module_name}} unexpectedly importable")
            print("OK")
            """
        completed = _run_fresh_interpreter(script)
        assert completed.returncode == 0, completed.stderr
        assert completed.stdout.strip() == "OK"

    def test_no_old_asyncio_aliases_remain_in_a_fresh_interpreter(self) -> None:
        script = f"""
            import foundation_tools.socket_transaction as package

            for name in {_REMOVED_NAMES!r}:
                assert not hasattr(package, name), f"{{name}} must not remain exported"
            print("OK")
            """
        completed = _run_fresh_interpreter(script)
        assert completed.returncode == 0, completed.stderr
        assert completed.stdout.strip() == "OK"

    def test_project_has_zero_runtime_dependencies_in_a_fresh_interpreter(self) -> None:
        pyproject_path = _repo_root() / "pyproject.toml"
        script = f"""
            import tomllib

            with open({str(pyproject_path)!r}, "rb") as handle:
                data = tomllib.load(handle)

            dependencies = data["project"]["dependencies"]
            assert dependencies == [], dependencies
            print("OK")
            """
        completed = _run_fresh_interpreter(script)
        assert completed.returncode == 0, completed.stderr
        assert completed.stdout.strip() == "OK"
