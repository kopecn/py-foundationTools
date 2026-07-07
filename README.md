# pyFoundationTools

A comprehensive collection of Python foundation utilities designed to extend the standard library with zero external dependencies. This library provides robust, reusable components for common programming patterns including CLI operations, data model management, mathematical utilities, and structured data types.

## Features

### 🔧 CLI Transaction Management (`foundation_tools.cli_transaction`)
- **Synchronous & Asynchronous execution** - Run shell commands with both sync and async support
- **Timeout handling** - Built-in timeout management for long-running commands
- **Success validation** - Optional success string validation for command output
- **Structured results** - Type-safe result objects with return codes, stdout, stderr
- **Model parsing** - Direct parsing of command output into structured data models

### 📊 Data Model Helpers (`foundationTypes`)
- **Base DataModelHelper class** - Foundation for JSON-serializable data models
- **File I/O operations** - Save/load data models to/from JSON files
- **Type-safe serialization** - Robust dictionary conversion with type validation
- **Common data types**:
  - `GeoCoordinate` - Geographical coordinate handling
  - `DiskUsage` - Parse and structure `df` command output
  - `ModelContextProtocol` - Protocol for model context management
- **Mathematical data types** (`mathTypes`):
  - `UnitSphericalSmallCircle` - Small circles on unit spheres using spherical coordinates
  - `UnitSphericalArc` - Arcs on unit spheres with orientation and arc length
  - `QuaternionType` - Abstract base class for quaternion representations (3D rotations)

### 🧮 Mathematical Utilities (`foundation_math`)
- **Clamping functions** - Constrain values within specified bounds with validation
- **Pure Python implementation** - No external mathematical dependencies

## Installation

```bash
pip install pyFoundationTools
```

## Quick Start

### CLI Operations
```python
from foundation_tools.cli_transaction.cliTransact import CLITransact

# Basic command execution (stateless classmethods)
result = CLITransact.run_sync("ls -la")
if result.success:
    print(result.stdout)

# With success validation (per-call marker)
result = CLITransact.run_sync("./deploy.sh", success_marker="deployment complete")

# Async execution with timeout
import asyncio
async def main():
    result = await CLITransact.run_async(["python", "script.py"], timeout=30)
    return result

# Parse command output into structured data
from foundationTypes.commonTypes.DiskUsage import DiskUsage
result = CLITransact.run_sync_with_model("df -h", DiskUsage.from_df_output)
if result.success and result.model:
    for entry in result.model.entries:
        print(f"{entry.filesystem}: {entry.use_percent} used")
```

### Data Model Management
```python
from foundationTypes.data_model_helper import DataModelHelper
from foundationTypes.commonTypes.GeoCoordinate import GeoCoordinate
from pathlib import Path
import json

# Create and serialize coordinates
coord = GeoCoordinate(latitude=40.7128, longitude=-74.0060)
coord.saveToFile(Path("location.json"))

# Load from file
loaded_coord = GeoCoordinate.loadFromFile(Path("location.json"))
print(f"Location: {loaded_coord.latitude}, {loaded_coord.longitude}")
```

### Mathematical Utilities
```python
from foundation_math.math import clamp

# Constrain values within bounds
value = clamp(150, 0, 100)  # Returns 100
safe_percentage = clamp(user_input, 0.0, 100.0)
```

### Mathematical Data Types
```python
import math
from foundationTypes.mathTypes.UnitSphericalSmallCircle import UnitSphericalSmallCircle
from foundationTypes.mathTypes.UnitSphericalArc import UnitSphericalArc
from foundationTypes.mathTypes.QuaternionType import QuaternionType

# Create a small circle on a unit sphere
circle = UnitSphericalSmallCircle(
    azimuth=0.0,              # Longitudinal position (0 to 2*pi)
    polar=math.pi / 4,        # Latitudinal position (-pi/2 to pi/2)
    radius_angle=math.pi / 6  # Angular radius
)

# Serialize to JSON
circle_dict = circle.to_dict()
# Save to file
circle.saveToFile(Path("circle.json"))

# Create an arc on a unit sphere
arc = UnitSphericalArc(
    arc_length=math.pi / 2,  # Arc length in radians
    azimuth=math.pi / 4,     # Starting longitudinal position
    orient=0.0,              # Rotational orientation
    polar=0.0                # Starting latitudinal position
)

# Use QuaternionType as base for custom quaternion implementations
# (Subclass and implement the abstract methods)
```

## Development Workflows

This project includes a comprehensive Makefile to streamline development workflows. Use `make help` to see all available commands.

### 🚀 Quick Development Setup
```bash
make devInstall    # Install development dependencies
make e             # Install package in editable mode
```

### 🧪 Testing & Quality Assurance
```bash
make test          # Run tests in current environment
make testInEnv     # Run tests in isolated virtual environment
make uv-fullCheck  # Run complete quality checks (lint + typecheck + test)
make lint          # Run pylint on source code
make uv-typecheck  # Run mypy type checking
make format        # Format code with black
```

### 📦 Building & Distribution
```bash
make build         # Build source and wheel distributions
make dist          # Create distribution packages
make version       # Display current version
make tag           # Create and push git tag for current version
```

### 🚀 Release Management
```bash
make releaseTest   # Upload to TestPyPI for testing
make release       # Upload to PyPI (production)
```

### 🧹 Cleanup
```bash
make clean         # Remove all build, test, and Python artifacts
make cleanBuild    # Remove only build artifacts
make cleanTest     # Remove only test outputs
```

### 📖 Documentation
```bash
make docs          # Build HTML documentation with Sphinx
```

### 🔄 Version Management
```bash
make bumpPatch     # Increment patch version (x.x.X)
make bumpMinor     # Increment minor version (x.X.x)
make bumpMajor     # Increment major version (X.x.x)
```

## Design Philosophy

- **Zero external dependencies** - Only uses Python standard library
- **Type safety** - Comprehensive type hints and validation
- **Error handling** - Robust error management with structured results
- **Async support** - Modern async/await patterns where applicable
- **Extensible** - Base classes and protocols for easy extension

## Requirements

- Python >= 3.10
- No external dependencies
