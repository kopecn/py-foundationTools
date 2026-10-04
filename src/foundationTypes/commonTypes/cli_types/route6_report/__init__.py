"""Route6Report command model package; wire bindings activate on import."""

from . import wire_config  # noqa: F401
from .Route6Report import Route6Report, Route6ReportRow

__all__ = ["Route6Report", "Route6ReportRow"]
