#!/bin/bash

set -euo pipefail

# =============================================================================
# Generate DiskUsage Python types from JSON Schema.
# =============================================================================

# === Input schemas (relative to repo root) ===
INPUT_SCHEMA_FILES=(
  "schema/schemas/DiskUsage-schema.json"
)

# === Classes that should inherit from DataModelHelper ===
CLASSES_FOR_BASE_PARENT=(
    "DiskUsageEntry"
    "DiskUsage"
)

# === Output (relative to src/foundationTypes) ===
OUTPUT_PYTHON_REL="commonTypes/disk_usage/DiskUsage.py"

# === quicktype target. quicktype only emits up to 3.7; modern typing is
#     restored afterwards by fix_to_dict_return_type + normalization passes. ===
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
run_black "$OUTPUT_PYTHON_FILE"
ensure_py_typed "$OUTPUT_PYTHON_FILE"
