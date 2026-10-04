"""Wire config for ResolvConfReport (`cat /etc/resolv.conf`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .ResolvConfReport import ResolvConfReport


def _decode(cls: type[ResolvConfReport], wire_str: str) -> ResolvConfReport:
    return cls.from_dict({"raw": wire_str.strip()})


def _wire_encode(self: ResolvConfReport, **kwargs: object) -> str:
    return self.raw


ResolvConfReport.wire_invoke = ["cat", "/etc/resolv.conf"]
ResolvConfReport.wire_decode = _decode
ResolvConfReport.wire_encode = _wire_encode
