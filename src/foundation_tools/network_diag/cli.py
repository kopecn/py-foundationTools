"""The ``network-diag`` console entry point.

Builds a :class:`NetworkDiag` collector, runs it locally, and prints the JSON
report to stdout. Collect-only: it never mutates host state. See
``.claude/specs/networkDiag.md``.
"""

from __future__ import annotations

import asyncio
import json
import sys

from foundation_tools.network_diag.NetworkDiag import NetworkDiag


def main() -> int:
    """Collect the local diagnostics report and print it as JSON. Returns 0."""
    report = asyncio.run(NetworkDiag().run())
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
