"""NeighborReport command model package; wire bindings activate on import."""

from . import wire_config  # noqa: F401
from .NeighborReport import NeighborReport, NeighborReportRow

__all__ = ["NeighborReport", "NeighborReportRow"]
