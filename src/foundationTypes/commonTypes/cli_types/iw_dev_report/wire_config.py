"""Wire config for IwDevReport (`iw dev`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .IwDevReport import IwDevReport


def _decode(cls: type[IwDevReport], wire_str: str) -> IwDevReport:
    return cls.from_dict({"raw": wire_str.strip()})


def _wire_encode(self: IwDevReport, **kwargs: object) -> str:
    return self.raw


IwDevReport.wire_invoke = ["iw", "dev"]
IwDevReport.wire_decode = _decode
IwDevReport.wire_encode = _wire_encode
