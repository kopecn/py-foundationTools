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
class OSReleaseReportEntry(DataModelHelper):
    key: str
    value: str

    @classmethod
    def from_dict(cls, obj: Any) -> "OSReleaseReportEntry":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        key = from_str(obj.get("key"))
        value = from_str(obj.get("value"))
        return OSReleaseReportEntry(key, value)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["key"] = from_str(self.key)
        result["value"] = from_str(self.value)
        return result


@dataclass
class OSReleaseReport(DataModelHelper):
    """Parsed /etc/os-release KEY=VALUE pairs (distribution identity)."""

    entries: List[OSReleaseReportEntry]
    raw: str
    """Verbatim stdout, retained alongside fields."""

    @classmethod
    def from_dict(cls, obj: Any) -> "OSReleaseReport":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        entries = from_list(OSReleaseReportEntry.from_dict, obj.get("entries"))
        raw = from_str(obj.get("raw"))
        return OSReleaseReport(entries, raw)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["entries"] = from_list(lambda x: to_class(OSReleaseReportEntry, x), self.entries)
        result["raw"] = from_str(self.raw)
        return result


def os_release_report_from_dict(s: Any) -> OSReleaseReport:
    return OSReleaseReport.from_dict(s)


def os_release_report_to_dict(x: OSReleaseReport) -> Any:
    return to_class(OSReleaseReport, x)
