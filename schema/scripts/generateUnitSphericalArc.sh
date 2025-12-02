#!/bin/bash

# === Input Schemas ===
INPUT_SCHEMA_FILES=(
  "schema/schemas/Math/UnitSphericalArc-schema.json"
)
CLASSES_FOR_BASE_PARENT=(
    "UnitSphericalArc"
)

# === Output Directory ===
OUTPUT_PYTHON_FILE="src/foundationTypes/mathTypes/UnitSphericalArc.py"

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
    "$INPUT_SCHEMA_FILES"

    echo "✅ Generated: $output_file"

    echo "🎉 All specified schemas have been converted to Python classes."
}

add_base_class() {
    local file="$1"
    shift
    local base_class="DataModelHelper"
    local classes=("$@")

    sed -i '' '/^from dataclasses import dataclass$/a\
from foundationTypes.dataModelHelper import DataModelHelper
    ' "$file"

    for class in "${classes[@]}"; do
        if sed --version >/dev/null 2>&1; then
            # GNU sed (Linux)
            sed -i "s/^class $class:$/class $class($base_class):/" "$file"
        else
            # BSD sed (macOS)
            sed -i '' "s/^class $class:$/class $class($base_class):/" "$file"
        fi
    done
}

run_black() {
    black "$OUTPUT_PYTHON_FILE"
}


setup_and_run_quicktype
run_quicktype
add_base_class "$OUTPUT_PYTHON_FILE" "${CLASSES_FOR_BASE_PARENT[@]}"
run_black