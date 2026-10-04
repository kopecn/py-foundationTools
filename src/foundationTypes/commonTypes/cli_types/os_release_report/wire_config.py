"""Wire config for OSReleaseReport (`cat /etc/os-release`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

import platform

from .OSReleaseReport import OSReleaseReport


def _decode(cls: type[OSReleaseReport], wire_str: str) -> OSReleaseReport:
    entries: list[dict[str, str]] = []
    for line in wire_str.strip().splitlines():
        if not line.strip() or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        entries.append({"key": key.strip(), "value": value.strip().strip('"').strip("'")})
    return cls.from_dict({"entries": entries, "raw": wire_str.strip()})


def _decode_macos(cls: type[OSReleaseReport], wire_str: str) -> OSReleaseReport:
    entries: list[dict[str, str]] = []
    for line in wire_str.strip().splitlines():
        if ":" not in line or not line.strip():
            continue
        key, _, value = line.partition(":")
        entries.append({"key": key.strip(), "value": value.strip()})
    return cls.from_dict({"entries": entries, "raw": wire_str.strip()})


if platform.system() == "Darwin":
    OSReleaseReport.wire_invoke = ["sw_vers"]
    OSReleaseReport.wire_decode = _decode_macos
else:
    OSReleaseReport.wire_invoke = ["cat", "/etc/os-release"]
    OSReleaseReport.wire_decode = _decode
