"""Wire config for TailscaleStatusReport (`tailscale status --json`).

tailscale emits JSON directly, so the model exposes a single free-form ``response``
object and ``from_wire`` feeds the parsed dict straight in (DataModelHelper supports
a free-form object field) rather than re-parsing a human table. The JSON is identical
on macOS and Linux, so no OS branch is needed.
"""

from __future__ import annotations

import json

from .TailscaleStatusReport import TailscaleStatusReport


def _decode(cls: type[TailscaleStatusReport], wire_str: str) -> TailscaleStatusReport:
    return cls.from_dict({"response": json.loads(wire_str)})


def _wire_encode(self: TailscaleStatusReport, **kwargs: object) -> str:
    return json.dumps(self.response)


TailscaleStatusReport.wire_invoke = ["tailscale", "status", "--json"]
TailscaleStatusReport.wire_decode = _decode
TailscaleStatusReport.wire_encode = _wire_encode
