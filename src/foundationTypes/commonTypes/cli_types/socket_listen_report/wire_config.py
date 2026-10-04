"""Wire config for SocketListenReport (`ss -tulpnH`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .SocketListenReport import SocketListenReport


def _decode(cls: type[SocketListenReport], wire_str: str) -> SocketListenReport:
    rows: list[dict[str, object]] = []
    for line in wire_str.strip().splitlines():
        tokens = line.split()
        if len(tokens) < 6:
            continue
        row: dict[str, object] = {
            "netid": tokens[0],
            "state": tokens[1],
            "recv_q": tokens[2],
            "send_q": tokens[3],
            "local_address": tokens[4],
            "peer_address": tokens[5],
        }
        if len(tokens) > 6:
            row["process"] = " ".join(tokens[6:])
        rows.append(row)
    return cls.from_dict({"rows": rows, "raw": wire_str.strip()})


def _wire_encode(self: SocketListenReport, **kwargs: object) -> str:
    return self.raw


SocketListenReport.wire_invoke = ["ss", "-tulpnH"]
SocketListenReport.wire_decode = _decode
SocketListenReport.wire_encode = _wire_encode
