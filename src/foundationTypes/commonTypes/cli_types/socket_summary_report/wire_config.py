"""Wire config for SocketSummaryReport (`ss -s`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

import platform

from .SocketSummaryReport import SocketSummaryReport


def _decode(cls: type[SocketSummaryReport], wire_str: str) -> SocketSummaryReport:
    return cls.from_dict({"raw": wire_str.strip()})


if platform.system() == "Darwin":
    SocketSummaryReport.wire_invoke = ["netstat", "-an"]
    SocketSummaryReport.wire_decode = _decode
else:
    SocketSummaryReport.wire_invoke = ["ss", "-s"]
    SocketSummaryReport.wire_decode = _decode
