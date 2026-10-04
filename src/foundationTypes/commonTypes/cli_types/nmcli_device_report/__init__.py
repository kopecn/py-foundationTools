"""NmcliDeviceReport command model package; wire bindings activate on import."""

from . import wire_config  # noqa: F401
from .NmcliDeviceReport import NmcliDeviceReport, NmcliDeviceReportRow

__all__ = ["NmcliDeviceReport", "NmcliDeviceReportRow"]
