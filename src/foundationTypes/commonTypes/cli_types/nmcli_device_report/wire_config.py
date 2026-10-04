"""Wire config for NmcliDeviceReport (`nmcli device status`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .NmcliDeviceReport import NmcliDeviceReport


def _decode(cls: type[NmcliDeviceReport], wire_str: str) -> NmcliDeviceReport:
    rows: list[dict[str, object]] = []
    for line in wire_str.strip().splitlines():
        tokens = line.split()
        if len(tokens) < 3 or tokens[0] == "DEVICE":
            continue
        row: dict[str, object] = {"device": tokens[0], "type": tokens[1], "state": tokens[2]}
        if len(tokens) > 3:
            row["connection"] = " ".join(tokens[3:])
        rows.append(row)
    return cls.from_dict({"rows": rows, "raw": wire_str.strip()})


def _wire_encode(self: NmcliDeviceReport, **kwargs: object) -> str:
    return self.raw


NmcliDeviceReport.wire_invoke = ["nmcli", "device", "status"]
NmcliDeviceReport.wire_decode = _decode
NmcliDeviceReport.wire_encode = _wire_encode
