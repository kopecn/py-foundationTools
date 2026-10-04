"""Wire config for NeighborReport (`ip neigh show`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

import platform

from .NeighborReport import NeighborReport


def _after(tokens: list[str], key: str) -> str | None:
    if key in tokens:
        index = tokens.index(key)
        if index + 1 < len(tokens):
            return tokens[index + 1]
    return None


def _decode(cls: type[NeighborReport], wire_str: str) -> NeighborReport:
    rows: list[dict[str, object]] = []
    for line in wire_str.strip().splitlines():
        tokens = line.split()
        if not tokens:
            continue
        row: dict[str, object] = {
            "address": tokens[0],
            "state": tokens[-1],
            "raw": line.strip(),
        }
        dev = _after(tokens, "dev")
        lladdr = _after(tokens, "lladdr")
        if dev is not None:
            row["dev"] = dev
        if lladdr is not None:
            row["lladdr"] = lladdr
        rows.append(row)
    return cls.from_dict({"rows": rows, "raw": wire_str.strip()})


def _decode_macos(cls: type[NeighborReport], wire_str: str) -> NeighborReport:
    return cls.from_dict({"rows": [], "raw": wire_str.strip()})


if platform.system() == "Darwin":
    NeighborReport.wire_invoke = ["arp", "-an"]
    NeighborReport.wire_decode = _decode_macos
else:
    NeighborReport.wire_invoke = ["ip", "neigh", "show"]
    NeighborReport.wire_decode = _decode
