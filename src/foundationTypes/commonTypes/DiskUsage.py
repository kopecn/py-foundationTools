"""
Data model for parsing disk usage information from df command output.

This module provides structured data models for representing filesystem
disk usage data, compatible with both Linux and macOS df command formats.
"""

from dataclasses import dataclass
from typing import Any, TypeVar, Type, cast, List, Optional

from foundationTypes.dataModelHelper import DataModelHelper


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_optional_str(x: Any) -> Optional[str]:
    return from_str(x) if x is not None else None


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class DiskUsageEntry(DataModelHelper):
    """A single disk usage entry from df -h output"""

    filesystem: str
    size: str
    used: str
    available: str
    use_percent: str
    mounted_on: str

    @staticmethod
    def from_dict(obj: Any) -> "DiskUsageEntry":
        assert isinstance(obj, dict)
        filesystem = from_str(obj.get("filesystem"))
        size = from_str(obj.get("size"))
        used = from_str(obj.get("used"))
        available = from_str(obj.get("available"))
        use_percent = from_str(obj.get("use_percent"))
        mounted_on = from_str(obj.get("mounted_on"))
        return DiskUsageEntry(
            filesystem, size, used, available, use_percent, mounted_on
        )

    def to_dict(self) -> dict:
        result: dict = {}
        result["filesystem"] = from_str(self.filesystem)
        result["size"] = from_str(self.size)
        result["used"] = from_str(self.used)
        result["available"] = from_str(self.available)
        result["use_percent"] = from_str(self.use_percent)
        result["mounted_on"] = from_str(self.mounted_on)
        return result


@dataclass
class DiskUsage(DataModelHelper):
    """Collection of disk usage entries parsed from df -h output"""

    entries: List[DiskUsageEntry]

    @staticmethod
    def from_dict(obj: Any) -> "DiskUsage":
        assert isinstance(obj, dict)
        entries = [DiskUsageEntry.from_dict(y) for y in obj.get("entries", [])]
        return DiskUsage(entries)

    def to_dict(self) -> dict:
        result: dict = {}
        result["entries"] = [to_class(DiskUsageEntry, x) for x in self.entries]
        return result

    @staticmethod
    def from_df_output(output: str) -> "DiskUsage":
        """
        Parse df -h command output into a DiskUsage data model.

        Expected format (Linux):
        Filesystem      Size  Used Avail Use% Mounted on
        /dev/disk1s5s1  500G  250G  250G  50% /
        devfs           192K  192K     0 100% /dev

        Expected format (macOS with -h):
        Filesystem                         Size    Used   Avail Capacity iused ifree %iused  Mounted on
        /dev/disk3s1s1                    926Gi    10Gi   360Gi     3%    426k  3.8G    0%   /

        Args:
            output: Raw string output from df -h command

        Returns:
            DiskUsage object containing parsed entries
        """
        lines = output.strip().split("\n")

        # Skip header line
        if not lines or len(lines) < 2:
            return DiskUsage([])

        entries = []

        # Parse each data line
        for line in lines[1:]:
            # Split on whitespace, handling multiple spaces
            parts = line.split()

            # Skip malformed lines - need at least filesystem, size, used, avail, capacity, mounted
            if len(parts) < 6:
                continue

            # Detect if this is macOS format (has extra inode columns) or Linux format
            # macOS: filesystem size used avail capacity iused ifree %iused mounted_on (9+ columns)
            # Linux: filesystem size used avail use% mounted_on (6+ columns)

            if len(parts) >= 9:
                # macOS format with inode info
                if len(parts) > 9:
                    # Handle cases where filesystem or mount point might contain spaces
                    filesystem = " ".join(parts[:-8])
                    size, used, available, use_percent = parts[-8:-4]
                    mounted_on = " ".join(
                        parts[-1:]
                    )  # Only take the last part as mount point
                else:
                    filesystem, size, used, available, use_percent = (
                        parts[0],
                        parts[1],
                        parts[2],
                        parts[3],
                        parts[4],
                    )
                    mounted_on = parts[8]
            else:
                # Linux format or simpler format
                if len(parts) > 6:
                    filesystem = " ".join(parts[:-5])
                    size, used, available, use_percent, mounted_on = parts[-5:]
                else:
                    filesystem, size, used, available, use_percent, mounted_on = parts[
                        0:6
                    ]

            entry = DiskUsageEntry(
                filesystem=filesystem,
                size=size,
                used=used,
                available=available,
                use_percent=use_percent,
                mounted_on=mounted_on,
            )
            entries.append(entry)

        return DiskUsage(entries)


def disk_usage_from_dict(s: Any) -> DiskUsage:
    return DiskUsage.from_dict(s)


def disk_usage_to_dict(x: DiskUsage) -> Any:
    return to_class(DiskUsage, x)
