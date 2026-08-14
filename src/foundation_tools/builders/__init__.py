"""
Command Builders — Layer 2 of the process-transaction stack.

Command builders produce executable command vectors (``list[str]`` or ``str``)
deterministically and without side effects. They never execute commands; execution
is delegated to :mod:`foundation_tools.cli_transaction`.

See ``.claude/specs/transport_transaction_architecture.md`` (Layer 2 — Command
Builders) for the full contract.
"""

from foundation_tools.builders.rsync_builder import (
    WINDOWS_SAFE_RSYNC_OPTIONS,
    build_rsync_command,
)
from foundation_tools.builders.ssh_builder import build_ssh_command

__all__ = [
    "WINDOWS_SAFE_RSYNC_OPTIONS",
    "build_rsync_command",
    "build_ssh_command",
]
