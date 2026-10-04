# =============================================================================
# AUTO-GENERATED FILE — DO NOT EDIT
# Generated from JSON Schema via quicktype. Any manual edits will be
# overwritten the next time codegen runs (make codegen-all).
# To modify, update the source schema in schema/schemas/ and re-run codegen.
# =============================================================================

from dataclasses import dataclass
from foundationTypes.data_model_helper import (
    DataModelHelper,
    from_none,
    from_str,
    from_union,
    to_class,
)
from typing import Optional, Any, TypeVar, Type, cast

T = TypeVar("T")


@dataclass
class PingDNSReport(DataModelHelper):
    """DNS-resolved ping summary (`ping -c N <name>`)."""

    raw: str
    host: Optional[str] = None
    packet_loss: Optional[str] = None
    received: Optional[str] = None
    rtt_avg_ms: Optional[str] = None
    rtt_max_ms: Optional[str] = None
    rtt_min_ms: Optional[str] = None
    transmitted: Optional[str] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "PingDNSReport":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        raw = from_str(obj.get("raw"))
        host = from_union([from_none, from_str], obj.get("host"))
        packet_loss = from_union([from_none, from_str], obj.get("packet_loss"))
        received = from_union([from_none, from_str], obj.get("received"))
        rtt_avg_ms = from_union([from_none, from_str], obj.get("rtt_avg_ms"))
        rtt_max_ms = from_union([from_none, from_str], obj.get("rtt_max_ms"))
        rtt_min_ms = from_union([from_none, from_str], obj.get("rtt_min_ms"))
        transmitted = from_union([from_none, from_str], obj.get("transmitted"))
        return PingDNSReport(
            raw, host, packet_loss, received, rtt_avg_ms, rtt_max_ms, rtt_min_ms, transmitted
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["raw"] = from_str(self.raw)
        if self.host is not None:
            result["host"] = from_union([from_none, from_str], self.host)
        if self.packet_loss is not None:
            result["packet_loss"] = from_union([from_none, from_str], self.packet_loss)
        if self.received is not None:
            result["received"] = from_union([from_none, from_str], self.received)
        if self.rtt_avg_ms is not None:
            result["rtt_avg_ms"] = from_union([from_none, from_str], self.rtt_avg_ms)
        if self.rtt_max_ms is not None:
            result["rtt_max_ms"] = from_union([from_none, from_str], self.rtt_max_ms)
        if self.rtt_min_ms is not None:
            result["rtt_min_ms"] = from_union([from_none, from_str], self.rtt_min_ms)
        if self.transmitted is not None:
            result["transmitted"] = from_union([from_none, from_str], self.transmitted)
        return result


def ping_dns_report_from_dict(s: Any) -> PingDNSReport:
    return PingDNSReport.from_dict(s)


def ping_dns_report_to_dict(x: PingDNSReport) -> Any:
    return to_class(PingDNSReport, x)
