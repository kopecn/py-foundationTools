#!/bin/bash

set -euo pipefail

# =============================================================================
# Generate PrecisionTime Python types from JSON Schema.
#
# Emits one module containing the shared enums (NumericSign, Timescale,
# ReferenceFrame) and the underscore-private generated data carriers
# (_PrecisionTimeIntervalType, _PrecisionTimestampType). The public Tier-2
# abstract classes (PrecisionTimeInterval / PrecisionTimestamp) are hand-written
# siblings that inherit these carriers and add the math contract.
# =============================================================================

# === Input schemas (relative to repo root). List all so the $ref'd enums
#     become named top-level types in the output module. ===
INPUT_SCHEMA_FILES=(
  "schema/schemas/Math/NumericSign-schema.json"
  "schema/schemas/Math/Timescale-schema.json"
  "schema/schemas/Math/ReferenceFrame-schema.json"
  "schema/schemas/Math/PrecisionTimeInterval-schema.json"
  "schema/schemas/Math/PrecisionTimestamp-schema.json"
)

# === Classes that should inherit from DataModelHelper. Only the object data
#     carriers; the three enums must NOT inherit DataModelHelper. ===
CLASSES_FOR_BASE_PARENT=(
  "_PrecisionTimeIntervalType"
  "_PrecisionTimestampType"
)

# === Output (relative to src/foundationTypes) ===
OUTPUT_PYTHON_REL="mathTypes/PrecisionTime.py"

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
# quicktype strips leading underscores from type names, so the schema `title`
# "_PrecisionTimeIntervalType" emits as "PrecisionTimeIntervalType". Re-apply the
# private prefix to the generated data carriers (and every reference to them) so
# the clean public names belong to the hand-written Tier-2 ABCs. run_quicktype
# rewrites the file from scratch each run, so this single prefixing is idempotent
# across regenerations.
_sed_inplace \
  's/PrecisionTimeIntervalType/_PrecisionTimeIntervalType/g; s/PrecisionTimestampType/_PrecisionTimestampType/g' \
  "$OUTPUT_PYTHON_FILE"
add_base_class "$OUTPUT_PYTHON_FILE" "${CLASSES_FOR_BASE_PARENT[@]}"
add_helper_imports "$OUTPUT_PYTHON_FILE"
add_autogen_header "$OUTPUT_PYTHON_FILE"
run_ruff "$OUTPUT_PYTHON_FILE"
ensure_py_typed "$OUTPUT_PYTHON_FILE"
