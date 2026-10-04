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
from typing import List, Optional, Any, TypeVar, Callable, Type, cast

T = TypeVar("T")


@dataclass
class LinkBriefReportRow(DataModelHelper):
    flags: List[str]
    ifname: str
    operstate: str
    mac: Optional[str] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "LinkBriefReportRow":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        flags = from_list(from_str, obj.get("flags"))
        ifname = from_str(obj.get("ifname"))
        operstate = from_str(obj.get("operstate"))
        mac = from_union([from_none, from_str], obj.get("mac"))
        return LinkBriefReportRow(flags, ifname, operstate, mac)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["flags"] = from_list(from_str, self.flags)
        result["ifname"] = from_str(self.ifname)
        result["operstate"] = from_str(self.operstate)
        if self.mac is not None:
            result["mac"] = from_union([from_none, from_str], self.mac)
        return result


@dataclass
class LinkBriefReport(DataModelHelper):
    """One row per link from `ip -brief link show`."""

    raw: str
    """Verbatim stdout, retained alongside rows."""

    rows: List[LinkBriefReportRow]

    @classmethod
    def from_dict(cls, obj: Any) -> "LinkBriefReport":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        raw = from_str(obj.get("raw"))
        rows = from_list(LinkBriefReportRow.from_dict, obj.get("rows"))
        return LinkBriefReport(raw, rows)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["raw"] = from_str(self.raw)
        result["rows"] = from_list(lambda x: to_class(LinkBriefReportRow, x), self.rows)
        return result


def link_brief_report_from_dict(s: Any) -> LinkBriefReport:
    return LinkBriefReport.from_dict(s)


def link_brief_report_to_dict(x: LinkBriefReport) -> Any:
    return to_class(LinkBriefReport, x)
