"""Wire config for Route6Report (`ip -6 route show`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

import platform

from .Route6Report import Route6Report


def _after(tokens: list[str], key: str) -> str | None:
    if key in tokens:
        index = tokens.index(key)
        if index + 1 < len(tokens):
            return tokens[index + 1]
    return None


def _decode(cls: type[Route6Report], wire_str: str) -> Route6Report:
    rows: list[dict[str, object]] = []
    for line in wire_str.strip().splitlines():
        tokens = line.split()
        if not tokens:
            continue
        row: dict[str, object] = {"destination": tokens[0], "raw": line.strip()}
        for key in ("via", "dev", "proto", "metric"):
            value = _after(tokens, key)
            if value is not None:
                row[key] = value
        rows.append(row)
    return cls.from_dict({"rows": rows, "raw": wire_str.strip()})


def _decode_macos(cls: type[Route6Report], wire_str: str) -> Route6Report:
    return cls.from_dict({"rows": [], "raw": wire_str.strip()})


if platform.system() == "Darwin":
    Route6Report.wire_invoke = ["netstat", "-rn", "-f", "inet6"]
    Route6Report.wire_decode = _decode_macos
else:
    Route6Report.wire_invoke = ["ip", "-6", "route", "show"]
    Route6Report.wire_decode = _decode
