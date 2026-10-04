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
class LsmodReportRow(DataModelHelper):
    module: str
    size: str
    used_by: List[str]
    used_by_count: str

    @classmethod
    def from_dict(cls, obj: Any) -> "LsmodReportRow":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        module = from_str(obj.get("module"))
        size = from_str(obj.get("size"))
        used_by = from_list(from_str, obj.get("used_by"))
        used_by_count = from_str(obj.get("used_by_count"))
        return LsmodReportRow(module, size, used_by, used_by_count)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["module"] = from_str(self.module)
        result["size"] = from_str(self.size)
        result["used_by"] = from_list(from_str, self.used_by)
        result["used_by_count"] = from_str(self.used_by_count)
        return result


@dataclass
class LsmodReport(DataModelHelper):
    """Loaded kernel modules from `lsmod` (header dropped)."""

    raw: str
    """Verbatim stdout, retained alongside rows."""

    rows: List[LsmodReportRow]

    @classmethod
    def from_dict(cls, obj: Any) -> "LsmodReport":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        raw = from_str(obj.get("raw"))
        rows = from_list(LsmodReportRow.from_dict, obj.get("rows"))
        return LsmodReport(raw, rows)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["raw"] = from_str(self.raw)
        result["rows"] = from_list(lambda x: to_class(LsmodReportRow, x), self.rows)
        return result


def lsmod_report_from_dict(s: Any) -> LsmodReport:
    return LsmodReport.from_dict(s)


def lsmod_report_to_dict(x: LsmodReport) -> Any:
    return to_class(LsmodReport, x)
