"""The ``network-diag`` console entry point.

Builds a :class:`NetworkDiag` collector, runs it locally, writes the report to disk
as a timestamped JSON artifact, and relays the JSON to stdout. Collect-only: it
never mutates host state. See ``.claude/specs/networkDiag.md``.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from platform import node

from foundation_tools.network_diag.NetworkDiag import NetworkDiag

_PROG = "network-diag"


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser for the collector."""
    parser = argparse.ArgumentParser(
        prog=_PROG,
        description="Read-only local network diagnostics collector (collect-only; never mutates).",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path.cwd(),
        help="Directory for the JSON report artifact (default: current directory).",
    )
    parser.add_argument(
        "--no-file",
        action="store_true",
        help="Do not write the report file; emit to stdout only.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Collect the local diagnostics report, write it as JSON, and relay it. Returns 0."""
    args = build_parser().parse_args(argv)

    report = asyncio.run(NetworkDiag().run())
    payload = json.dumps(report, indent=2)

    if not args.no_file:
        path = _write_json(payload, args.out_dir)

    sys.stdout.write(payload + "\n")

    if not args.no_file:
        print(f"saved: {path}", file=sys.stderr)

    return 0


def _write_json(payload: str, out_dir: Path) -> Path:
    """Write the JSON report to a timestamped file under ``out_dir`` and return its path."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"netdiag_{_safe(node() or 'host')}_{_file_stamp()}.json"
    path.write_text(payload + "\n", encoding="utf-8")
    return path


def _safe(name: str) -> str:
    """Reduce a hostname to a filename-safe token."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", name).strip("._")
    return cleaned or "host"


def _file_stamp() -> str:
    """Return a compact UTC timestamp for the artifact file name."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


if __name__ == "__main__":
    raise SystemExit(main())
