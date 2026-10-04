"""Wire config for NetworkctlReport (`networkctl status --no-pager`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .NetworkctlReport import NetworkctlReport


def _decode(cls: type[NetworkctlReport], wire_str: str) -> NetworkctlReport:
    return cls.from_dict({"raw": wire_str.strip()})


def _wire_encode(self: NetworkctlReport, **kwargs: object) -> str:
    return self.raw


NetworkctlReport.wire_invoke = ["networkctl", "status", "--no-pager"]
NetworkctlReport.wire_decode = _decode
NetworkctlReport.wire_encode = _wire_encode
