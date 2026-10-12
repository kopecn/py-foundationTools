#!/bin/bash

set -euo pipefail

# =============================================================================
# Generate Mermaid Python types from JSON Schema.
# =============================================================================

# === Input schemas (relative to repo root) ===
# One module, fed by the trunk schema. quicktype resolves the trunk's $refs
# (mermaidConfig-schema.json, mermaidDirectives-schema.json) by following them
# from this entry file, so only the trunk is listed here. The per-type body
# schemas (e.g. diagrams/flowchart-schema.json) are generated independently in
# their own files; the trunk names them only through the `diagramType` enum.
INPUT_SCHEMA_FILES=(
  "schema/schemas/Mermaid/mermaid-schema.json"
)

# === Classes that should inherit from DataModelHelper ===
# Every quicktype-generated dataclass, not just the schema-root class: to_class()
# (used inside every to_dict()) requires its argument class to be a
# DataModelHelper under mypy --strict, so a nested class reached only via a
# parent's field needs the base too (same reasoning as generatePresentations.sh).
#
# The config node ($ref mermaidConfig-schema.json) emits MermaidConfig plus a
# large tree of per-diagram nested config classes; every one needs the base.
CLASSES_FOR_BASE_PARENT=(
    "AgentflowDiagramConfig"
    "ArchitectureDiagramConfig"
    "BlockDiagramConfig"
    "C4DiagramConfig"
    "ClassDiagramConfig"
    "CynefinDiagramConfig"
    "Elk"
    "ErDiagramConfig"
    "EventModelingDiagramConfig"
    "FlowchartDiagramConfig"
    "GanttDiagramConfig"
    "GitGraphDiagramConfig"
    "IshikawaDiagramConfig"
    "JourneyDiagramConfig"
    "KanbanDiagramConfig"
    "MindmapDiagramConfig"
    "NodeLabel"
    "PacketDiagramConfig"
    "PieDiagramConfig"
    "QuadrantChartConfig"
    "RadarDiagramConfig"
    "RailroadDiagramConfig"
    "RequirementDiagramConfig"
    "SankeyDiagramConfig"
    "SequenceDiagramConfig"
    "StateDiagramConfig"
    "SubGraphTitleMargin"
    "SwimlaneDiagramConfig"
    "TimelineDiagramConfig"
    "TreeViewDiagramConfig"
    "UsecaseDiagramConfig"
    "VennDiagramConfig"
    "WardleyDiagramConfig"
    "XYChartAxisConfig"
    "XYChartConfig"
    "MermaidConfig"
    "MermaidDirectives"
    "Mermaid"
)

# === Output (relative to src/foundationTypes) ===
OUTPUT_PYTHON_REL="mermaidTypes/Mermaid.py"

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
