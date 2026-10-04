"""Wire config for LinkBriefReport (`ip -brief link show`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

import re

from .LinkBriefReport import LinkBriefReport

_MAC_RE = re.compile(r"^(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$")


def _decode(cls: type[LinkBriefReport], wire_str: str) -> LinkBriefReport:
    rows: list[dict[str, object]] = []
    for line in wire_str.strip().splitlines():
        tokens = line.split()
        if len(tokens) < 2:
            continue
        ifname, operstate = tokens[0], tokens[1]
        rest = tokens[2:]
        mac: str | None = None
        if rest and _MAC_RE.match(rest[0]):
            mac = rest[0]
            rest = rest[1:]
        flags: list[str] = []
        for token in rest:
            if token.startswith("<") and token.endswith(">"):
                flags.extend(part for part in token.strip("<>").split(",") if part)
        row: dict[str, object] = {"ifname": ifname, "operstate": operstate, "flags": flags}
        if mac is not None:
            row["mac"] = mac
        rows.append(row)
    return cls.from_dict({"rows": rows, "raw": wire_str.strip()})


LinkBriefReport.wire_invoke = ["ip", "-brief", "link", "show"]
LinkBriefReport.wire_decode = _decode
