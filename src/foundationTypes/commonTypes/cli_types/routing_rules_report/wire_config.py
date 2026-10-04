"""Wire config for RoutingRulesReport (`ip rule show`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .RoutingRulesReport import RoutingRulesReport


def _decode(cls: type[RoutingRulesReport], wire_str: str) -> RoutingRulesReport:
    return cls.from_dict({"raw": wire_str.strip()})


RoutingRulesReport.wire_invoke = ["ip", "rule", "show"]
RoutingRulesReport.wire_decode = _decode
