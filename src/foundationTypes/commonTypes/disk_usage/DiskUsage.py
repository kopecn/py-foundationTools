# =============================================================================
# AUTO-GENERATED FILE — DO NOT EDIT
# Generated from JSON Schema via quicktype. Any manual edits will be
# overwritten the next time codegen runs (make codegen-all).
# To modify, update the source schema in schema/schemas/ and re-run codegen.
# =============================================================================

from dataclasses import dataclass
from typing import Any, TypeVar

from foundationTypes.data_model_helper import (
    DataModelHelper,
    from_list,
    from_str,
    to_class,
)

T = TypeVar("T")


@dataclass
class DiskUsageEntry(DataModelHelper):
    """A single disk usage entry from df -h output"""

    available: str
    """Space still available on the filesystem, human-readable with df -h's unit suffix."""

    filesystem: str
    """The mounted device or source (e.g. /dev/disk3s5, devfs, map auto_home) as reported in
    df's first column.
    """
    mounted_on: str
    """Filesystem mount point (e.g. /, /System/Volumes/Data)."""

    size: str
    """Total size of the filesystem, human-readable with df -h's unit suffix (e.g. 926Gi, 500G)."""

    use_percent: str
    """Used space as a percentage of total capacity, including the trailing '%' (e.g. 70%)."""

    used: str
    """Space currently used on the filesystem, human-readable with df -h's unit suffix."""

    @classmethod
    def from_dict(cls, obj: Any) -> "DiskUsageEntry":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        available = from_str(obj.get("available"))
        filesystem = from_str(obj.get("filesystem"))
        mounted_on = from_str(obj.get("mounted_on"))
        size = from_str(obj.get("size"))
        use_percent = from_str(obj.get("use_percent"))
        used = from_str(obj.get("used"))
        return DiskUsageEntry(available, filesystem, mounted_on, size, use_percent, used)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["available"] = from_str(self.available)
        result["filesystem"] = from_str(self.filesystem)
        result["mounted_on"] = from_str(self.mounted_on)
        result["size"] = from_str(self.size)
        result["use_percent"] = from_str(self.use_percent)
        result["used"] = from_str(self.used)
        return result


@dataclass
class DiskUsage(DataModelHelper):
    """Collection of disk usage entries parsed from df -h output"""

    entries: list[DiskUsageEntry]

    @classmethod
    def from_dict(cls, obj: Any) -> "DiskUsage":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        entries = from_list(DiskUsageEntry.from_dict, obj.get("entries"))
        return DiskUsage(entries)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["entries"] = from_list(lambda x: to_class(DiskUsageEntry, x), self.entries)
        return result


def disk_usage_from_dict(s: Any) -> DiskUsage:
    return DiskUsage.from_dict(s)


def disk_usage_to_dict(x: DiskUsage) -> Any:
    return to_class(DiskUsage, x)
