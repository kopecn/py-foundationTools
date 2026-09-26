"""Usage examples for DataModelHelper models: a file I/O round trip, and CLI output
parsed straight into a model via its wire_invoke/from_wire."""

import asyncio
from pathlib import Path

from foundation_tools.cli_transaction.cliTransact import CLITransact
from foundationTypes.commonTypes.disk_usage.DiskUsage import DiskUsage
from foundationTypes.commonTypes.GeoCoordinate import GeoCoordinate

print("---- GeoCoordinate save / load round trip ----")
coord_file = Path.home() / "acoord.json"
coord = GeoCoordinate(3.1, 2.3)
coord.save_to_file(coord_file)
reloaded = GeoCoordinate.load_from_file(coord_file)
print(f"original={coord} reloaded={reloaded}")
coord_file.unlink(missing_ok=True)

print("\n---- DiskUsage from a CLI transaction ----")
# DiskUsage declares its own wire_invoke (["df", "-h"]); the model class alone
# runs the command and parses stdout via DiskUsage.from_wire.
result = CLITransact.run_sync_with_model(DiskUsage)
print(f"success={result.success}")
if result.model:
    print(f"parsed {len(result.model.entries)} filesystem entries")
    for entry in result.model.entries[:3]:
        print(f"  {entry.filesystem}: {entry.size} used={entry.used} on {entry.mounted_on}")

print("\n---- DiskUsage async ----")
result = asyncio.run(CLITransact.run_async_with_model(DiskUsage))
entries = len(result.model.entries) if result.model else 0
print(f"success={result.success} entries={entries}")
