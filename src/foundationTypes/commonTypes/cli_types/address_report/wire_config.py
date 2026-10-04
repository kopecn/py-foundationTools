"""Wire config for AddressReport (`ip -details address show`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

import platform

from .AddressReport import AddressReport


def _decode(cls: type[AddressReport], wire_str: str) -> AddressReport:
    return cls.from_dict({"raw": wire_str.strip()})


def _wire_encode(self: AddressReport, **kwargs: object) -> str:
    return self.raw


if platform.system() == "Darwin":
    AddressReport.wire_invoke = ["ifconfig", "-a"]
    AddressReport.wire_decode = _decode
else:
    AddressReport.wire_invoke = ["ip", "-details", "address", "show"]
    AddressReport.wire_decode = _decode
AddressReport.wire_encode = _wire_encode
