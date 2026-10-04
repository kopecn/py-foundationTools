"""Wire config for TailscaleStatusReport (`tailscale status`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .TailscaleStatusReport import TailscaleStatusReport


def _decode(cls: type[TailscaleStatusReport], wire_str: str) -> TailscaleStatusReport:
    return cls.from_dict({"raw": wire_str.strip()})


TailscaleStatusReport.wire_invoke = ["tailscale", "status"]
TailscaleStatusReport.wire_decode = _decode
