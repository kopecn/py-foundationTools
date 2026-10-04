#!/bin/bash

set -euo pipefail

# =============================================================================
# Generate Route4Report Python types from JSON Schema (CLI-tool command model).
# One script -> one module, per the golden template (generateDiskUsage.sh).
# =============================================================================

# === Input schema (relative to repo root) ===
INPUT_SCHEMA_FILES=(
  "schema/schemas/CLITools/Route4Report-schema.json"
)

# === Classes that should inherit from DataModelHelper ===
CLASSES_FOR_BASE_PARENT=(
  "Route4Report"
  "Route4ReportRow"
)

# === Output (relative to src/foundationTypes) ===
OUTPUT_PYTHON_REL="commonTypes/cli_types/route4_report/Route4Report.py"

# === quicktype target (quicktype's ceiling; modern typing restored afterwards). ===
PYTHON_VERSION="3.7"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$SCRIPT_DIR/../reuse/codegen.sh"
source "$SCRIPT_DIR/../reuse/add_datamodelhelper.sh"

echo "Generating Python types: $OUTPUT_PYTHON_FILE"
echo "    from schemas: ${INPUT_SCHEMA_FILES[*]}"

setup_quicktype
run_quicktype
add_base_class "$OUTPUT_PYTHON_FILE" "${CLASSES_FOR_BASE_PARENT[@]}"
add_helper_imports "$OUTPUT_PYTHON_FILE"
add_autogen_header "$OUTPUT_PYTHON_FILE"
run_black "$OUTPUT_PYTHON_FILE"
ensure_py_typed "$OUTPUT_PYTHON_FILE"
