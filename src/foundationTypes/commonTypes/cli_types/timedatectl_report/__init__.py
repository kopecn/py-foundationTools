"""TimedatectlReport command model package; wire bindings activate on import."""

from . import wire_config  # noqa: F401
from .TimedatectlReport import TimedatectlReport, TimedatectlReportEntry

__all__ = ["TimedatectlReport", "TimedatectlReportEntry"]
