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
class IptablesReport(DataModelHelper):
    """iptables rules (`iptables -S`), verbatim."""

    raw: str
    """Verbatim stdout captured from the command."""

    @classmethod
    def from_dict(cls, obj: Any) -> "IptablesReport":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        raw = from_str(obj.get("raw"))
        return IptablesReport(raw)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["raw"] = from_str(self.raw)
        return result


def iptables_report_from_dict(s: Any) -> IptablesReport:
    return IptablesReport.from_dict(s)


def iptables_report_to_dict(x: IptablesReport) -> Any:
    return to_class(IptablesReport, x)
