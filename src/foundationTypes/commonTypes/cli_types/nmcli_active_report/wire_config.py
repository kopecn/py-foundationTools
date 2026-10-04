"""Wire config for NmcliActiveReport (`nmcli -f all connection show --active`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .NmcliActiveReport import NmcliActiveReport


def _decode(cls: type[NmcliActiveReport], wire_str: str) -> NmcliActiveReport:
    return cls.from_dict({"raw": wire_str.strip()})


NmcliActiveReport.wire_invoke = ["nmcli", "-f", "all", "connection", "show", "--active"]
NmcliActiveReport.wire_decode = _decode
