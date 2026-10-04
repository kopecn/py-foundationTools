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
class NmcliDeviceReportRow(DataModelHelper):
    device: str
    state: str
    type: str
    connection: Optional[str] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "NmcliDeviceReportRow":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        device = from_str(obj.get("device"))
        state = from_str(obj.get("state"))
        type = from_str(obj.get("type"))
        connection = from_union([from_none, from_str], obj.get("connection"))
        return NmcliDeviceReportRow(device, state, type, connection)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["device"] = from_str(self.device)
        result["state"] = from_str(self.state)
        result["type"] = from_str(self.type)
        if self.connection is not None:
            result["connection"] = from_union([from_none, from_str], self.connection)
        return result


@dataclass
class NmcliDeviceReport(DataModelHelper):
    """Per-device managed state from `nmcli device status`."""

    raw: str
    """Verbatim stdout, retained alongside rows."""

    rows: List[NmcliDeviceReportRow]

    @classmethod
    def from_dict(cls, obj: Any) -> "NmcliDeviceReport":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        raw = from_str(obj.get("raw"))
        rows = from_list(NmcliDeviceReportRow.from_dict, obj.get("rows"))
        return NmcliDeviceReport(raw, rows)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["raw"] = from_str(self.raw)
        result["rows"] = from_list(lambda x: to_class(NmcliDeviceReportRow, x), self.rows)
        return result


def nmcli_device_report_from_dict(s: Any) -> NmcliDeviceReport:
    return NmcliDeviceReport.from_dict(s)


def nmcli_device_report_to_dict(x: NmcliDeviceReport) -> Any:
    return to_class(NmcliDeviceReport, x)
