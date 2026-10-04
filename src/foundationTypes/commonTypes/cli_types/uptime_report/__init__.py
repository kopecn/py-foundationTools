"""UptimeReport command model package; wire bindings activate on import."""

from . import wire_config  # noqa: F401
from .UptimeReport import UptimeReport

__all__ = ["UptimeReport"]
