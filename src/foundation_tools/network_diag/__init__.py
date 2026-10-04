"""Read-only, collect-only local network diagnostics.

Runs the ``cli_types`` CLI command models and emits their parsed output as one
JSON report. See ``.claude/specs/networkDiag.md``. The ``network-diag`` console
script is defined in :mod:`foundation_tools.network_diag.cli`.
"""

from foundation_tools.network_diag.NetworkDiag import NetworkDiag

__all__ = ["NetworkDiag"]
