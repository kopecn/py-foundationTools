#!/bin/bash

set -euo pipefail

# =============================================================================
# Generate RobotConfig Python types from JSON Schema.
# =============================================================================

# === Input schemas (relative to repo root) ===
# The root file's $ref chain pulls in every file under schema/schemas/Robot/
# (Common/, Units/, Geometry/, Mechanism/, Structure/, Joints/, Constraints/,
# Composition/, Kinematics/); quicktype resolves those relative $refs itself.
INPUT_SCHEMA_FILES=(
  "schema/schemas/Robot/robot-mechanism.schema.json"
)

# === Classes that should inherit from DataModelHelper ===
# (every non-enum dataclass quicktype emits from the Robot/ schema family;
# the root class is named after OUTPUT_PYTHON_REL's stem, not the schema's
# own "MechanismDefinition" title -- see generation notes.)
#
# The geometry carriers (Position/Quaternion/SpatialTransform) are NOT listed:
# Robot geometry $refs the canonical Math schemas, so quicktype inlines those
# carriers and postprocess_robotconfig.py strips them, importing the already-
# parented Math carriers from foundationTypes.mathTypes.MathTypes and retyping
# Robot fields to the foundation_abc.math protocols. See mathTypeTiers.md.
CLASSES_FOR_BASE_PARENT=(
    "RobotConfig"
    "Mount"
    "QuantityClass"
    "Inertia"
    "Body"
    "Classification"
    "Connection"
    "Constraint"
    "Frame"
    "Interface"
    "JointCoordinate"
    "Joint"
    "KinematicRepresentation"
    "Kinematics"
    "Units"
    "Component"
)

# === Output (relative to src/foundationTypes) ===
OUTPUT_PYTHON_REL="automationTypes/RobotConfig.py"

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
# Robot-specific rewrite: strip the inlined Math geometry carriers, retype Robot
# fields to the foundation_abc.math protocols, and import the concrete carriers
# (for construction) from mathTypes. Runs before base-class/helper injection.
python3 "$SCRIPT_DIR/reuse/postprocess_robotconfig.py" "$OUTPUT_PYTHON_FILE"
add_base_class "$OUTPUT_PYTHON_FILE" "${CLASSES_FOR_BASE_PARENT[@]}"
add_helper_imports "$OUTPUT_PYTHON_FILE"
add_autogen_header "$OUTPUT_PYTHON_FILE"
run_black "$OUTPUT_PYTHON_FILE"
ensure_py_typed "$OUTPUT_PYTHON_FILE"
