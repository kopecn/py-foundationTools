"""Wire config for RfkillReport (`rfkill list`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .RfkillReport import RfkillReport


def _decode(cls: type[RfkillReport], wire_str: str) -> RfkillReport:
    return cls.from_dict({"raw": wire_str.strip()})


def _wire_encode(self: RfkillReport, **kwargs: object) -> str:
    return self.raw


RfkillReport.wire_invoke = ["rfkill", "list"]
RfkillReport.wire_decode = _decode
RfkillReport.wire_encode = _wire_encode
