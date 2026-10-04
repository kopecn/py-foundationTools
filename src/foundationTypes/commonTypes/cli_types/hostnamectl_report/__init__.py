"""HostnamectlReport command model package; wire bindings activate on import."""

from . import wire_config  # noqa: F401
from .HostnamectlReport import HostnamectlReport, HostnamectlReportEntry

__all__ = ["HostnamectlReport", "HostnamectlReportEntry"]
