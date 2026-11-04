#!/bin/bash

set -euo pipefail

# =============================================================================
# Generate MermaidConfig Python types from JSON Schema.
# One script -> one module, per the golden template (generateDiskUsage.sh).
# The cross-cutting `config` node, split out of the former trunk Mermaid.py so
# the manually-constructed mermaidTop.py can import it from its own file. The
# config schema is a local copy of the official Mermaid config schema (with
# `required` removed) and emits MermaidConfig plus a large tree of per-diagram
# nested config classes; every one needs the DataModelHelper base.
# =============================================================================

# === Input schema (relative to repo root) ===
INPUT_SCHEMA_FILES=(
  "schema/schemas/Mermaid/mermaidConfig-schema.json"
)

# === Classes that should inherit from DataModelHelper ===
# MermaidConfig plus every nested per-diagram config class quicktype emits from
# the config $ref tree (to_class() requires its argument class to be a
# DataModelHelper under mypy --strict).
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
)

# === Output (relative to src/foundationTypes) ===
OUTPUT_PYTHON_REL="mermaidTypes/MermaidConfig.py"

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
