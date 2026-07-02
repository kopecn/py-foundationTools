#!/bin/bash

set -euo pipefail

# =============================================================================
# Generate MathTypes Python types from JSON Schema.
#
# Consolidates every Math-domain schema whose $ref dependency graph forms one
# connected component into a single quicktype invocation / single output module
# (quicktype resolves $ref only within one invocation, and one invocation emits
# exactly one .py file). Supersedes generatePrecisionTime.sh,
# generateUnitSphericalArc.sh and generateUnitSphericalSmallCircle.sh.
#
# The Math family uses the 3-tier architecture in .claude/specs/mathTypeTiers.md:
# each generated Tier-1 `XxxxType` dataclass inherits its hand-written Tier-2
# `XxxxLike` abstraction. quicktype knows nothing about that, so the Math-specific
# post-processor (reuse/postprocess_mathtypes.py) reparents the classes, extracts
# the enums to mathEnums, imports the dataModelHelper helpers, and injects the
# literal field defaults required for a dataclass to satisfy inherited abstract
# `@property` accessors. from_dict/to_dict normalization is the shared run_ruff pass.
# =============================================================================

# === Input schemas (relative to repo root). Listed leaf-dependency-first for
#     readability; quicktype's --src-lang schema resolves the full $ref graph and
#     is not order-sensitive. ===
INPUT_SCHEMA_FILES=(
  "schema/schemas/Math/NumericSign-schema.json"
  "schema/schemas/Math/Timescale-schema.json"
  "schema/schemas/Math/ReferenceFrame-schema.json"
  "schema/schemas/Math/PrecisionTimeInterval-schema.json"
  "schema/schemas/Math/PrecisionTimestamp-schema.json"
  "schema/schemas/Math/PositionVector-schema.json"
  "schema/schemas/Math/Quaternion-schema.json"
  "schema/schemas/Math/UnitSphericalArc-schema.json"
  "schema/schemas/Math/UnitSphericalSmallCircle-schema.json"
  "schema/schemas/Math/SpatialPose-schema.json"
  "schema/schemas/Math/PositionWaveform-schema.json"
  "schema/schemas/Math/QuaternionWaveform-schema.json"
  "schema/schemas/Math/SpatialPoseWaveform-schema.json"
  "schema/schemas/Math/ScalarWaveform-schema.json"
  "schema/schemas/Math/UnitSphericalArcWaveform-schema.json"
  "schema/schemas/Math/UnitSphericalSmallCircleWaveform-schema.json"
)

# === Output (relative to src/foundationTypes) ===
OUTPUT_PYTHON_REL="mathTypes/MathTypes.py"

# === quicktype target. quicktype only emits up to 3.7; modern typing is restored
#     afterwards by run_ruff (UP rules) + fix_to_dict_return_type. ===
PYTHON_VERSION="3.7"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$SCRIPT_DIR/reuse/codegen.sh"

echo "Generating Python types: $OUTPUT_PYTHON_FILE"
echo "    from schemas: ${INPUT_SCHEMA_FILES[*]}"

setup_quicktype
run_quicktype
# Math-specific rewrite: reparent XxxxType -> XxxxLike, extract enums, import
# helpers, inject the literal field defaults the Tier-2 accessors require.
python3 "$SCRIPT_DIR/reuse/postprocess_mathtypes.py" "$OUTPUT_PYTHON_FILE"
add_autogen_header "$OUTPUT_PYTHON_FILE"
run_ruff "$OUTPUT_PYTHON_FILE"
ensure_py_typed "$OUTPUT_PYTHON_FILE"
