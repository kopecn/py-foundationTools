"""Wire config for LinkStatsReport (`ip -statistics link show`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .LinkStatsReport import LinkStatsReport


def _decode(cls: type[LinkStatsReport], wire_str: str) -> LinkStatsReport:
    return cls.from_dict({"raw": wire_str.strip()})


LinkStatsReport.wire_invoke = ["ip", "-statistics", "link", "show"]
LinkStatsReport.wire_decode = _decode
