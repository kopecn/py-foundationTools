"""Wire config for NftablesReport (`nft list ruleset`).

Binds the read-only argv (``wire_invoke``) and the stdout parser (``wire_decode``)
onto the generated model, so it runs via ``CLITransact``/``SSHTransact``
``run_async_with_model``. Self-contained by design.
"""

from __future__ import annotations

from .NftablesReport import NftablesReport


def _decode(cls: type[NftablesReport], wire_str: str) -> NftablesReport:
    return cls.from_dict({"raw": wire_str.strip()})


NftablesReport.wire_invoke = ["nft", "list", "ruleset"]
NftablesReport.wire_decode = _decode
