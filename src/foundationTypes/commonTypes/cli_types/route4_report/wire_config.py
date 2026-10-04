"""Wire config for Route4Report (`ip route show`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .Route4Report import Route4Report


def _after(tokens: list[str], key: str) -> str | None:
    if key in tokens:
        index = tokens.index(key)
        if index + 1 < len(tokens):
            return tokens[index + 1]
    return None


def _decode(cls: type[Route4Report], wire_str: str) -> Route4Report:
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


Route4Report.wire_invoke = ["ip", "route", "show"]
Route4Report.wire_decode = _decode
