"""Wire config for JournalKernelReport (`journalctl -k -n 300 --no-pager`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .JournalKernelReport import JournalKernelReport


def _decode(cls: type[JournalKernelReport], wire_str: str) -> JournalKernelReport:
    return cls.from_dict({"raw": wire_str.strip()})


JournalKernelReport.wire_invoke = ["journalctl", "-k", "-n", "300", "--no-pager"]
JournalKernelReport.wire_decode = _decode
