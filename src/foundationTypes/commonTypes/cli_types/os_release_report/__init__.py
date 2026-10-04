"""OSReleaseReport command model package; wire bindings activate on import."""

from . import wire_config  # noqa: F401
from .OSReleaseReport import OSReleaseReport, OSReleaseReportEntry

__all__ = ["OSReleaseReport", "OSReleaseReportEntry"]
