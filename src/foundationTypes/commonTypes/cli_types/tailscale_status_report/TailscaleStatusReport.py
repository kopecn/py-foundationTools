# =============================================================================
# AUTO-GENERATED FILE — DO NOT EDIT
# Generated from JSON Schema via quicktype. Any manual edits will be
# overwritten the next time codegen runs (make codegen-all).
# To modify, update the source schema in schema/schemas/ and re-run codegen.
# =============================================================================

from dataclasses import dataclass
from foundationTypes.data_model_helper import (
    DataModelHelper,
    from_dict,
    to_class,
)
from typing import Dict, Any, TypeVar, Callable, Type, cast

T = TypeVar("T")


@dataclass
class TailscaleStatusReport(DataModelHelper):
    """Tailscale backend/peer state (tailscale status --json), fed through as a structured
    object.
    """

    response: Dict[str, Any]
    """The tool's JSON output, parsed and fed through unchanged."""

    @classmethod
    def from_dict(cls, obj: Any) -> "TailscaleStatusReport":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        response = from_dict(lambda x: x, obj.get("response"))
        return TailscaleStatusReport(response)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["response"] = from_dict(lambda x: x, self.response)
        return result


def tailscale_status_report_from_dict(s: Any) -> TailscaleStatusReport:
    return TailscaleStatusReport.from_dict(s)


def tailscale_status_report_to_dict(x: TailscaleStatusReport) -> Any:
    return to_class(TailscaleStatusReport, x)
