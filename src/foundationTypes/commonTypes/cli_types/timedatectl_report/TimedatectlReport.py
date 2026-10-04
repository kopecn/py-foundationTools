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
from typing import Any, List, TypeVar, Callable, Type, cast

T = TypeVar("T")


@dataclass
class TimedatectlReportEntry(DataModelHelper):
    key: str
    value: str

    @classmethod
    def from_dict(cls, obj: Any) -> "TimedatectlReportEntry":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        key = from_str(obj.get("key"))
        value = from_str(obj.get("value"))
        return TimedatectlReportEntry(key, value)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["key"] = from_str(self.key)
        result["value"] = from_str(self.value)
        return result


@dataclass
class TimedatectlReport(DataModelHelper):
    """timedatectl status as `key: value` fields (clock and time sync state)."""

    entries: List[TimedatectlReportEntry]
    raw: str
    """Verbatim stdout, retained alongside fields."""

    @classmethod
    def from_dict(cls, obj: Any) -> "TimedatectlReport":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        entries = from_list(TimedatectlReportEntry.from_dict, obj.get("entries"))
        raw = from_str(obj.get("raw"))
        return TimedatectlReport(entries, raw)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["entries"] = from_list(lambda x: to_class(TimedatectlReportEntry, x), self.entries)
        result["raw"] = from_str(self.raw)
        return result


def timedatectl_report_from_dict(s: Any) -> TimedatectlReport:
    return TimedatectlReport.from_dict(s)


def timedatectl_report_to_dict(x: TimedatectlReport) -> Any:
    return to_class(TimedatectlReport, x)
