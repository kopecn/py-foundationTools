# =============================================================================
# HAND-MAINTAINED TOP-LEVEL — the Mermaid document root is constructed here, not
# generated. The two cross-cutting nodes (config, directives) are schema-generated
# in their own files and imported below; `DiagramType` (the body discriminator)
# lives here with the root it belongs to.
# =============================================================================

from enum import Enum
from dataclasses import dataclass
from foundationTypes.data_model_helper import (
    DataModelHelper,
    from_dict,
    from_none,
    from_union,
    to_class,
    to_enum,
)
from typing import Optional, Any, Dict, TypeVar

from foundationTypes.mermaidTypes.MermaidConfig import MermaidConfig
from foundationTypes.mermaidTypes.MermaidDirectives import MermaidDirectives

T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


class DiagramType(Enum):
    """The diagram body type. Each value names a body schema that is generated independently in
    its own file. This enum lists every known Mermaid diagram type, including types Mermaid's
    team has not yet fully built out. A value here does not imply that a generated body schema
    exists yet; `flowchart` and `classDiagram` are modeled today, and the rest are added as
    their body types are modeled.
    """

    AGENTFLOW = "agentflow"
    ARCHITECTURE = "architecture"
    BLOCK = "block"
    C4 = "c4"
    CLASS_DIAGRAM = "classDiagram"
    CYNEFIN = "cynefin"
    ENTITY_RELATIONSHIP_DIAGRAM = "entityRelationshipDiagram"
    EVENT_MODELING = "eventmodeling"
    FLOWCHART = "flowchart"
    GANTT = "gantt"
    GIT_GRAPH = "gitgraph"
    ISHIKAWA = "ishikawa"
    KANBAN = "kanban"
    MINDMAP = "mindmap"
    PACKET = "packet"
    PIE = "pie"
    QUADRANT_CHART = "quadrantChart"
    RADAR = "radar"
    RAILROAD = "railroad"
    REQUIREMENT_DIAGRAM = "requirementDiagram"
    SANKEY = "sankey"
    SEQUENCE_DIAGRAM = "sequenceDiagram"
    STATE_DIAGRAM = "stateDiagram"
    SWIMLANES = "swimlanes"
    TIMELINE = "timeline"
    TREEMAP = "treemap"
    TREE_VIEW = "treeView"
    USECASE = "usecase"
    USER_JOURNEY = "userJourney"
    VENN = "venn"
    WARDLEY = "wardley"
    XY_CHART = "xyChart"
    ZENUML = "zenuml"


@dataclass
class Mermaid(DataModelHelper):
    """Top-level schema for a Mermaid diagram document. It gathers the cross-cutting nodes
    (config, directives) a `diagramType` discriminator that names which diagram body applies,
    and a single `body` node that holds it (flowchart first; swimlane, gantt, and the rest
    are added to the `diagramType` enum as they are modeled). Every node is optional.
    Breadcrumbs for the config node: the official config schema is
    https://mermaid.js.org/schemas/config.schema.json and its API docs are
    https://mermaid.js.org/config/schema-docs/config.html . The local
    `mermaidConfig-schema.json` is a copy of that official schema with every `required` array
    removed, because the official `required` describes the fully-resolved runtime config, not
    a partial author config.
    """

    body: Dict[str, Any]
    """The body for the Mermaid diagram."""

    diagram_type: DiagramType
    """The diagram body type. Each value names a body schema that is generated independently in
    its own file. Populated with `flowchart` for now; more values are added as body types are
    modeled.
    """
    config: Optional[MermaidConfig] = None
    """Optional. The Mermaid configuration object (local copy of the official schema, with
    `required` removed).
    """
    directives: Optional[MermaidDirectives] = None
    """Optional. Pre-render directives."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Mermaid":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        body = from_dict(lambda x: x, obj.get("body"))
        diagram_type = DiagramType(obj.get("diagramType"))
        config = from_union([MermaidConfig.from_dict, from_none], obj.get("config"))
        directives = from_union([MermaidDirectives.from_dict, from_none], obj.get("directives"))
        return Mermaid(body, diagram_type, config, directives)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["body"] = from_dict(lambda x: x, self.body)
        result["diagramType"] = to_enum(DiagramType, self.diagram_type)
        if self.config is not None:
            result["config"] = from_union(
                [lambda x: to_class(MermaidConfig, x), from_none], self.config
            )
        if self.directives is not None:
            result["directives"] = from_union(
                [lambda x: to_class(MermaidDirectives, x), from_none], self.directives
            )
        return result


def mermaid_from_dict(s: Any) -> Mermaid:
    return Mermaid.from_dict(s)


def mermaid_to_dict(x: Mermaid) -> Any:
    return to_class(Mermaid, x)
