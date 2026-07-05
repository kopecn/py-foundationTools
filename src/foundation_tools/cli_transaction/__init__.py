"""
CLI Transaction — Layer 1 (execution kernel) of the process-transaction stack.

Re-exports the public surface so callers import from the package rather than the
module file: ``from foundation_tools.cli_transaction import CLITransact``.
"""

from foundation_tools.cli_transaction.cliTransact import (
    CLITransact,
    CLITransactResult,
    CLITransactResultModel,
)
from foundation_tools.cli_transaction.rsyncTransact import (
    RSYNC_PERMANENT_RETURN_CODES,
    RSYNC_TRANSIENT_RETURN_CODES,
    WINDOWS_SAFE_RSYNC_OPTIONS,
    RsyncTransact,
)
from foundation_tools.cli_transaction.sshTransact import SSHTransact

__all__ = [
    "RSYNC_PERMANENT_RETURN_CODES",
    "RSYNC_TRANSIENT_RETURN_CODES",
    "WINDOWS_SAFE_RSYNC_OPTIONS",
    "CLITransact",
    "CLITransactResult",
    "CLITransactResultModel",
    "RsyncTransact",
    "SSHTransact",
]
