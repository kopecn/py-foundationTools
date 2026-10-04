"""Tests for the stripped-down NetworkDiag collector."""

from __future__ import annotations

import asyncio

from foundation_tools.network_diag import NetworkDiag
from foundation_tools.network_diag.NetworkDiag import _discover_models
from foundationTypes.commonTypes.cli_types.uname_report import UnameReport
from foundationTypes.data_model_helper import DataModelHelper


def test_discover_models_excludes_disk_usage() -> None:
    models = _discover_models()
    assert models, "expected at least one network command model"
    assert all(issubclass(model, DataModelHelper) for model in models)
    assert all(isinstance(model.wire_invoke, list) and model.wire_invoke for model in models)
    assert UnameReport in models
    assert not any(model.__name__ == "DiskUsage" for model in models)


def test_networkdiag_runs_injected_model() -> None:
    report = asyncio.run(NetworkDiag(models=[UnameReport], timeout_s=5).run())
    assert set(report) == {"UnameReport"}
