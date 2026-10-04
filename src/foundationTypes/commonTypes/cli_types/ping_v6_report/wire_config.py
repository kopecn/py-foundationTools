"""Wire config for PingV6Report (`ping -6 -c 2 -W 2 2606:4700:4700::1111`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

import platform
import re

from .PingV6Report import PingV6Report

_HOST_RE = re.compile(r"^PING\s+(\S+)")
_STATS_RE = re.compile(
    r"(\d+)\s+packets transmitted,\s+(\d+)\s+(?:packets )?received" r".*?([\d.]+)%\s+packet loss"
)
_RTT_RE = re.compile(r"=\s*([\d.]+)/([\d.]+)/([\d.]+)/[\d.]+\s*ms")


def _decode(cls: type[PingV6Report], wire_str: str) -> PingV6Report:
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


if platform.system() == "Darwin":
    PingV6Report.wire_invoke = ["ping6", "-c", "2", "2606:4700:4700::1111"]
    PingV6Report.wire_decode = _decode
else:
    PingV6Report.wire_invoke = ["ping", "-6", "-c", "2", "-W", "2", "2606:4700:4700::1111"]
    PingV6Report.wire_decode = _decode
