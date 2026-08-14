"""Wire protocol configuration for DiskUsage.

Assigns wire_encode/wire_decode so DataModelHelper.to_wire()/from_wire() route
to the df -h text format, and wire_invoke so CLITransact.run_sync_with_model
(DiskUsage) can run "df -h" and parse it without a separate command or
output_parser argument.
"""

from __future__ import annotations

from foundationTypes.commonTypes.disk_usage.DiskUsage import DiskUsage

_HEADER = "Filesystem      Size  Used Avail Use% Mounted on"


def _wire_encode(self: DiskUsage, **kwargs: object) -> str:
    lines = [_HEADER]
    for entry in self.entries:
        lines.append(
            f"{entry.filesystem} {entry.size} {entry.used} "
            f"{entry.available} {entry.use_percent} {entry.mounted_on}"
        )
    return "\n".join(lines)


def _wire_decode(cls: type[DiskUsage], wire_str: str) -> DiskUsage:
    lines = wire_str.strip().split("\n")

    if not lines or len(lines) < 2:
        return cls.from_dict({"entries": []})

    entries: list[dict[str, str]] = []

    for line in lines[1:]:
        # Split on whitespace, handling multiple spaces.
        parts = line.split()

        # Skip malformed lines - need at least filesystem, size, used, avail,
        # capacity, mounted.
        if len(parts) < 6:
            continue

        # Detect if this is macOS format (has extra inode columns) or Linux
        # format.
        # macOS: filesystem size used avail capacity iused ifree %iused
        #        mounted_on (9+ columns)
        # Linux: filesystem size used avail use% mounted_on (6+ columns)
        if len(parts) >= 9:
            if len(parts) > 9:
                filesystem = " ".join(parts[:-8])
                size, used, available, use_percent = parts[-8:-4]
                mounted_on = " ".join(parts[-1:])
            else:
                filesystem, size, used, available, use_percent = parts[:5]
                mounted_on = parts[8]
        else:
            if len(parts) > 6:
                filesystem = " ".join(parts[:-5])
                size, used, available, use_percent, mounted_on = parts[-5:]
            else:
                filesystem, size, used, available, use_percent, mounted_on = parts[:6]

        entries.append(
            {
                "filesystem": filesystem,
                "size": size,
                "used": used,
                "available": available,
                "use_percent": use_percent,
                "mounted_on": mounted_on,
            }
        )

    return cls.from_dict({"entries": entries})


DiskUsage.wire_encode = _wire_encode
DiskUsage.wire_decode = _wire_decode
DiskUsage.wire_invoke = ["df", "-h"]
