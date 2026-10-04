"""Wire config for SSHServiceReport (`systemctl status ssh --no-pager`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .SSHServiceReport import SSHServiceReport


def _decode(cls: type[SSHServiceReport], wire_str: str) -> SSHServiceReport:
    return cls.from_dict({"raw": wire_str.strip()})


def _wire_encode(self: SSHServiceReport, **kwargs: object) -> str:
    return self.raw


SSHServiceReport.wire_invoke = ["systemctl", "status", "ssh", "--no-pager"]
SSHServiceReport.wire_decode = _decode
SSHServiceReport.wire_encode = _wire_encode
