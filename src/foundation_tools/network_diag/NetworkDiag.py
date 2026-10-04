"""Local, read-only network diagnostics collector.

:class:`NetworkDiag` runs every CLI command model under
``foundationTypes.commonTypes.cli_types`` (except ``disk_usage``) concurrently
through :class:`CLITransact`. Each model carries its own read-only argv
(``wire_invoke``) and stdout parser (``from_wire``); the heavy lifting —
invocation, parsing, serialization — lives in those models and in
``DataModelHelper``. This class only drives the run and collects the parsed
results into one JSON-serializable report. Collect-only: it never mutates host
state. See ``.claude/specs/networkDiag.md``.
"""

from __future__ import annotations

import asyncio
import importlib
import pkgutil
from collections.abc import Sequence

from foundation_tools.cli_transaction import CLITransact
from foundationTypes.commonTypes import cli_types
from foundationTypes.data_model_helper import DataModelHelper

_DEFAULT_TIMEOUT_S = 10

# ``disk_usage`` (df -h) shares the cli_types shape but is not a network probe.
_EXCLUDED = frozenset({"disk_usage"})


def _discover_models() -> tuple[type[DataModelHelper], ...]:
    """Every network command model under ``cli_types``, sorted by class name.

    Each ``cli_types`` subpackage activates its wire bindings on import, so new
    probes are picked up with no change here. A command model is one bound to a
    non-empty argv (``wire_invoke``); the schema-generated nested row/entry models
    have none and are skipped.
    """
    models: list[type[DataModelHelper]] = []
    for info in pkgutil.iter_modules(cli_types.__path__):
        if not info.ispkg or info.name in _EXCLUDED:
            continue
        package = importlib.import_module(f"{cli_types.__name__}.{info.name}")
        for name in getattr(package, "__all__", ()):
            obj = getattr(package, name)
            if isinstance(obj, type) and issubclass(obj, DataModelHelper):
                if isinstance(obj.wire_invoke, list) and obj.wire_invoke:
                    models.append(obj)
    return tuple(sorted(models, key=lambda model: model.__name__))


class NetworkDiag:
    """Runs the read-only CLI command suite locally and reports the parsed result."""

    def __init__(
        self,
        models: Sequence[type[DataModelHelper]] | None = None,
        timeout_s: int = _DEFAULT_TIMEOUT_S,
    ) -> None:
        self.models = tuple(models) if models is not None else _discover_models()
        self.timeout_s = timeout_s

    async def run(self) -> dict[str, object]:
        """Run every model concurrently; return ``{model name: parsed dict | error}``."""
        results = await asyncio.gather(*(self._run_one(model) for model in self.models))
        return dict(results)

    async def _run_one(self, model: type[DataModelHelper]) -> tuple[str, object]:
        """Run one model via CLITransact, serializing the parsed model or the failure."""
        result = await CLITransact.run_async_with_model(model, timeout=self.timeout_s)
        if result.success and result.model is not None:
            return model.__name__, result.model.to_dict()
        return model.__name__, {"return_code": result.return_code, "stderr": result.stderr}
