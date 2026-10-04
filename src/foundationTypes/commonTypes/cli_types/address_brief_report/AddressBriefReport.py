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
    from_str,
    to_class,
)
from typing import List, Any, TypeVar, Callable, Type, cast

T = TypeVar("T")


@dataclass
class AddressBriefReportRow(DataModelHelper):
    addresses: List[str]
    ifname: str
    operstate: str

    @classmethod
    def from_dict(cls, obj: Any) -> "AddressBriefReportRow":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        addresses = from_list(from_str, obj.get("addresses"))
        ifname = from_str(obj.get("ifname"))
        operstate = from_str(obj.get("operstate"))
        return AddressBriefReportRow(addresses, ifname, operstate)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["addresses"] = from_list(from_str, self.addresses)
        result["ifname"] = from_str(self.ifname)
        result["operstate"] = from_str(self.operstate)
        return result


@dataclass
class AddressBriefReport(DataModelHelper):
    """One row per link from `ip -brief address show`."""

    raw: str
    """Verbatim stdout, retained alongside rows."""

    rows: List[AddressBriefReportRow]

    @classmethod
    def from_dict(cls, obj: Any) -> "AddressBriefReport":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        raw = from_str(obj.get("raw"))
        rows = from_list(AddressBriefReportRow.from_dict, obj.get("rows"))
        return AddressBriefReport(raw, rows)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["raw"] = from_str(self.raw)
        result["rows"] = from_list(lambda x: to_class(AddressBriefReportRow, x), self.rows)
        return result


def address_brief_report_from_dict(s: Any) -> AddressBriefReport:
    return AddressBriefReport.from_dict(s)


def address_brief_report_to_dict(x: AddressBriefReport) -> Any:
    return to_class(AddressBriefReport, x)
