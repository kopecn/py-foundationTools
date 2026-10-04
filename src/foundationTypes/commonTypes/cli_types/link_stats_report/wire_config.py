"""Wire config for LinkStatsReport (`ip -statistics link show`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

import platform

from .LinkStatsReport import LinkStatsReport


def _decode(cls: type[LinkStatsReport], wire_str: str) -> LinkStatsReport:
    return cls.from_dict({"raw": wire_str.strip()})


def _wire_encode(self: LinkStatsReport, **kwargs: object) -> str:
    return self.raw


if platform.system() == "Darwin":
    LinkStatsReport.wire_invoke = ["netstat", "-i", "-b"]
    LinkStatsReport.wire_decode = _decode
else:
    LinkStatsReport.wire_invoke = ["ip", "-statistics", "link", "show"]
    LinkStatsReport.wire_decode = _decode
LinkStatsReport.wire_encode = _wire_encode
