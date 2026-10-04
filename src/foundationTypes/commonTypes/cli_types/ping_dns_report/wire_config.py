"""Wire config for PingDNSReport (`ping -c 2 -W 2 one.one.one.one`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

import re

from .PingDNSReport import PingDNSReport

_HOST_RE = re.compile(r"^PING\s+(\S+)")
_STATS_RE = re.compile(
    r"(\d+)\s+packets transmitted,\s+(\d+)\s+(?:packets )?received" r".*?([\d.]+)%\s+packet loss"
)
_RTT_RE = re.compile(r"=\s*([\d.]+)/([\d.]+)/([\d.]+)/[\d.]+\s*ms")


def _decode(cls: type[PingDNSReport], wire_str: str) -> PingDNSReport:
    out: dict[str, object] = {"raw": wire_str.strip()}
    host_match = _HOST_RE.search(wire_str)
    if host_match:
        out["host"] = host_match.group(1)
    stats_match = _STATS_RE.search(wire_str)
    if stats_match:
        out["transmitted"] = stats_match.group(1)
        out["received"] = stats_match.group(2)
        out["packet_loss"] = f"{stats_match.group(3)}%"
    rtt_match = _RTT_RE.search(wire_str)
    if rtt_match:
        out["rtt_min_ms"] = rtt_match.group(1)
        out["rtt_avg_ms"] = rtt_match.group(2)
        out["rtt_max_ms"] = rtt_match.group(3)
    return cls.from_dict(out)


PingDNSReport.wire_invoke = ["ping", "-c", "2", "-W", "2", "one.one.one.one"]
PingDNSReport.wire_decode = _decode
