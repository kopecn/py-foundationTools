# =============================================================================
# AUTO-GENERATED FILE — DO NOT EDIT
# Generated from JSON Schema via quicktype. Any manual edits will be
# overwritten the next time codegen runs (make codegen-all).
# To modify, update the source schema in schema/schemas/ and re-run codegen.
# =============================================================================

from dataclasses import dataclass
from foundationTypes.data_model_helper import (
    DataModelHelper,
    from_list,
    from_none,
    from_str,
    from_union,
    to_class,
)
from typing import Optional, Any, List, TypeVar, Callable, Type, cast

T = TypeVar("T")


@dataclass
class Route6ReportRow(DataModelHelper):
    destination: str
    raw: str
    dev: Optional[str] = None
    metric: Optional[str] = None
    proto: Optional[str] = None
    via: Optional[str] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "Route6ReportRow":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        destination = from_str(obj.get("destination"))
        raw = from_str(obj.get("raw"))
        dev = from_union([from_none, from_str], obj.get("dev"))
        metric = from_union([from_none, from_str], obj.get("metric"))
        proto = from_union([from_none, from_str], obj.get("proto"))
        via = from_union([from_none, from_str], obj.get("via"))
        return Route6ReportRow(destination, raw, dev, metric, proto, via)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["destination"] = from_str(self.destination)
        result["raw"] = from_str(self.raw)
        if self.dev is not None:
            result["dev"] = from_union([from_none, from_str], self.dev)
        if self.metric is not None:
            result["metric"] = from_union([from_none, from_str], self.metric)
        if self.proto is not None:
            result["proto"] = from_union([from_none, from_str], self.proto)
        if self.via is not None:
            result["via"] = from_union([from_none, from_str], self.via)
        return result


@dataclass
class Route6Report(DataModelHelper):
    """IPv6 routes from `ip -6 route show`; fields best-effort, full line retained."""

    raw: str
    """Verbatim stdout, retained alongside rows."""

    rows: List[Route6ReportRow]

    @classmethod
    def from_dict(cls, obj: Any) -> "Route6Report":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        raw = from_str(obj.get("raw"))
        rows = from_list(Route6ReportRow.from_dict, obj.get("rows"))
        return Route6Report(raw, rows)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["raw"] = from_str(self.raw)
        result["rows"] = from_list(lambda x: to_class(Route6ReportRow, x), self.rows)
        return result


def route6_report_from_dict(s: Any) -> Route6Report:
    return Route6Report.from_dict(s)


def route6_report_to_dict(x: Route6Report) -> Any:
    return to_class(Route6Report, x)
