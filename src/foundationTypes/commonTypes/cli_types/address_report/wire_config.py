"""Wire config for AddressReport (`ip -details address show`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .AddressReport import AddressReport


def _decode(cls: type[AddressReport], wire_str: str) -> AddressReport:
    return cls.from_dict({"raw": wire_str.strip()})


AddressReport.wire_invoke = ["ip", "-details", "address", "show"]
AddressReport.wire_decode = _decode
