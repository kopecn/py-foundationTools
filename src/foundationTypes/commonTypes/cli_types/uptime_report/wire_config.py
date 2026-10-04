"""Wire config for UptimeReport (`uptime`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .UptimeReport import UptimeReport


def _decode(cls: type[UptimeReport], wire_str: str) -> UptimeReport:
    return cls.from_dict({"raw": wire_str.strip()})


UptimeReport.wire_invoke = ["uptime"]
UptimeReport.wire_decode = _decode
