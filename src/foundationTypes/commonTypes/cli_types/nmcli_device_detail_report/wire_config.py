"""Wire config for NmcliDeviceDetailReport (`nmcli -f all device show`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .NmcliDeviceDetailReport import NmcliDeviceDetailReport


def _decode(cls: type[NmcliDeviceDetailReport], wire_str: str) -> NmcliDeviceDetailReport:
    return cls.from_dict({"raw": wire_str.strip()})


def _wire_encode(self: NmcliDeviceDetailReport, **kwargs: object) -> str:
    return self.raw


NmcliDeviceDetailReport.wire_invoke = ["nmcli", "-f", "all", "device", "show"]
NmcliDeviceDetailReport.wire_decode = _decode
NmcliDeviceDetailReport.wire_encode = _wire_encode
