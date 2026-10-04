"""Wire config for UnameReport (`uname -a`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .UnameReport import UnameReport


def _decode(cls: type[UnameReport], wire_str: str) -> UnameReport:
    return cls.from_dict({"raw": wire_str.strip()})


UnameReport.wire_invoke = ["uname", "-a"]
UnameReport.wire_decode = _decode
