"""Wire config for JournalNmReport (`journalctl -u NetworkManager -n 200 --no-pager`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .JournalNmReport import JournalNmReport


def _decode(cls: type[JournalNmReport], wire_str: str) -> JournalNmReport:
    return cls.from_dict({"raw": wire_str.strip()})


def _wire_encode(self: JournalNmReport, **kwargs: object) -> str:
    return self.raw


JournalNmReport.wire_invoke = ["journalctl", "-u", "NetworkManager", "-n", "200", "--no-pager"]
JournalNmReport.wire_decode = _decode
JournalNmReport.wire_encode = _wire_encode
