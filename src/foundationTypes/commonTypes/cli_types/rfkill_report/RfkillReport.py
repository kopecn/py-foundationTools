# =============================================================================
# AUTO-GENERATED FILE — DO NOT EDIT
# Generated from JSON Schema via quicktype. Any manual edits will be
# overwritten the next time codegen runs (make codegen-all).
# To modify, update the source schema in schema/schemas/ and re-run codegen.
# =============================================================================

from dataclasses import dataclass
from foundationTypes.data_model_helper import (
    DataModelHelper,
    from_str,
    to_class,
)
from typing import Any, TypeVar, Type, cast

T = TypeVar("T")


@dataclass
class RfkillReport(DataModelHelper):
    """Radio soft/hard block state (`rfkill list`), verbatim."""

    raw: str
    """Verbatim stdout captured from the command."""

    @classmethod
    def from_dict(cls, obj: Any) -> "RfkillReport":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        raw = from_str(obj.get("raw"))
        return RfkillReport(raw)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["raw"] = from_str(self.raw)
        return result


def rfkill_report_from_dict(s: Any) -> RfkillReport:
    return RfkillReport.from_dict(s)


def rfkill_report_to_dict(x: RfkillReport) -> Any:
    return to_class(RfkillReport, x)
