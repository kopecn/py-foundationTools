"""Wire config for AddressBriefReport (`ip -brief address show`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .AddressBriefReport import AddressBriefReport


def _decode(cls: type[AddressBriefReport], wire_str: str) -> AddressBriefReport:
    rows: list[dict[str, object]] = []
    for line in wire_str.strip().splitlines():
        tokens = line.split()
        if len(tokens) < 2:
            continue
        rows.append({"ifname": tokens[0], "operstate": tokens[1], "addresses": tokens[2:]})
    return cls.from_dict({"rows": rows, "raw": wire_str.strip()})


AddressBriefReport.wire_invoke = ["ip", "-brief", "address", "show"]
AddressBriefReport.wire_decode = _decode
