"""Wire config for DmesgReport (`dmesg --level=err,warn --ctime`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .DmesgReport import DmesgReport


def _decode(cls: type[DmesgReport], wire_str: str) -> DmesgReport:
    return cls.from_dict({"raw": wire_str.strip()})


DmesgReport.wire_invoke = ["dmesg", "--level=err,warn", "--ctime"]
DmesgReport.wire_decode = _decode
