"""Wire config for LinkBriefReport (`ip -brief link show`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

import platform
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


def _wire_encode(self: LinkBriefReport, **kwargs: object) -> str:
    return self.raw


def _decode_macos(cls: type[LinkBriefReport], wire_str: str) -> LinkBriefReport:
    rows: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for line in wire_str.splitlines():
        if line and not line[0].isspace():
            name = line.split(":", 1)[0]
            flags: list[str] = []
            if "<" in line and ">" in line:
                flags = [f for f in line[line.index("<") + 1 : line.index(">")].split(",") if f]
            current = {
                "ifname": name,
                "operstate": "UP" if "UP" in flags else "DOWN",
                "flags": flags,
            }
            rows.append(current)
        elif current is not None:
            stripped = line.strip()
            if stripped.startswith("ether "):
                current["mac"] = stripped.split()[1]
            elif stripped.startswith("status:"):
                current["operstate"] = stripped.split(":", 1)[1].strip()
    return cls.from_dict({"rows": rows, "raw": wire_str.strip()})


if platform.system() == "Darwin":
    LinkBriefReport.wire_invoke = ["ifconfig"]
    LinkBriefReport.wire_decode = _decode_macos
else:
    LinkBriefReport.wire_invoke = ["ip", "-brief", "link", "show"]
    LinkBriefReport.wire_decode = _decode
LinkBriefReport.wire_encode = _wire_encode
