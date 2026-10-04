"""Wire config for AddressBriefReport (`ip -brief address show`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

import platform

from .AddressBriefReport import AddressBriefReport


def _decode(cls: type[AddressBriefReport], wire_str: str) -> AddressBriefReport:
    rows: list[dict[str, object]] = []
    for line in wire_str.strip().splitlines():
        tokens = line.split()
        if len(tokens) < 2:
            continue
        rows.append({"ifname": tokens[0], "operstate": tokens[1], "addresses": tokens[2:]})
    return cls.from_dict({"rows": rows, "raw": wire_str.strip()})


def _wire_encode(self: AddressBriefReport, **kwargs: object) -> str:
    return self.raw


def _decode_macos(cls: type[AddressBriefReport], wire_str: str) -> AddressBriefReport:
    rows: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for line in wire_str.splitlines():
        if line and not line[0].isspace():
            name = line.split(":", 1)[0]
            operstate = "UP" if "UP" in line.split("<", 1)[-1] else "DOWN"
            current = {"ifname": name, "operstate": operstate, "addresses": []}
            rows.append(current)
        elif current is not None:
            stripped = line.strip()
            if stripped.startswith(("inet ", "inet6 ")):
                addresses = current["addresses"]
                assert isinstance(addresses, list)
                addresses.append(stripped.split()[1])
            elif stripped.startswith("status:"):
                current["operstate"] = stripped.split(":", 1)[1].strip()
    return cls.from_dict({"rows": rows, "raw": wire_str.strip()})


if platform.system() == "Darwin":
    AddressBriefReport.wire_invoke = ["ifconfig"]
    AddressBriefReport.wire_decode = _decode_macos
else:
    AddressBriefReport.wire_invoke = ["ip", "-brief", "address", "show"]
    AddressBriefReport.wire_decode = _decode
AddressBriefReport.wire_encode = _wire_encode
