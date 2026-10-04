"""Wire config for NmcliGeneralReport (`nmcli general status`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .NmcliGeneralReport import NmcliGeneralReport


def _decode(cls: type[NmcliGeneralReport], wire_str: str) -> NmcliGeneralReport:
    return cls.from_dict({"raw": wire_str.strip()})


NmcliGeneralReport.wire_invoke = ["nmcli", "general", "status"]
NmcliGeneralReport.wire_decode = _decode
