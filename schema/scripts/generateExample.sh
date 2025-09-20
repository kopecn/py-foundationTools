#!/bin/bash

# === Input Schemas ===
INPUT_SCHEMA_FILES=(
  "schema/schemas/Coordinate.json"
)

# === Output Directory ===
OUTPUT_PYTHON_FILE="src/dataModelHelpers/commonTypes/Coordinate.py"

# === Quicktype Arguements ===
PYTHON_VERSION="3.7"

echo "Attempting to generate python types: $OUTPUT_PYTHON_FILE"
echo "    from schemas: $INPUT_SCHEMA_FILES"

# === Setting up correct Directory for script to operate ===
# Get the directory where this script is located and CD to root of project
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
cd ../..
echo "DataModel generation directory running from: $(pwd)"
quicktype -v


# Run quicktype
quicktype \
--lang py \
--src-lang schema \
--python-version "$PYTHON_VERSION" \
--just-types \
--out "$output_file" \
--telemetry disable \
--no-pydantic-base-model \
"$schema_file"

echo "✅ Generated: $output_file"

echo "🎉 All specified schemas have been converted to Python classes."

# # === Ensure Output Directory Exists ===
# mkdir -p "$OUTPUT_DIR"

# # === Loop Over Explicit Files ===
# for schema_file in "${SCHEMA_FILES[@]}"; do
#   # Ensure the schema file exists
#   if [[ ! -f "$schema_file" ]]; then
#     echo "⚠️  Skipping missing file: $schema_file"
#     continue
#   fi

#   # Get the base name (e.g., user_schema.json → user_schema)
#   base_name=$(basename "$schema_file" .json)

#   # Set output file path
#   output_file="$OUTPUT_DIR/${base_name}.py"
