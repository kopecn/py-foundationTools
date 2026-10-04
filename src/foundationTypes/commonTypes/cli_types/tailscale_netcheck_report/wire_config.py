"""Wire config for TailscaleNetcheckReport (`tailscale netcheck`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .TailscaleNetcheckReport import TailscaleNetcheckReport


def _decode(cls: type[TailscaleNetcheckReport], wire_str: str) -> TailscaleNetcheckReport:
    return cls.from_dict({"raw": wire_str.strip()})


TailscaleNetcheckReport.wire_invoke = ["tailscale", "netcheck"]
TailscaleNetcheckReport.wire_decode = _decode
