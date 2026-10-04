"""Wire config for LsmodReport (`lsmod`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .LsmodReport import LsmodReport


def _decode(cls: type[LsmodReport], wire_str: str) -> LsmodReport:
    rows: list[dict[str, object]] = []
    for line in wire_str.strip().splitlines():
        tokens = line.split()
        if len(tokens) < 3 or tokens[0] == "Module":
            continue
        used_by = [part for part in tokens[3].split(",") if part] if len(tokens) > 3 else []
        rows.append(
            {
                "module": tokens[0],
                "size": tokens[1],
                "used_by_count": tokens[2],
                "used_by": used_by,
            }
        )
    return cls.from_dict({"rows": rows, "raw": wire_str.strip()})


def _wire_encode(self: LsmodReport, **kwargs: object) -> str:
    return self.raw


LsmodReport.wire_invoke = ["lsmod"]
LsmodReport.wire_decode = _decode
LsmodReport.wire_encode = _wire_encode
