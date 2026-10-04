"""Wire config for IptablesReport (`iptables -S`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .IptablesReport import IptablesReport


def _decode(cls: type[IptablesReport], wire_str: str) -> IptablesReport:
    return cls.from_dict({"raw": wire_str.strip()})


def _wire_encode(self: IptablesReport, **kwargs: object) -> str:
    return self.raw


IptablesReport.wire_invoke = ["iptables", "-S"]
IptablesReport.wire_decode = _decode
IptablesReport.wire_encode = _wire_encode
