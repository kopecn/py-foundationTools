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
class NeighborReportRow(DataModelHelper):
    address: str
    raw: str
    state: str
    dev: Optional[str] = None
    lladdr: Optional[str] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "NeighborReportRow":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        address = from_str(obj.get("address"))
        raw = from_str(obj.get("raw"))
        state = from_str(obj.get("state"))
        dev = from_union([from_none, from_str], obj.get("dev"))
        lladdr = from_union([from_none, from_str], obj.get("lladdr"))
        return NeighborReportRow(address, raw, state, dev, lladdr)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["address"] = from_str(self.address)
        result["raw"] = from_str(self.raw)
        result["state"] = from_str(self.state)
        if self.dev is not None:
            result["dev"] = from_union([from_none, from_str], self.dev)
        if self.lladdr is not None:
            result["lladdr"] = from_union([from_none, from_str], self.lladdr)
        return result


@dataclass
class NeighborReport(DataModelHelper):
    """ARP/NDP neighbor entries from `ip neigh show`."""

    raw: str
    """Verbatim stdout, retained alongside rows."""

    rows: List[NeighborReportRow]

    @classmethod
    def from_dict(cls, obj: Any) -> "NeighborReport":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        raw = from_str(obj.get("raw"))
        rows = from_list(NeighborReportRow.from_dict, obj.get("rows"))
        return NeighborReport(raw, rows)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["raw"] = from_str(self.raw)
        result["rows"] = from_list(lambda x: to_class(NeighborReportRow, x), self.rows)
        return result


def neighbor_report_from_dict(s: Any) -> NeighborReport:
    return NeighborReport.from_dict(s)


def neighbor_report_to_dict(x: NeighborReport) -> Any:
    return to_class(NeighborReport, x)
