"""LinkBriefReport command model package; wire bindings activate on import."""

from . import wire_config  # noqa: F401
from .LinkBriefReport import LinkBriefReport, LinkBriefReportRow

__all__ = ["LinkBriefReport", "LinkBriefReportRow"]
