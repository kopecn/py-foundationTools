"""Local, read-only network diagnostics collector.

:class:`NetworkDiag` runs a platform-appropriate suite of CLI command models
(under ``foundationTypes.commonTypes.cli_types``) concurrently through
:class:`CLITransact`. Each model carries its own read-only argv (``wire_invoke``)
and stdout parser (``from_wire``); the heavy lifting — invocation, parsing,
serialization — lives in those models and in ``DataModelHelper``. This class only
drives the run and collects the parsed results into one JSON-serializable report.
Collect-only: it never mutates host state. See ``.claude/specs/networkDiag.md``.

Which models run is an **explicit, hand-maintained registry** keyed by OS
(``platform.system()``), not a directory scan: a command runs on an OS only if it
is listed for that OS below. Adding a probe is a deliberate edit here — the suite is
never inferred from whatever modules happen to import.
"""

from __future__ import annotations

import asyncio
import platform
from collections.abc import Sequence

from foundation_tools.cli_transaction import CLITransact
from foundationTypes.commonTypes.cli_types.address_brief_report import AddressBriefReport
from foundationTypes.commonTypes.cli_types.address_report import AddressReport
from foundationTypes.commonTypes.cli_types.dmesg_report import DmesgReport
from foundationTypes.commonTypes.cli_types.hostnamectl_report import HostnamectlReport
from foundationTypes.commonTypes.cli_types.iptables_report import IptablesReport
from foundationTypes.commonTypes.cli_types.iw_dev_report import IwDevReport
from foundationTypes.commonTypes.cli_types.iwconfig_report import IwconfigReport
from foundationTypes.commonTypes.cli_types.journal_kernel_report import JournalKernelReport
from foundationTypes.commonTypes.cli_types.journal_nm_report import JournalNmReport
from foundationTypes.commonTypes.cli_types.link_brief_report import LinkBriefReport
from foundationTypes.commonTypes.cli_types.link_stats_report import LinkStatsReport
from foundationTypes.commonTypes.cli_types.lsmod_report import LsmodReport
from foundationTypes.commonTypes.cli_types.neighbor_report import NeighborReport
from foundationTypes.commonTypes.cli_types.networkctl_report import NetworkctlReport
from foundationTypes.commonTypes.cli_types.nftables_report import NftablesReport
from foundationTypes.commonTypes.cli_types.nm_service_report import NmServiceReport
from foundationTypes.commonTypes.cli_types.nmcli_active_report import NmcliActiveReport
from foundationTypes.commonTypes.cli_types.nmcli_device_detail_report import NmcliDeviceDetailReport
from foundationTypes.commonTypes.cli_types.nmcli_device_report import NmcliDeviceReport
from foundationTypes.commonTypes.cli_types.nmcli_general_report import NmcliGeneralReport
from foundationTypes.commonTypes.cli_types.os_release_report import OSReleaseReport
from foundationTypes.commonTypes.cli_types.ping_dns_report import PingDNSReport
from foundationTypes.commonTypes.cli_types.ping_v4_report import PingV4Report
from foundationTypes.commonTypes.cli_types.ping_v6_report import PingV6Report
from foundationTypes.commonTypes.cli_types.resolv_conf_report import ResolvConfReport
from foundationTypes.commonTypes.cli_types.resolvectl_report import ResolvectlReport
from foundationTypes.commonTypes.cli_types.rfkill_report import RfkillReport
from foundationTypes.commonTypes.cli_types.route4_report import Route4Report
from foundationTypes.commonTypes.cli_types.route6_report import Route6Report
from foundationTypes.commonTypes.cli_types.routing_rules_report import RoutingRulesReport
from foundationTypes.commonTypes.cli_types.socket_listen_report import SocketListenReport
from foundationTypes.commonTypes.cli_types.socket_summary_report import SocketSummaryReport
from foundationTypes.commonTypes.cli_types.ssh_service_report import SSHServiceReport
from foundationTypes.commonTypes.cli_types.tailscale_netcheck_report import TailscaleNetcheckReport
from foundationTypes.commonTypes.cli_types.tailscale_status_report import TailscaleStatusReport
from foundationTypes.commonTypes.cli_types.timedatectl_report import TimedatectlReport
from foundationTypes.commonTypes.cli_types.uname_report import UnameReport
from foundationTypes.commonTypes.cli_types.uptime_report import UptimeReport
from foundationTypes.data_model_helper import DataModelHelper

_DEFAULT_TIMEOUT_S = 10

_Model = type[DataModelHelper]

# Same command/output on every OS (uname, uptime, /etc/resolv.conf, tailscale JSON).
_CROSS_PLATFORM: tuple[_Model, ...] = (
    UnameReport,
    UptimeReport,
    ResolvConfReport,
    TailscaleStatusReport,
    TailscaleNetcheckReport,
)

# A native command on BOTH macOS and Linux; the per-OS argv/parser is selected in
# the model's wire_config (e.g. ip -brief vs ifconfig, ip route vs netstat -rn).
_PORTABLE: tuple[_Model, ...] = (
    AddressReport,
    AddressBriefReport,
    LinkBriefReport,
    LinkStatsReport,
    Route4Report,
    Route6Report,
    NeighborReport,
    ResolvectlReport,
    OSReleaseReport,
    DmesgReport,
    PingV4Report,
    PingV6Report,
    PingDNSReport,
)

# Linux-only tools with no macOS counterpart; they run on Linux and are simply
# absent from the macOS suite.
_LINUX_ONLY: tuple[_Model, ...] = (
    RoutingRulesReport,
    NmcliGeneralReport,
    NmcliDeviceReport,
    NmcliDeviceDetailReport,
    NmcliActiveReport,
    NetworkctlReport,
    IwDevReport,
    IwconfigReport,
    RfkillReport,
    SocketListenReport,
    SocketSummaryReport,
    NftablesReport,
    IptablesReport,
    JournalKernelReport,
    JournalNmReport,
    LsmodReport,
    NmServiceReport,
    SSHServiceReport,
    HostnamectlReport,
    TimedatectlReport,
)

# The explicit suite per OS. Keyed by platform.system().
_MODELS_BY_SYSTEM: dict[str, tuple[_Model, ...]] = {
    "Linux": _CROSS_PLATFORM + _PORTABLE + _LINUX_ONLY,
    "Darwin": _CROSS_PLATFORM + _PORTABLE,
}


def models_for_system(system: str | None = None) -> tuple[_Model, ...]:
    """Return the command models that run on ``system`` (default: the current OS).

    An unrecognized OS yields an empty suite rather than a guessed one — the suite is
    always something explicitly declared, never inferred.
    """
    return _MODELS_BY_SYSTEM.get(system or platform.system(), ())


class NetworkDiag:
    """Runs the read-only CLI command suite locally and reports the parsed result."""

    def __init__(
        self,
        models: Sequence[_Model] | None = None,
        timeout_s: int = _DEFAULT_TIMEOUT_S,
    ) -> None:
        self.models = tuple(models) if models is not None else models_for_system()
        self.timeout_s = timeout_s

    async def run(self) -> dict[str, object]:
        """Run every model concurrently; return ``{model name: parsed dict | error}``."""
        results = await asyncio.gather(*(self._run_one(model) for model in self.models))
        return dict(results)

    async def _run_one(self, model: _Model) -> tuple[str, object]:
        """Run one model via CLITransact, serializing the parsed model or the failure."""
        result = await CLITransact.run_async_with_model(model, timeout=self.timeout_s)
        if result.success and result.model is not None:
            return model.__name__, result.model.to_dict()
        return model.__name__, {"return_code": result.return_code, "stderr": result.stderr}
