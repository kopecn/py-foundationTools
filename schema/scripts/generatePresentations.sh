#!/bin/bash

set -euo pipefail

# =============================================================================
# Generate Presentations Python types from JSON Schema.
# =============================================================================

# === Input schemas (relative to repo root) ===
INPUT_SCHEMA_FILES=(
  "schema/schemas/Presentations/PresentationColorTheme-schema.json"
  "schema/schemas/Presentations/PresentationMetadata-schema.json"
  "schema/schemas/Presentations/PresentationSlideLayouts-schema.json"
  "schema/schemas/Presentations/PresentationDeck-schema.json"
)

# === Classes that should inherit from DataModelHelper ===
# Every quicktype-generated dataclass, not just the four schema-root classes:
# to_class() (used inside every to_dict()) requires its argument class to be a
# DataModelHelper under mypy --strict, so a nested class reached only via a
# parent's field (e.g. PresentationColor inside PresentationColorTheme) needs
# the base too, the same reasoning that gives generateDiskUsage.sh both
# DiskUsageEntry and DiskUsage here, just at this domain's larger nesting depth.
CLASSES_FOR_BASE_PARENT=(
    "PresentationColor"
    "PresentationAccent"
    "RegionDefaults"
    "Notes"
    "LayoutDefaults"
    "Region"
    "SlideLayout"
    "Defaults"
    "File"
    "ThemeVersion"
    "LayoutVersion"
    "Style"
    "TextRun"
    "ChartSeries"
    "ContentBlock"
    "Slide"
    "PresentationColorTheme"
    "PresentationSlideLayouts"
    "PresentationMetadata"
    "PresentationDeck"
)

# === Output (relative to src/foundationTypes) ===
OUTPUT_PYTHON_REL="presentationTypes/Presentations.py"

# === quicktype target. quicktype only emits up to 3.7; modern typing is
#     restored afterwards by run_ruff (UP rules) + fix_to_dict_return_type. ===
PYTHON_VERSION="3.7"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$SCRIPT_DIR/reuse/codegen.sh"
source "$SCRIPT_DIR/reuse/add_datamodelhelper.sh"

echo "Generating Python types: $OUTPUT_PYTHON_FILE"
echo "    from schemas: ${INPUT_SCHEMA_FILES[*]}"

setup_quicktype
run_quicktype
add_base_class "$OUTPUT_PYTHON_FILE" "${CLASSES_FOR_BASE_PARENT[@]}"
add_helper_imports "$OUTPUT_PYTHON_FILE"
add_autogen_header "$OUTPUT_PYTHON_FILE"
run_ruff "$OUTPUT_PYTHON_FILE"
ensure_py_typed "$OUTPUT_PYTHON_FILE"
