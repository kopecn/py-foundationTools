#!/bin/bash

set -euo pipefail

# =============================================================================
# Generate MermaidDirectives Python types from JSON Schema.
# One script -> one module, per the golden template (generateDiskUsage.sh).
# The cross-cutting `directives` node, split out of the former trunk Mermaid.py
# so the manually-constructed mermaidTop.py can import it from its own file.
# =============================================================================

# === Input schema (relative to repo root) ===
INPUT_SCHEMA_FILES=(
  "schema/schemas/Mermaid/mermaidDirectives-schema.json"
)

# === Classes that should inherit from DataModelHelper ===
CLASSES_FOR_BASE_PARENT=(
  "MermaidDirectives"
)

# === Output (relative to src/foundationTypes) ===
OUTPUT_PYTHON_REL="mermaidTypes/MermaidDirectives.py"

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
