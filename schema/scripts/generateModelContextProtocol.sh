#!/bin/bash

# === Input Schemas ===
INPUT_SCHEMA_FILES=(
  "schema/schemas/ModelContextProtocolTypes-schema.json"
  "schema/schemas/MCP/ModelContextProtocol-2025-06-18-schema.json"
)

# === Output Directory ===
OUTPUT_PYTHON_FILE="src/foundationTypes/commonTypes/ModelContextProtocol.py"

# === Quicktype Arguements ===
PYTHON_VERSION="3.7"

echo "Attempting to generate python types: $OUTPUT_PYTHON_FILE"
echo "    from schemas: $INPUT_SCHEMA_FILES"

setup_and_run_quicktype() {
  # === Setting up correct Directory for script to operate ===
  # Get the directory where this script is located and CD to root of project
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  cd "$SCRIPT_DIR" || return 1
  cd ../.. || return 1
  echo "DataModel generation directory running from: $(pwd)"
  
  quicktype -v
}

run_quicktype() {
    # Run quicktype
    quicktype \
    --lang py \
    --src-lang schema \
    --python-version "$PYTHON_VERSION" \
    --out "$OUTPUT_PYTHON_FILE" \
    --telemetry disable \
    --no-pydantic-base-model \
    "${INPUT_SCHEMA_FILES[@]}"

    echo "✅ Generated: $output_file"

    echo "🎉 All specified schemas have been converted to Python classes."
}

add_base_class() {
    local file="$1"
    local base_class="DataModelHelper"

    sed -i '' '/^from dataclasses import dataclass$/a\
from foundationTypes.dataModelHelper import DataModelHelper
    ' "$file"

    if sed --version >/dev/null 2>&1; then
        # GNU sed (Linux)
        sed -i "s/^class \([A-Za-z0-9_]*\):$/class \1($base_class):/" "$file"
    else
        # BSD sed (macOS)
        sed -i '' "s/^class \([A-Za-z0-9_]*\):$/class \1($base_class):/" "$file"
    fi
}

run_black() {
    black "$OUTPUT_PYTHON_FILE"
}


setup_and_run_quicktype
run_quicktype
add_base_class "$OUTPUT_PYTHON_FILE"
run_black