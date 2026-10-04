"""Wire config for IwconfigReport (`iwconfig`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .IwconfigReport import IwconfigReport


def _decode(cls: type[IwconfigReport], wire_str: str) -> IwconfigReport:
    return cls.from_dict({"raw": wire_str.strip()})


IwconfigReport.wire_invoke = ["iwconfig"]
IwconfigReport.wire_decode = _decode
