# =============================================================================
# AUTO-GENERATED FILE — DO NOT EDIT
# Generated from JSON Schema via quicktype. Any manual edits will be
# overwritten the next time codegen runs (make codegen-all).
# To modify, update the source schema in schema/schemas/ and re-run codegen.
# =============================================================================

from dataclasses import dataclass
from foundationTypes.data_model_helper import (
    DataModelHelper,
    from_bool,
    from_float,
    from_int,
    from_list,
    from_none,
    from_str,
    from_union,
    to_class,
    to_enum,
    to_float,
)
from typing import Optional, Any, List, TypeVar, Callable, Type, cast
from enum import Enum

T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


@dataclass
class ClassDefElement:
    """A named style class (Mermaid `classDef name style`), bound to nodes and relationships by
    name through their `classes` field.
    """

    name: str
    """The class name referenced by a node or relationship `classes` entry. The reserved name
    `default` applies to every node without an explicit class.
    """
    style: Optional[str] = None
    """The style declarations, comma-separated as Mermaid writes them, e.g.
    `fill:#f9f,stroke:#333,stroke-width:4px`.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ClassDefElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        name = from_str(obj.get("name"))
        style = from_union([from_str, from_none], obj.get("style"))
        return ClassDefElement(name, style)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        if self.style is not None:
            result["style"] = from_union([from_str, from_none], self.style)
        return result


@dataclass
class LinkStyleElement:
    """A link styling by definition order (Mermaid `linkStyle`), distinct from class binding."""

    style: str
    """The style declarations, comma-separated as Mermaid writes them, e.g.
    `stroke:#ff3,stroke-width:4px,color:red`.
    """
    default: Optional[bool] = None
    """Apply the style to all links (Mermaid `linkStyle default ...`) instead of specific
    indices.
    """
    indices: Optional[List[int]] = None
    """The zero-based order indices of the links this style applies to (the Nth link defined in
    the diagram).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "LinkStyleElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        style = from_str(obj.get("style"))
        default = from_union([from_bool, from_none], obj.get("default"))
        indices = from_union([lambda x: from_list(from_int, x), from_none], obj.get("indices"))
        return LinkStyleElement(style, default, indices)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["style"] = from_str(self.style)
        if self.default is not None:
            result["default"] = from_union([from_bool, from_none], self.default)
        if self.indices is not None:
            result["indices"] = from_union(
                [lambda x: from_list(from_int, x), from_none], self.indices
            )
        return result


class Form(Enum):
    """The background shape behind the icon. Omitted means no background."""

    CIRCLE = "circle"
    ROUNDED = "rounded"
    SQUARE = "square"


class Pos(Enum):
    """The label position, top or bottom. Defaults to bottom."""

    B = "b"
    T = "t"


@dataclass
class Icon:
    """An icon node (Mermaid `@{ icon: ... }`). Requires a registered icon pack."""

    icon: str
    """The icon name from the registered icon pack, e.g. `fa:user`."""

    form: Optional[Form] = None
    """The background shape behind the icon. Omitted means no background."""

    h: Optional[float] = None
    """The icon height. Defaults to 48, which is the minimum."""

    label: Optional[str] = None
    """The text label for the icon. Omitted means no label."""

    pos: Optional[Pos] = None
    """The label position, top or bottom. Defaults to bottom."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Icon":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        icon = from_str(obj.get("icon"))
        form = from_union([Form, from_none], obj.get("form"))
        h = from_union([from_float, from_none], obj.get("h"))
        label = from_union([from_str, from_none], obj.get("label"))
        pos = from_union([Pos, from_none], obj.get("pos"))
        return Icon(icon, form, h, label, pos)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["icon"] = from_str(self.icon)
        if self.form is not None:
            result["form"] = from_union([lambda x: to_enum(Form, x), from_none], self.form)
        if self.h is not None:
            result["h"] = from_union([to_float, from_none], self.h)
        if self.label is not None:
            result["label"] = from_union([from_str, from_none], self.label)
        if self.pos is not None:
            result["pos"] = from_union([lambda x: to_enum(Pos, x), from_none], self.pos)
        return result


class Constraint(Enum):
    """Whether the image constrains the node size and keeps its aspect ratio. Defaults to off."""

    OFF = "off"
    ON = "on"


@dataclass
class Image:
    """An image node (Mermaid `@{ img: ... }`)."""

    img: str
    """The URL of the image to display."""

    constraint: Optional[Constraint] = None
    """Whether the image constrains the node size and keeps its aspect ratio. Defaults to off."""

    h: Optional[float] = None
    """The image height. Defaults to the natural height."""

    label: Optional[str] = None
    """The text label for the image. Omitted means no label."""

    pos: Optional[Pos] = None
    """The label position, top or bottom. Defaults to bottom."""

    w: Optional[float] = None
    """The image width. Defaults to the natural width."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Image":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        img = from_str(obj.get("img"))
        constraint = from_union([Constraint, from_none], obj.get("constraint"))
        h = from_union([from_float, from_none], obj.get("h"))
        label = from_union([from_str, from_none], obj.get("label"))
        pos = from_union([Pos, from_none], obj.get("pos"))
        w = from_union([from_float, from_none], obj.get("w"))
        return Image(img, constraint, h, label, pos, w)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["img"] = from_str(self.img)
        if self.constraint is not None:
            result["constraint"] = from_union(
                [lambda x: to_enum(Constraint, x), from_none], self.constraint
            )
        if self.h is not None:
            result["h"] = from_union([to_float, from_none], self.h)
        if self.label is not None:
            result["label"] = from_union([from_str, from_none], self.label)
        if self.pos is not None:
            result["pos"] = from_union([lambda x: to_enum(Pos, x), from_none], self.pos)
        if self.w is not None:
            result["w"] = from_union([to_float, from_none], self.w)
        return result


class Shape(Enum):
    """A Mermaid node shape, named by its descriptive geometry (v11.3.0+). These are readable
    names, not the literal `@{ shape: <name> }` tokens Mermaid accepts; a mapping to those
    short tokens is still needed before this is referenced by the main schema.
    """

    BOW_TIE_RECTANGLE = "bowTieRectangle"
    BRACES = "braces"
    BRACE_RIGHT = "braceRight"
    CIRCLE = "circle"
    COMMENT = "comment"
    CROSSED_CIRCLE = "crossedCircle"
    CURVED_TRAPEZOID = "curvedTrapezoid"
    CYLINDER = "cylinder"
    DATASTORE = "datastore"
    DELAY = "delay"
    DIAMOND = "diamond"
    DIRECT_ACCESS_STORAGE = "directAccessStorage"
    DIVIDED_RECTANGLE = "dividedRectangle"
    DOCUMENT = "document"
    DOUBLE_CIRCLE = "doubleCircle"
    FILLED_CIRCLE = "filledCircle"
    FLAG = "flag"
    FLIPPED_TRIANGLE = "flippedTriangle"
    FORK = "fork"
    FRAMED_CIRCLE = "framedCircle"
    HEXAGON = "hexagon"
    HOURGLASS = "hourglass"
    LEAN_LEFT = "leanLeft"
    LEAN_RIGHT = "leanRight"
    LIGHTNING_BOLT = "lightningBolt"
    LINED_CYLINDER = "linedCylinder"
    LINED_DOCUMENT = "linedDocument"
    LINED_RECTANGLE = "linedRectangle"
    NOTCHED_PENTAGON = "notchedPentagon"
    NOTCHED_RECTANGLE = "notchedRectangle"
    ODD = "odd"
    RECTANGLE = "rectangle"
    ROUNDED = "rounded"
    SLOPED_RECTANGLE = "slopedRectangle"
    SMALL_CIRCLE = "smallCircle"
    STACKED_DOCUMENT = "stackedDocument"
    STACKED_RECTANGLE = "stackedRectangle"
    STADIUM = "stadium"
    SUBPROCESS = "subprocess"
    TAGGED_DOCUMENT = "taggedDocument"
    TAGGED_RECTANGLE = "taggedRectangle"
    TEXT = "text"
    TRAPEZOID_BASE_BOTTOM = "trapezoidBaseBottom"
    TRAPEZOID_BASE_TOP = "trapezoidBaseTop"
    TRIANGLE = "triangle"
    WINDOW_PANE = "windowPane"


@dataclass
class NodeElement:
    """A flowchart node. Populated incrementally with the attributes that make up a node."""

    id: str
    """The node's identifier, used to reference it from relationships."""

    classes: Optional[List[str]] = None
    """Names of classDefs applied to this node (Mermaid `class`/`:::`). Each entry must match a
    classDefs[].name.
    """
    icon: Optional[Icon] = None
    image: Optional[Image] = None
    markdown: Optional[bool] = None
    """Whether text is a Markdown string. When true the renderer encloses it in double quotes
    and backticks (e.g. id["`This **is** _Markdown_`"]), enabling bold/italics, automatic
    wrapping, and newline-based line breaks. Defaults to false (plain text).
    """
    shape: Optional[Shape] = None
    text: Optional[str] = None
    """The display text in the node box, differing from the id. Stored as a raw Unicode string;
    the renderer quotes it (Mermaid requires double quotes around Unicode text, e.g. id["This
    ❤ Unicode"]). When text is defined several times for a node, Mermaid uses the last
    definition.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "NodeElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_str(obj.get("id"))
        classes = from_union([lambda x: from_list(from_str, x), from_none], obj.get("classes"))
        icon = from_union([Icon.from_dict, from_none], obj.get("icon"))
        image = from_union([Image.from_dict, from_none], obj.get("image"))
        markdown = from_union([from_bool, from_none], obj.get("markdown"))
        shape = from_union([Shape, from_none], obj.get("shape"))
        text = from_union([from_str, from_none], obj.get("text"))
        return NodeElement(id, classes, icon, image, markdown, shape, text)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_str(self.id)
        if self.classes is not None:
            result["classes"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.classes
            )
        if self.icon is not None:
            result["icon"] = from_union([lambda x: to_class(Icon, x), from_none], self.icon)
        if self.image is not None:
            result["image"] = from_union([lambda x: to_class(Image, x), from_none], self.image)
        if self.markdown is not None:
            result["markdown"] = from_union([from_bool, from_none], self.markdown)
        if self.shape is not None:
            result["shape"] = from_union([lambda x: to_enum(Shape, x), from_none], self.shape)
        if self.text is not None:
            result["text"] = from_union([from_str, from_none], self.text)
        return result


class Orientation(Enum):
    """The orientation of the graph. `TB` top to bottom; `TD` top-down (same as top to bottom);
    `BT` bottom to top; `RL` right to left; `LR` left to right.
    """

    BT = "BT"
    LR = "LR"
    RL = "RL"
    TB = "TB"
    TD = "TD"


class Animation(Enum):
    """The animation speed; setting it implies animate:true."""

    FAST = "fast"
    SLOW = "slow"


class Curve(Enum):
    """The curve style for a link's line."""

    BASIS = "basis"
    BUMP_X = "bumpX"
    BUMP_Y = "bumpY"
    CARDINAL = "cardinal"
    CATMULL_ROM = "catmullRom"
    LINEAR = "linear"
    MONOTONE_X = "monotoneX"
    MONOTONE_Y = "monotoneY"
    NATURAL = "natural"
    STEP = "step"
    STEP_AFTER = "stepAfter"
    STEP_BEFORE = "stepBefore"


class LinkType(Enum):
    """A Mermaid flowchart link (edge) kind, named by the connection it draws. These are
    readable names, not the literal Mermaid operators (`-->`, `---`, `-.->`, `==>`, `~~~`,
    `--o`, `--x`, `o--o`, `<-->`, `x--x`); a mapping to those operators is still needed
    before this is referenced by the main schema.
    """

    ARROW = "arrow"
    CIRCLE_EDGE = "circleEdge"
    CROSS_EDGE = "crossEdge"
    DOTTED = "dotted"
    INVISIBLE = "invisible"
    MULTI_DIRECTIONAL_ARROW = "multiDirectionalArrow"
    MULTI_DIRECTIONAL_CIRCLE = "multiDirectionalCircle"
    MULTI_DIRECTIONAL_CROSS = "multiDirectionalCross"
    OPEN = "open"
    THICK = "thick"


@dataclass
class RelationshipElement:
    """A relationship (edge) between flowchart nodes. Populated incrementally with the
    attributes that make up a relationship.
    """

    flowchart_schema_from: str
    """The id of the source node the relationship starts from."""

    to: str
    """The id of the target node the relationship points to."""

    animate: Optional[bool] = None
    """Whether the edge is animated (requires the edge `id`)."""

    animation: Optional[Animation] = None
    """The animation speed; setting it implies animate:true."""

    classes: Optional[List[str]] = None
    """Names of classDefs applied to this relationship (bound by the edge id). Each entry must
    match a classDefs[].name.
    """
    curve: Optional[Curve] = None
    id: Optional[str] = None
    """An optional edge ID (the `id@` prefix in Mermaid, e.g. `A e1@--> B`), usable later for
    styling, classes, and animation.
    """
    label: Optional[str] = None
    """Text attached to the link, rendered on the edge."""

    length: Optional[int] = None
    """The number of ranks the link spans. 1 is the default; a higher value lengthens the link
    (the extra dashes in Mermaid). The renderer may still draw it longer to satisfy other
    links.
    """
    link_type: Optional[LinkType] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "RelationshipElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        flowchart_schema_from = from_str(obj.get("from"))
        to = from_str(obj.get("to"))
        animate = from_union([from_bool, from_none], obj.get("animate"))
        animation = from_union([Animation, from_none], obj.get("animation"))
        classes = from_union([lambda x: from_list(from_str, x), from_none], obj.get("classes"))
        curve = from_union([Curve, from_none], obj.get("curve"))
        id = from_union([from_str, from_none], obj.get("id"))
        label = from_union([from_str, from_none], obj.get("label"))
        length = from_union([from_int, from_none], obj.get("length"))
        link_type = from_union([LinkType, from_none], obj.get("linkType"))
        return RelationshipElement(
            flowchart_schema_from,
            to,
            animate,
            animation,
            classes,
            curve,
            id,
            label,
            length,
            link_type,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["from"] = from_str(self.flowchart_schema_from)
        result["to"] = from_str(self.to)
        if self.animate is not None:
            result["animate"] = from_union([from_bool, from_none], self.animate)
        if self.animation is not None:
            result["animation"] = from_union(
                [lambda x: to_enum(Animation, x), from_none], self.animation
            )
        if self.classes is not None:
            result["classes"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.classes
            )
        if self.curve is not None:
            result["curve"] = from_union([lambda x: to_enum(Curve, x), from_none], self.curve)
        if self.id is not None:
            result["id"] = from_union([from_str, from_none], self.id)
        if self.label is not None:
            result["label"] = from_union([from_str, from_none], self.label)
        if self.length is not None:
            result["length"] = from_union([from_int, from_none], self.length)
        if self.link_type is not None:
            result["linkType"] = from_union(
                [lambda x: to_enum(LinkType, x), from_none], self.link_type
            )
        return result


class View(Enum):
    """Whether the subgraph is drawn in full (`expanded`, the default) or as a single compact
    node carrying its title (`collapsed`, Mermaid `@{ view: collapsed }`).
    """

    COLLAPSED = "collapsed"
    EXPANDED = "expanded"


@dataclass
class Subgraphs:
    """A flowchart graph: its nodes, the relationships between them, and nested subgraphs.
    Recursive — each subgraph is itself a graph.
    """

    id: Optional[str] = None
    """An explicit subgraph id (Mermaid `subgraph id [Title]`), referenced by edges to and from
    the subgraph and required to collapse it.
    """
    nodes: Optional[List[NodeElement]] = None
    """The nodes in this graph."""

    orientation: Optional[Orientation] = None
    relationships: Optional[List[RelationshipElement]] = None
    """The relationships (edges) between nodes in this graph."""

    subgraphs: Optional[List["Subgraphs"]] = None
    """Nested subgraphs, each a graph in its own right."""

    title: Optional[str] = None
    """The subgraph's displayed name."""

    view: Optional[View] = None
    """Whether the subgraph is drawn in full (`expanded`, the default) or as a single compact
    node carrying its title (`collapsed`, Mermaid `@{ view: collapsed }`).
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Subgraphs":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_str, from_none], obj.get("id"))
        nodes = from_union(
            [lambda x: from_list(NodeElement.from_dict, x), from_none], obj.get("nodes")
        )
        orientation = from_union([Orientation, from_none], obj.get("orientation"))
        relationships = from_union(
            [lambda x: from_list(RelationshipElement.from_dict, x), from_none],
            obj.get("relationships"),
        )
        subgraphs = from_union(
            [lambda x: from_list(Subgraphs.from_dict, x), from_none], obj.get("subgraphs")
        )
        title = from_union([from_str, from_none], obj.get("title"))
        view = from_union([View, from_none], obj.get("view"))
        return Subgraphs(id, nodes, orientation, relationships, subgraphs, title, view)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.id is not None:
            result["id"] = from_union([from_str, from_none], self.id)
        if self.nodes is not None:
            result["nodes"] = from_union(
                [lambda x: from_list(lambda x: to_class(NodeElement, x), x), from_none], self.nodes
            )
        if self.orientation is not None:
            result["orientation"] = from_union(
                [lambda x: to_enum(Orientation, x), from_none], self.orientation
            )
        if self.relationships is not None:
            result["relationships"] = from_union(
                [lambda x: from_list(lambda x: to_class(RelationshipElement, x), x), from_none],
                self.relationships,
            )
        if self.subgraphs is not None:
            result["subgraphs"] = from_union(
                [lambda x: from_list(lambda x: to_class(Subgraphs, x), x), from_none],
                self.subgraphs,
            )
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        if self.view is not None:
            result["view"] = from_union([lambda x: to_enum(View, x), from_none], self.view)
        return result


@dataclass
class FlowchartDiagram(DataModelHelper):
    """The flowchart diagram body: its orientation, its root graph, and the nodes and
    relationships that make it up. This is the first of several diagram bodies; swimlane,
    gantt, and the rest follow as sibling schemas in this folder.
    """

    class_defs: Optional[List[ClassDefElement]] = None
    """The flowchart's style classes. Declared at the top level because classDef is
    diagram-global, not subgraph-scoped: node and relationship ids share one global
    namespace, so a class binds by name from anywhere in the diagram.
    """
    link_styles: Optional[List[LinkStyleElement]] = None
    """Link styling by definition order (Mermaid `linkStyle`), distinct from class binding."""

    nodes: Optional[List[NodeElement]] = None
    """The nodes in the flowchart."""

    orientation: Optional[Orientation] = None
    relationships: Optional[List[RelationshipElement]] = None
    """The relationships (edges) between nodes in the flowchart."""

    subgraphs: Optional[Subgraphs] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "FlowchartDiagram":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        class_defs = from_union(
            [lambda x: from_list(ClassDefElement.from_dict, x), from_none], obj.get("classDefs")
        )
        link_styles = from_union(
            [lambda x: from_list(LinkStyleElement.from_dict, x), from_none], obj.get("linkStyles")
        )
        nodes = from_union(
            [lambda x: from_list(NodeElement.from_dict, x), from_none], obj.get("nodes")
        )
        orientation = from_union([Orientation, from_none], obj.get("orientation"))
        relationships = from_union(
            [lambda x: from_list(RelationshipElement.from_dict, x), from_none],
            obj.get("relationships"),
        )
        subgraphs = from_union([Subgraphs.from_dict, from_none], obj.get("subgraphs"))
        return FlowchartDiagram(
            class_defs, link_styles, nodes, orientation, relationships, subgraphs
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.class_defs is not None:
            result["classDefs"] = from_union(
                [lambda x: from_list(lambda x: to_class(ClassDefElement, x), x), from_none],
                self.class_defs,
            )
        if self.link_styles is not None:
            result["linkStyles"] = from_union(
                [lambda x: from_list(lambda x: to_class(LinkStyleElement, x), x), from_none],
                self.link_styles,
            )
        if self.nodes is not None:
            result["nodes"] = from_union(
                [lambda x: from_list(lambda x: to_class(NodeElement, x), x), from_none], self.nodes
            )
        if self.orientation is not None:
            result["orientation"] = from_union(
                [lambda x: to_enum(Orientation, x), from_none], self.orientation
            )
        if self.relationships is not None:
            result["relationships"] = from_union(
                [lambda x: from_list(lambda x: to_class(RelationshipElement, x), x), from_none],
                self.relationships,
            )
        if self.subgraphs is not None:
            result["subgraphs"] = from_union(
                [lambda x: to_class(Subgraphs, x), from_none], self.subgraphs
            )
        return result


def flowchart_diagram_from_dict(s: Any) -> FlowchartDiagram:
    return FlowchartDiagram.from_dict(s)


def flowchart_diagram_to_dict(x: FlowchartDiagram) -> Any:
    return to_class(FlowchartDiagram, x)
