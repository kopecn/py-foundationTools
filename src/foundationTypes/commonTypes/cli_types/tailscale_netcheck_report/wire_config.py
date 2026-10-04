"""Wire config for TailscaleNetcheckReport (`tailscale netcheck --format=json`).

tailscale emits JSON directly, so the model exposes a single free-form ``response``
object and ``from_wire`` feeds the parsed dict straight in (DataModelHelper supports
a free-form object field) rather than re-parsing a human report. The JSON is
identical on macOS and Linux, so no OS branch is needed.
"""

from __future__ import annotations

import json

from .TailscaleNetcheckReport import TailscaleNetcheckReport


def _decode(cls: type[TailscaleNetcheckReport], wire_str: str) -> TailscaleNetcheckReport:
    return cls.from_dict({"response": json.loads(wire_str)})


def _wire_encode(self: TailscaleNetcheckReport, **kwargs: object) -> str:
    return json.dumps(self.response)


TailscaleNetcheckReport.wire_invoke = ["tailscale", "netcheck", "--format=json"]
TailscaleNetcheckReport.wire_decode = _decode
TailscaleNetcheckReport.wire_encode = _wire_encode
