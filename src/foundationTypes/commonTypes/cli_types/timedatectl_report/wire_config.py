"""Wire config for TimedatectlReport (`timedatectl status`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .TimedatectlReport import TimedatectlReport


def _decode(cls: type[TimedatectlReport], wire_str: str) -> TimedatectlReport:
    entries: list[dict[str, str]] = []
    for line in wire_str.strip().splitlines():
        if ":" not in line or not line.strip():
            continue
        key, _, value = line.partition(":")
        entries.append({"key": key.strip(), "value": value.strip()})
    return cls.from_dict({"entries": entries, "raw": wire_str.strip()})


TimedatectlReport.wire_invoke = ["timedatectl", "status"]
TimedatectlReport.wire_decode = _decode
