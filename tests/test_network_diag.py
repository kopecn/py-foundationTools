"""Tests for the stripped-down NetworkDiag collector."""

from __future__ import annotations

import asyncio

from foundation_tools.network_diag import NetworkDiag
from foundation_tools.network_diag.NetworkDiag import models_for_system
from foundationTypes.commonTypes.cli_types.nmcli_general_report import NmcliGeneralReport
from foundationTypes.commonTypes.cli_types.uname_report import UnameReport
from foundationTypes.data_model_helper import DataModelHelper


def test_suite_is_explicit_and_per_os() -> None:
    linux = models_for_system("Linux")
    macos = models_for_system("Darwin")
    assert linux and macos, "expected a non-empty suite for each OS"
    assert all(issubclass(model, DataModelHelper) for model in linux + macos)
    # Cross-platform model present on both; Linux-only model only on Linux.
    assert UnameReport in linux and UnameReport in macos
    assert NmcliGeneralReport in linux and NmcliGeneralReport not in macos
    # macOS suite is a strict subset of the Linux suite here.
    assert set(macos) < set(linux)
    # DiskUsage is not a network probe and is never in the suite.
    assert not any(model.__name__ == "DiskUsage" for model in linux)


def test_unknown_os_yields_empty_suite() -> None:
    assert models_for_system("Plan9") == ()


def test_networkdiag_runs_injected_model() -> None:
    report = asyncio.run(NetworkDiag(models=[UnameReport], timeout_s=5).run())
    assert set(report) == {"UnameReport"}
