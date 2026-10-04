"""Wire config for ResolvectlReport (`resolvectl status`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

import platform

from .ResolvectlReport import ResolvectlReport


def _decode(cls: type[ResolvectlReport], wire_str: str) -> ResolvectlReport:
    return cls.from_dict({"raw": wire_str.strip()})


if platform.system() == "Darwin":
    ResolvectlReport.wire_invoke = ["scutil", "--dns"]
    ResolvectlReport.wire_decode = _decode
else:
    ResolvectlReport.wire_invoke = ["resolvectl", "status"]
    ResolvectlReport.wire_decode = _decode
