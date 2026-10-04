"""Wire config for HostnamectlReport (`hostnamectl status`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .HostnamectlReport import HostnamectlReport


def _decode(cls: type[HostnamectlReport], wire_str: str) -> HostnamectlReport:
    entries: list[dict[str, str]] = []
    for line in wire_str.strip().splitlines():
        if ":" not in line or not line.strip():
            continue
        key, _, value = line.partition(":")
        entries.append({"key": key.strip(), "value": value.strip()})
    return cls.from_dict({"entries": entries, "raw": wire_str.strip()})


def _wire_encode(self: HostnamectlReport, **kwargs: object) -> str:
    return self.raw


HostnamectlReport.wire_invoke = ["hostnamectl", "status"]
HostnamectlReport.wire_decode = _decode
HostnamectlReport.wire_encode = _wire_encode
