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
class SocketListenReportRow(DataModelHelper):
    local_address: str
    netid: str
    peer_address: str
    recv_q: str
    send_q: str
    state: str
    process: Optional[str] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "SocketListenReportRow":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        local_address = from_str(obj.get("local_address"))
        netid = from_str(obj.get("netid"))
        peer_address = from_str(obj.get("peer_address"))
        recv_q = from_str(obj.get("recv_q"))
        send_q = from_str(obj.get("send_q"))
        state = from_str(obj.get("state"))
        process = from_union([from_none, from_str], obj.get("process"))
        return SocketListenReportRow(
            local_address, netid, peer_address, recv_q, send_q, state, process
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["local_address"] = from_str(self.local_address)
        result["netid"] = from_str(self.netid)
        result["peer_address"] = from_str(self.peer_address)
        result["recv_q"] = from_str(self.recv_q)
        result["send_q"] = from_str(self.send_q)
        result["state"] = from_str(self.state)
        if self.process is not None:
            result["process"] = from_union([from_none, from_str], self.process)
        return result


@dataclass
class SocketListenReport(DataModelHelper):
    """Listening sockets from `ss -tulpnH` (header suppressed)."""

    raw: str
    """Verbatim stdout, retained alongside rows."""

    rows: List[SocketListenReportRow]

    @classmethod
    def from_dict(cls, obj: Any) -> "SocketListenReport":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        raw = from_str(obj.get("raw"))
        rows = from_list(SocketListenReportRow.from_dict, obj.get("rows"))
        return SocketListenReport(raw, rows)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["raw"] = from_str(self.raw)
        result["rows"] = from_list(lambda x: to_class(SocketListenReportRow, x), self.rows)
        return result


def socket_listen_report_from_dict(s: Any) -> SocketListenReport:
    return SocketListenReport.from_dict(s)


def socket_listen_report_to_dict(x: SocketListenReport) -> Any:
    return to_class(SocketListenReport, x)
