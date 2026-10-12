#!/bin/bash

set -euo pipefail

# =============================================================================
# Generate ClassDiagram Python types from JSON Schema (Mermaid diagram body).
# One script -> one diagram type, per the golden template (generateDiskUsage.sh).
# This folder mirrors schema/schemas/Mermaid/diagrams/: one script per diagram
# schema, each emitting a single file into mermaidTypes/diagrams/.
# =============================================================================

# === Input schema (relative to repo root) ===
INPUT_SCHEMA_FILES=(
  "schema/schemas/Mermaid/diagrams/classDiagram.schema.json"
)

# === Classes that should inherit from DataModelHelper ===
# The top class is driven by the --out basename (ClassDiagram). Nested dataclasses
# emitted by this schema must be appended here after the first successful run
# (read them off the generated file), exactly as generateFlowchartDiagram.sh lists
# its nested classes.
CLASSES_FOR_BASE_PARENT=(
  "ClassDiagram"
)

# === Output (relative to src/foundationTypes) ===
OUTPUT_PYTHON_REL="mermaidTypes/diagrams/ClassDiagram.py"

# === quicktype target (quicktype's ceiling; modern typing restored afterwards). ===
PYTHON_VERSION="3.7"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$SCRIPT_DIR/../../reuse/codegen.sh"
source "$SCRIPT_DIR/../../reuse/add_datamodelhelper.sh"

echo "Generating Python types: $OUTPUT_PYTHON_FILE"
echo "    from schemas: ${INPUT_SCHEMA_FILES[*]}"

setup_quicktype
run_quicktype
add_base_class "$OUTPUT_PYTHON_FILE" "${CLASSES_FOR_BASE_PARENT[@]}"
add_helper_imports "$OUTPUT_PYTHON_FILE"
add_autogen_header "$OUTPUT_PYTHON_FILE"
run_black "$OUTPUT_PYTHON_FILE"
ensure_py_typed "$OUTPUT_PYTHON_FILE"
