"""
Examples demonstrating data model usage with CLI transactions.

This module showcases:
1. Basic data model serialization and file I/O
2. CLI transactions with automatic data model parsing
3. Asynchronous CLI execution with model serialization
4. Custom serializer concepts

The examples use the DiskUsage model with df -h command to demonstrate
how CLI output can be automatically parsed into structured data models.
"""

import asyncio
from pathlib import Path

from foundation_tools.cli_transaction.cliTransact import CLITransact
from foundationTypes.commonTypes.DiskUsage import DiskUsage
from foundationTypes.commonTypes.GeoCoordinate import GeoCoordinate


def example_basic_datamodel():
    """Demonstrate basic data model serialization with GeoCoordinate."""
    print("=== Basic Data Model Example ===")

    aCoordfile = Path.home().joinpath("acoord.json")

    # Create and save a coord
    geoCoord = GeoCoordinate(3.1, 2.3)
    geoCoord.save_to_file(aCoordfile)

    # load and validate the coord
    reloadedCoord = GeoCoordinate.load_from_file(aCoordfile)
    print(f"Original: {geoCoord}")
    print(f"Reloaded: {reloadedCoord}")
    coords_match = (
        geoCoord.latitude == reloadedCoord.latitude
        and geoCoord.longitude == reloadedCoord.longitude
    )
    print(f"Coordinates match: {coords_match}")

    if aCoordfile.exists() and aCoordfile.is_file():
        aCoordfile.unlink()
    print()


def example_cli_with_datamodel():
    """Demonstrate CLI transaction with automatic data model serialization."""
    print("=== CLI Transaction with Data Model Example ===")

    # Execute df -h command and automatically parse into DiskUsage model
    result = CLITransact.run_sync_with_model("df -h", DiskUsage.from_df_output)

    print(f"Command success: {result.success}")
    print(f"Return code: {result.return_code}")

    if result.model:
        print(f"Parsed {len(result.model.entries)} filesystem entries:")

        # Show first 3 entries as example
        for i, entry in enumerate(result.model.entries[:3]):
            print(f"  {i + 1}. {entry.filesystem}")
            print(f"     Size: {entry.size}, Used: {entry.used}, Available: {entry.available}")
            print(f"     Usage: {entry.use_percent}, Mounted: {entry.mounted_on}")

        if len(result.model.entries) > 3:
            print(f"  ... and {len(result.model.entries) - 3} more entries")

        # Demonstrate serialization to dict/JSON
        disk_data = result.model.to_dict()
        print(f"\nModel serializes to dictionary with {len(disk_data['entries'])} entries")

        # Round-trip test
        reconstructed = DiskUsage.from_dict(disk_data)
        roundtrip_ok = len(reconstructed.entries) == len(result.model.entries)
        print(f"Round-trip serialization successful: {roundtrip_ok}")
    else:
        print("No model data was parsed")
        if result.stderr:
            print(f"Error: {result.stderr}")
    print()


async def example_async_cli_with_datamodel():
    """Demonstrate asynchronous CLI transaction with data model serialization."""
    print("=== Async CLI Transaction with Data Model Example ===")

    result = await CLITransact.run_async_with_model("df -h", DiskUsage.from_df_output)

    print(f"Async command success: {result.success}")

    if result.model:
        # Find the largest filesystem by size
        largest_entry = None
        for entry in result.model.entries:
            if entry.size != "0Bi" and (
                largest_entry is None
                or entry.size.replace("Gi", "").replace("Mi", "").replace("Ki", "")
                > largest_entry.size.replace("Gi", "").replace("Mi", "").replace("Ki", "")
            ):
                largest_entry = entry

        if largest_entry:
            print(f"Largest filesystem: {largest_entry.filesystem}")
            print(f"  Size: {largest_entry.size}, Usage: {largest_entry.use_percent}")
            print(f"  Mounted at: {largest_entry.mounted_on}")
    print()


def example_custom_serializer():
    """Demonstrate custom serializer for simple command output."""
    print("=== Custom Serializer Example ===")

    # Simple serializer that just counts lines
    def count_lines(output: str) -> int:
        return len(output.strip().split("\n")) if output else 0

    # This won't work directly since count_lines doesn't return DataModelHelper
    # But shows the concept of custom serializers
    result = CLITransact.run_sync("ls -la")
    if result.success and result.stdout:
        line_count = count_lines(result.stdout)
        print(f"Command 'ls -la' produced {line_count} lines of output")
    print()


if __name__ == "__main__":
    print("Data Model Examples\n" + "=" * 50)

    # Basic data model usage
    example_basic_datamodel()

    # CLI with data model serialization
    example_cli_with_datamodel()

    # Async CLI with data model
    asyncio.run(example_async_cli_with_datamodel())

    # Custom serializer concept
    example_custom_serializer()

    print("All examples completed!")
