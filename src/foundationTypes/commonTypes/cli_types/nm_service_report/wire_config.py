"""Wire config for NmServiceReport (`systemctl status NetworkManager --no-pager`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .NmServiceReport import NmServiceReport


def _decode(cls: type[NmServiceReport], wire_str: str) -> NmServiceReport:
    return cls.from_dict({"raw": wire_str.strip()})


def _wire_encode(self: NmServiceReport, **kwargs: object) -> str:
    return self.raw


NmServiceReport.wire_invoke = ["systemctl", "status", "NetworkManager", "--no-pager"]
NmServiceReport.wire_decode = _decode
NmServiceReport.wire_encode = _wire_encode
