# =============================================================================
# AUTO-GENERATED FILE — DO NOT EDIT
# Generated from JSON Schema via quicktype. Any manual edits will be
# overwritten the next time codegen runs (make codegen-all).
# To modify, update the source schema in schema/schemas/ and re-run codegen.
# =============================================================================

from enum import Enum
from dataclasses import dataclass
from foundationTypes.data_model_helper import (
    DataModelHelper,
    from_bool,
    from_dict,
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
from typing import Optional, Any, Union, List, Dict, TypeVar, Type, cast, Callable

T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


class Look(Enum):
    """Defines which main look to use for the diagram."""

    CLASSIC = "classic"
    HAND_DRAWN = "handDrawn"
    NEO = "neo"


class Theme(Enum):
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """

    BASE = "base"
    DARK = "dark"
    DEFAULT = "default"
    FOREST = "forest"
    NEO = "neo"
    NEO_DARK = "neo-dark"
    NEUTRAL = "neutral"
    NULL = "null"
    REDUX = "redux"
    REDUX_COLOR = "redux-color"
    REDUX_DARK = "redux-dark"
    REDUX_DARK_COLOR = "redux-dark-color"


@dataclass
class AgentflowDiagramConfig(DataModelHelper):
    """The object containing configurations specific for the agentflow diagram type.

    Agentflow renders through the shared unified renderer, so it owns the same
    spacing and padding knobs a flowchart does. They live in their own block so
    that agentflow can be tuned without moving every flowchart on the page.
    """

    diagram_padding: Optional[int] = None
    """The amount of padding around the diagram as a whole so that embedded
    diagrams have margins, expressed in pixels.
    """
    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    min_node_width: Optional[float] = None
    """Minimum width of the label area of a node.
    
    Labels narrower than this are widened to it, so nodes with short text
    get a uniform width; the node's own padding is added on top, the same
    way it is for `wrappingWidth`. Nodes with an explicit width are not
    affected.
    """
    node_spacing: Optional[int] = None
    """Defines the spacing between nodes on the same level.
    
    Pertains to horizontal spacing for TB (top to bottom) or BT (bottom to top) graphs,
    and the vertical spacing for LR as well as RL graphs.
    """
    rank_spacing: Optional[int] = None
    """Defines the spacing between nodes on different levels.
    
    Pertains to vertical spacing for TB (top to bottom) or BT (bottom to top), and the
    horizontal spacing for LR as well as RL graphs.
    """
    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    title_top_margin: Optional[int] = None
    """Margin top for the text over the diagram"""

    wrapping_width: Optional[float] = None
    """Width of nodes where text is wrapped.
    
    When using markdown strings the text is wrapped automatically, this
    value sets the max width of a text before it continues on a new line.
    """
    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    use_max_width: Optional[bool] = None
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "AgentflowDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        diagram_padding = from_union([from_int, from_none], obj.get("diagramPadding"))
        look = from_union([Look, from_none], obj.get("look"))
        min_node_width = from_union([from_float, from_none], obj.get("minNodeWidth"))
        node_spacing = from_union([from_int, from_none], obj.get("nodeSpacing"))
        rank_spacing = from_union([from_int, from_none], obj.get("rankSpacing"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        title_top_margin = from_union([from_int, from_none], obj.get("titleTopMargin"))
        wrapping_width = from_union([from_float, from_none], obj.get("wrappingWidth"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        use_max_width = from_union([from_bool, from_none], obj.get("useMaxWidth"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return AgentflowDiagramConfig(
            diagram_padding,
            look,
            min_node_width,
            node_spacing,
            rank_spacing,
            theme,
            title_top_margin,
            wrapping_width,
            layout,
            use_max_width,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.diagram_padding is not None:
            result["diagramPadding"] = from_union([from_int, from_none], self.diagram_padding)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.min_node_width is not None:
            result["minNodeWidth"] = from_union([to_float, from_none], self.min_node_width)
        if self.node_spacing is not None:
            result["nodeSpacing"] = from_union([from_int, from_none], self.node_spacing)
        if self.rank_spacing is not None:
            result["rankSpacing"] = from_union([from_int, from_none], self.rank_spacing)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.title_top_margin is not None:
            result["titleTopMargin"] = from_union([from_int, from_none], self.title_top_margin)
        if self.wrapping_width is not None:
            result["wrappingWidth"] = from_union([to_float, from_none], self.wrapping_width)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.use_max_width is not None:
            result["useMaxWidth"] = from_union([from_bool, from_none], self.use_max_width)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


@dataclass
class ArchitectureDiagramConfig(DataModelHelper):
    """The object containing configurations specific for architecture diagrams"""

    edge_elasticity: float
    """Spring elasticity (0–1) applied to edges between nodes within the same group, passed
    through to
    fcose. Higher values pull connected nodes closer together; lower values let the layout
    spread them
    out. Edges crossing group boundaries are unaffected.
    """
    font_size: float
    icon_size: float
    ideal_edge_length_multiplier: float
    """Multiplier applied to `iconSize` to compute the ideal length of edges between nodes
    within the
    same group. Increase to add breathing room; decrease to pack the diagram tighter. Edges
    crossing
    group boundaries are unaffected and use a fixed shorter length.
    """
    node_separation: float
    """Minimum separation (in pixels) between sibling nodes in the same group, passed through to
    the
    underlying fcose layout. Increase to spread overlapping siblings apart when many edges
    share the
    same port direction.
    """
    num_iter: float
    """Maximum number of iterations the fcose layout algorithm runs before stopping. Increase
    for higher
    quality on large or densely-connected diagrams at the cost of render time.
    """
    padding: float
    randomize: bool
    """Whether to randomize initial node positions before running the layout algorithm.
    When false (default), nodes start at deterministic seed positions. When true, nodes
    start at random positions, which may produce varied but potentially better-spaced
    layouts. Note: `randomize: false` alone does NOT guarantee identical renders, because
    the underlying fcose layout still uses `Math.random()` internally during its
    constraint solver — use the `seed` option for full determinism.
    """
    seed: float
    """Deterministic seed for the fcose layout. Defaults to 1, which makes every render of the
    same diagram produce the same layout — required for visual regression tests to be stable.
    Set to 0 to opt out and use the unstubbed Math.random (the layout will still differ
    slightly between renders, matching pre-fix behavior). Any other number selects a
    different reproducible layout variant.
    """
    use_max_width: bool
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ArchitectureDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        edge_elasticity = from_float(obj.get("edgeElasticity"))
        font_size = from_float(obj.get("fontSize"))
        icon_size = from_float(obj.get("iconSize"))
        ideal_edge_length_multiplier = from_float(obj.get("idealEdgeLengthMultiplier"))
        node_separation = from_float(obj.get("nodeSeparation"))
        num_iter = from_float(obj.get("numIter"))
        padding = from_float(obj.get("padding"))
        randomize = from_bool(obj.get("randomize"))
        seed = from_float(obj.get("seed"))
        use_max_width = from_bool(obj.get("useMaxWidth"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        look = from_union([Look, from_none], obj.get("look"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return ArchitectureDiagramConfig(
            edge_elasticity,
            font_size,
            icon_size,
            ideal_edge_length_multiplier,
            node_separation,
            num_iter,
            padding,
            randomize,
            seed,
            use_max_width,
            layout,
            look,
            theme,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["edgeElasticity"] = to_float(self.edge_elasticity)
        result["fontSize"] = to_float(self.font_size)
        result["iconSize"] = to_float(self.icon_size)
        result["idealEdgeLengthMultiplier"] = to_float(self.ideal_edge_length_multiplier)
        result["nodeSeparation"] = to_float(self.node_separation)
        result["numIter"] = to_float(self.num_iter)
        result["padding"] = to_float(self.padding)
        result["randomize"] = from_bool(self.randomize)
        result["seed"] = to_float(self.seed)
        result["useMaxWidth"] = from_bool(self.use_max_width)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


@dataclass
class BlockDiagramConfig(DataModelHelper):
    """The object containing configurations specific for block diagrams."""

    padding: Optional[float] = None
    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_max_width: Optional[bool] = None
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "BlockDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        padding = from_union([from_float, from_none], obj.get("padding"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        look = from_union([Look, from_none], obj.get("look"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_max_width = from_union([from_bool, from_none], obj.get("useMaxWidth"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return BlockDiagramConfig(padding, layout, look, theme, use_max_width, use_width)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.padding is not None:
            result["padding"] = from_union([to_float, from_none], self.padding)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_max_width is not None:
            result["useMaxWidth"] = from_union([from_bool, from_none], self.use_max_width)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


@dataclass
class C4DiagramConfig(DataModelHelper):
    """The object containing configurations specific for c4 diagrams"""

    box_margin: int
    """Margin around boxes"""

    c4_boundary_in_row: int
    """How many boundaries to place in each row."""

    c4_shape_in_row: int
    """How many shapes to place in each row."""

    c4_shape_margin: int
    """Margin between shapes"""

    c4_shape_padding: int
    """Padding between shapes"""

    diagram_margin_x: int
    """Margin to the right and left of the c4 diagram, must be a positive value."""

    diagram_margin_y: int
    """Margin to the over and under the c4 diagram, must be a positive value."""

    height: int
    """Height of person boxes"""

    width: int
    """Width of person boxes"""

    use_max_width: bool
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    boundary_font: Any
    boundary_font_family: Optional[str] = None
    """This sets the font family of Boundary shape for the diagram"""

    boundary_font_size: Optional[Union[float, str]] = None
    """This sets the font size of Boundary shape for the diagram"""

    boundary_font_weight: Optional[Union[float, str]] = None
    """This sets the font weight of Boundary shape for the diagram"""

    component_bg_color: Optional[str] = None
    component_border_color: Optional[str] = None
    component_db_bg_color: Optional[str] = None
    component_db_border_color: Optional[str] = None
    component_db_font: Any = None
    component_db_font_family: Optional[str] = None
    """This sets the font family of Component DB shape for the diagram"""

    component_db_font_size: Optional[Union[float, str]] = None
    """This sets the font size of Component DB shape for the diagram"""

    component_db_font_weight: Optional[Union[float, str]] = None
    """This sets the font weight of Component DB shape for the diagram"""

    component_queue_bg_color: Optional[str] = None
    component_queue_border_color: Optional[str] = None
    component_queue_font: Any = None
    component_queue_font_family: Optional[str] = None
    """This sets the font family of Component Queue shape for the diagram"""

    component_queue_font_size: Optional[Union[float, str]] = None
    """This sets the font size of Component Queue shape for the diagram"""

    component_queue_font_weight: Optional[Union[float, str]] = None
    """This sets the font weight of Component Queue shape for the diagram"""

    component_font: Any = None
    component_font_family: Optional[str] = None
    """This sets the font family of Component shape for the diagram"""

    component_font_size: Optional[Union[float, str]] = None
    """This sets the font size of Component shape for the diagram"""

    component_font_weight: Optional[Union[float, str]] = None
    """This sets the font weight of Component shape for the diagram"""

    container_bg_color: Optional[str] = None
    container_border_color: Optional[str] = None
    container_db_bg_color: Optional[str] = None
    container_db_border_color: Optional[str] = None
    container_db_font: Any = None
    container_db_font_family: Optional[str] = None
    """This sets the font family of Container DB shape for the diagram"""

    container_db_font_size: Optional[Union[float, str]] = None
    """This sets the font size of Container DB shape for the diagram"""

    container_db_font_weight: Optional[Union[float, str]] = None
    """This sets the font weight of Container DB shape for the diagram"""

    container_queue_bg_color: Optional[str] = None
    container_queue_border_color: Optional[str] = None
    container_queue_font: Any = None
    container_queue_font_family: Optional[str] = None
    """This sets the font family of Container Queue shape for the diagram"""

    container_queue_font_size: Optional[Union[float, str]] = None
    """This sets the font size of Container Queue shape for the diagram"""

    container_queue_font_weight: Optional[Union[float, str]] = None
    """This sets the font weight of Container Queue shape for the diagram"""

    container_font: Any = None
    container_font_family: Optional[str] = None
    """This sets the font family of Container shape for the diagram"""

    container_font_size: Optional[Union[float, str]] = None
    """This sets the font size of Container shape for the diagram"""

    container_font_weight: Optional[Union[float, str]] = None
    """This sets the font weight of Container shape for the diagram"""

    external_component_bg_color: Optional[str] = None
    external_component_border_color: Optional[str] = None
    external_component_db_bg_color: Optional[str] = None
    external_component_db_border_color: Optional[str] = None
    external_component_db_font: Any = None
    external_component_db_font_family: Optional[str] = None
    """This sets the font family of External Component DB shape for the diagram"""

    external_component_db_font_size: Optional[Union[float, str]] = None
    """This sets the font size of External Component DB shape for the diagram"""

    external_component_db_font_weight: Optional[Union[float, str]] = None
    """This sets the font weight of External Component DB shape for the diagram"""

    external_component_queue_bg_color: Optional[str] = None
    external_component_queue_border_color: Optional[str] = None
    external_component_queue_font: Any = None
    external_component_queue_font_family: Optional[str] = None
    """This sets the font family of External Component Queue shape for the diagram"""

    external_component_queue_font_size: Optional[Union[float, str]] = None
    """This sets the font size of External Component Queue shape for the diagram"""

    external_component_queue_font_weight: Optional[Union[float, str]] = None
    """This sets the font weight of External Component Queue shape for the diagram"""

    external_component_font: Any = None
    external_component_font_family: Optional[str] = None
    """This sets the font family of External Component shape for the diagram"""

    external_component_font_size: Optional[Union[float, str]] = None
    """This sets the font size of External Component shape for the diagram"""

    external_component_font_weight: Optional[Union[float, str]] = None
    """This sets the font weight of External Component shape for the diagram"""

    external_container_bg_color: Optional[str] = None
    external_container_border_color: Optional[str] = None
    external_container_db_bg_color: Optional[str] = None
    external_container_db_border_color: Optional[str] = None
    external_container_db_font: Any = None
    external_container_db_font_family: Optional[str] = None
    """This sets the font family of External Container DB shape for the diagram"""

    external_container_db_font_size: Optional[Union[float, str]] = None
    """This sets the font size of External Container DB shape for the diagram"""

    external_container_db_font_weight: Optional[Union[float, str]] = None
    """This sets the font weight of External Container DB shape for the diagram"""

    external_container_queue_bg_color: Optional[str] = None
    external_container_queue_border_color: Optional[str] = None
    external_container_queue_font: Any = None
    external_container_queue_font_family: Optional[str] = None
    """This sets the font family of External Container Queue shape for the diagram"""

    external_container_queue_font_size: Optional[Union[float, str]] = None
    """This sets the font size of External Container Queue shape for the diagram"""

    external_container_queue_font_weight: Optional[Union[float, str]] = None
    """This sets the font weight of External Container Queue shape for the diagram"""

    external_container_font: Any = None
    external_container_font_family: Optional[str] = None
    """This sets the font family of External Container shape for the diagram"""

    external_container_font_size: Optional[Union[float, str]] = None
    """This sets the font size of External Container shape for the diagram"""

    external_container_font_weight: Optional[Union[float, str]] = None
    """This sets the font weight of External Container shape for the diagram"""

    external_person_bg_color: Optional[str] = None
    external_person_border_color: Optional[str] = None
    external_person_font: Any = None
    external_person_font_family: Optional[str] = None
    """This sets the font family of External Person shape for the diagram"""

    external_person_font_size: Optional[Union[float, str]] = None
    """This sets the font size of External Person shape for the diagram"""

    external_person_font_weight: Optional[Union[float, str]] = None
    """This sets the font weight of External Person shape for the diagram"""

    external_system_bg_color: Optional[str] = None
    external_system_border_color: Optional[str] = None
    external_system_db_bg_color: Optional[str] = None
    external_system_db_border_color: Optional[str] = None
    external_system_db_font: Any = None
    external_system_db_font_family: Optional[str] = None
    """This sets the font family of External System DB shape for the diagram"""

    external_system_db_font_size: Optional[Union[float, str]] = None
    """This sets the font size of External System DB shape for the diagram"""

    external_system_db_font_weight: Optional[Union[float, str]] = None
    """This sets the font weight of External System DB shape for the diagram"""

    external_system_queue_bg_color: Optional[str] = None
    external_system_queue_border_color: Optional[str] = None
    external_system_queue_font: Any = None
    external_system_queue_font_family: Optional[str] = None
    """This sets the font family of External System Queue shape for the diagram"""

    external_system_queue_font_size: Optional[Union[float, str]] = None
    """This sets the font size of External System Queue shape for the diagram"""

    external_system_queue_font_weight: Optional[Union[float, str]] = None
    """This sets the font weight of External System Queue shape for the diagram"""

    external_system_font: Any = None
    external_system_font_family: Optional[str] = None
    """This sets the font family of External System shape for the diagram"""

    external_system_font_size: Optional[Union[float, str]] = None
    """This sets the font size of External System shape for the diagram"""

    external_system_font_weight: Optional[Union[float, str]] = None
    """This sets the font weight of External System shape for the diagram"""

    message_font: Any = None
    message_font_family: Optional[str] = None
    """This sets the font family of Message shape for the diagram"""

    message_font_size: Optional[Union[float, str]] = None
    """This sets the font size of Message shape for the diagram"""

    message_font_weight: Optional[Union[float, str]] = None
    """This sets the font weight of Message shape for the diagram"""

    next_line_padding_x: Optional[float] = None
    person_bg_color: Optional[str] = None
    person_border_color: Optional[str] = None
    person_font: Any = None
    person_font_family: Optional[str] = None
    """This sets the font weight of Person shape for the diagram"""

    person_font_size: Optional[Union[float, str]] = None
    """This sets the font size of Person shape for the diagram"""

    person_font_weight: Optional[Union[float, str]] = None
    """This sets the font weight of Person shape for the diagram"""

    system_bg_color: Optional[str] = None
    system_border_color: Optional[str] = None
    system_db_bg_color: Optional[str] = None
    system_db_border_color: Optional[str] = None
    system_db_font: Any = None
    system_db_font_family: Optional[str] = None
    """This sets the font family of System DB shape for the diagram"""

    system_db_font_size: Optional[Union[float, str]] = None
    """This sets the font size of System DB shape for the diagram"""

    system_db_font_weight: Optional[Union[float, str]] = None
    """This sets the font weight of System DB shape for the diagram"""

    system_queue_bg_color: Optional[str] = None
    system_queue_border_color: Optional[str] = None
    system_queue_font: Any = None
    system_queue_font_family: Optional[str] = None
    """This sets the font family of System Queue shape for the diagram"""

    system_queue_font_size: Optional[Union[float, str]] = None
    """This sets the font size of System Queue shape for the diagram"""

    system_queue_font_weight: Optional[Union[float, str]] = None
    """This sets the font weight of System Queue shape for the diagram"""

    system_font: Any = None
    system_font_family: Optional[str] = None
    """This sets the font family of System shape for the diagram"""

    system_font_size: Optional[Union[float, str]] = None
    """This sets the font size of System shape for the diagram"""

    system_font_weight: Optional[Union[float, str]] = None
    """This sets the font weight of System shape for the diagram"""

    wrap: Optional[bool] = None
    """This sets the auto-wrap state for the diagram"""

    wrap_padding: Optional[float] = None
    """This sets the auto-wrap padding for the diagram (sides only)"""

    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "C4DiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        box_margin = from_int(obj.get("boxMargin"))
        c4_boundary_in_row = from_int(obj.get("c4BoundaryInRow"))
        c4_shape_in_row = from_int(obj.get("c4ShapeInRow"))
        c4_shape_margin = from_int(obj.get("c4ShapeMargin"))
        c4_shape_padding = from_int(obj.get("c4ShapePadding"))
        diagram_margin_x = from_int(obj.get("diagramMarginX"))
        diagram_margin_y = from_int(obj.get("diagramMarginY"))
        height = from_int(obj.get("height"))
        width = from_int(obj.get("width"))
        use_max_width = from_bool(obj.get("useMaxWidth"))
        boundary_font = obj.get("boundaryFont")
        boundary_font_family = from_union([from_str, from_none], obj.get("boundaryFontFamily"))
        boundary_font_size = from_union(
            [from_float, from_str, from_none], obj.get("boundaryFontSize")
        )
        boundary_font_weight = from_union(
            [from_float, from_str, from_none], obj.get("boundaryFontWeight")
        )
        component_bg_color = from_union([from_str, from_none], obj.get("component_bg_color"))
        component_border_color = from_union(
            [from_str, from_none], obj.get("component_border_color")
        )
        component_db_bg_color = from_union([from_str, from_none], obj.get("component_db_bg_color"))
        component_db_border_color = from_union(
            [from_str, from_none], obj.get("component_db_border_color")
        )
        component_db_font = obj.get("component_dbFont")
        component_db_font_family = from_union(
            [from_str, from_none], obj.get("component_dbFontFamily")
        )
        component_db_font_size = from_union(
            [from_float, from_str, from_none], obj.get("component_dbFontSize")
        )
        component_db_font_weight = from_union(
            [from_float, from_str, from_none], obj.get("component_dbFontWeight")
        )
        component_queue_bg_color = from_union(
            [from_str, from_none], obj.get("component_queue_bg_color")
        )
        component_queue_border_color = from_union(
            [from_str, from_none], obj.get("component_queue_border_color")
        )
        component_queue_font = obj.get("component_queueFont")
        component_queue_font_family = from_union(
            [from_str, from_none], obj.get("component_queueFontFamily")
        )
        component_queue_font_size = from_union(
            [from_float, from_str, from_none], obj.get("component_queueFontSize")
        )
        component_queue_font_weight = from_union(
            [from_float, from_str, from_none], obj.get("component_queueFontWeight")
        )
        component_font = obj.get("componentFont")
        component_font_family = from_union([from_str, from_none], obj.get("componentFontFamily"))
        component_font_size = from_union(
            [from_float, from_str, from_none], obj.get("componentFontSize")
        )
        component_font_weight = from_union(
            [from_float, from_str, from_none], obj.get("componentFontWeight")
        )
        container_bg_color = from_union([from_str, from_none], obj.get("container_bg_color"))
        container_border_color = from_union(
            [from_str, from_none], obj.get("container_border_color")
        )
        container_db_bg_color = from_union([from_str, from_none], obj.get("container_db_bg_color"))
        container_db_border_color = from_union(
            [from_str, from_none], obj.get("container_db_border_color")
        )
        container_db_font = obj.get("container_dbFont")
        container_db_font_family = from_union(
            [from_str, from_none], obj.get("container_dbFontFamily")
        )
        container_db_font_size = from_union(
            [from_float, from_str, from_none], obj.get("container_dbFontSize")
        )
        container_db_font_weight = from_union(
            [from_float, from_str, from_none], obj.get("container_dbFontWeight")
        )
        container_queue_bg_color = from_union(
            [from_str, from_none], obj.get("container_queue_bg_color")
        )
        container_queue_border_color = from_union(
            [from_str, from_none], obj.get("container_queue_border_color")
        )
        container_queue_font = obj.get("container_queueFont")
        container_queue_font_family = from_union(
            [from_str, from_none], obj.get("container_queueFontFamily")
        )
        container_queue_font_size = from_union(
            [from_float, from_str, from_none], obj.get("container_queueFontSize")
        )
        container_queue_font_weight = from_union(
            [from_float, from_str, from_none], obj.get("container_queueFontWeight")
        )
        container_font = obj.get("containerFont")
        container_font_family = from_union([from_str, from_none], obj.get("containerFontFamily"))
        container_font_size = from_union(
            [from_float, from_str, from_none], obj.get("containerFontSize")
        )
        container_font_weight = from_union(
            [from_float, from_str, from_none], obj.get("containerFontWeight")
        )
        external_component_bg_color = from_union(
            [from_str, from_none], obj.get("external_component_bg_color")
        )
        external_component_border_color = from_union(
            [from_str, from_none], obj.get("external_component_border_color")
        )
        external_component_db_bg_color = from_union(
            [from_str, from_none], obj.get("external_component_db_bg_color")
        )
        external_component_db_border_color = from_union(
            [from_str, from_none], obj.get("external_component_db_border_color")
        )
        external_component_db_font = obj.get("external_component_dbFont")
        external_component_db_font_family = from_union(
            [from_str, from_none], obj.get("external_component_dbFontFamily")
        )
        external_component_db_font_size = from_union(
            [from_float, from_str, from_none], obj.get("external_component_dbFontSize")
        )
        external_component_db_font_weight = from_union(
            [from_float, from_str, from_none], obj.get("external_component_dbFontWeight")
        )
        external_component_queue_bg_color = from_union(
            [from_str, from_none], obj.get("external_component_queue_bg_color")
        )
        external_component_queue_border_color = from_union(
            [from_str, from_none], obj.get("external_component_queue_border_color")
        )
        external_component_queue_font = obj.get("external_component_queueFont")
        external_component_queue_font_family = from_union(
            [from_str, from_none], obj.get("external_component_queueFontFamily")
        )
        external_component_queue_font_size = from_union(
            [from_float, from_str, from_none], obj.get("external_component_queueFontSize")
        )
        external_component_queue_font_weight = from_union(
            [from_float, from_str, from_none], obj.get("external_component_queueFontWeight")
        )
        external_component_font = obj.get("external_componentFont")
        external_component_font_family = from_union(
            [from_str, from_none], obj.get("external_componentFontFamily")
        )
        external_component_font_size = from_union(
            [from_float, from_str, from_none], obj.get("external_componentFontSize")
        )
        external_component_font_weight = from_union(
            [from_float, from_str, from_none], obj.get("external_componentFontWeight")
        )
        external_container_bg_color = from_union(
            [from_str, from_none], obj.get("external_container_bg_color")
        )
        external_container_border_color = from_union(
            [from_str, from_none], obj.get("external_container_border_color")
        )
        external_container_db_bg_color = from_union(
            [from_str, from_none], obj.get("external_container_db_bg_color")
        )
        external_container_db_border_color = from_union(
            [from_str, from_none], obj.get("external_container_db_border_color")
        )
        external_container_db_font = obj.get("external_container_dbFont")
        external_container_db_font_family = from_union(
            [from_str, from_none], obj.get("external_container_dbFontFamily")
        )
        external_container_db_font_size = from_union(
            [from_float, from_str, from_none], obj.get("external_container_dbFontSize")
        )
        external_container_db_font_weight = from_union(
            [from_float, from_str, from_none], obj.get("external_container_dbFontWeight")
        )
        external_container_queue_bg_color = from_union(
            [from_str, from_none], obj.get("external_container_queue_bg_color")
        )
        external_container_queue_border_color = from_union(
            [from_str, from_none], obj.get("external_container_queue_border_color")
        )
        external_container_queue_font = obj.get("external_container_queueFont")
        external_container_queue_font_family = from_union(
            [from_str, from_none], obj.get("external_container_queueFontFamily")
        )
        external_container_queue_font_size = from_union(
            [from_float, from_str, from_none], obj.get("external_container_queueFontSize")
        )
        external_container_queue_font_weight = from_union(
            [from_float, from_str, from_none], obj.get("external_container_queueFontWeight")
        )
        external_container_font = obj.get("external_containerFont")
        external_container_font_family = from_union(
            [from_str, from_none], obj.get("external_containerFontFamily")
        )
        external_container_font_size = from_union(
            [from_float, from_str, from_none], obj.get("external_containerFontSize")
        )
        external_container_font_weight = from_union(
            [from_float, from_str, from_none], obj.get("external_containerFontWeight")
        )
        external_person_bg_color = from_union(
            [from_str, from_none], obj.get("external_person_bg_color")
        )
        external_person_border_color = from_union(
            [from_str, from_none], obj.get("external_person_border_color")
        )
        external_person_font = obj.get("external_personFont")
        external_person_font_family = from_union(
            [from_str, from_none], obj.get("external_personFontFamily")
        )
        external_person_font_size = from_union(
            [from_float, from_str, from_none], obj.get("external_personFontSize")
        )
        external_person_font_weight = from_union(
            [from_float, from_str, from_none], obj.get("external_personFontWeight")
        )
        external_system_bg_color = from_union(
            [from_str, from_none], obj.get("external_system_bg_color")
        )
        external_system_border_color = from_union(
            [from_str, from_none], obj.get("external_system_border_color")
        )
        external_system_db_bg_color = from_union(
            [from_str, from_none], obj.get("external_system_db_bg_color")
        )
        external_system_db_border_color = from_union(
            [from_str, from_none], obj.get("external_system_db_border_color")
        )
        external_system_db_font = obj.get("external_system_dbFont")
        external_system_db_font_family = from_union(
            [from_str, from_none], obj.get("external_system_dbFontFamily")
        )
        external_system_db_font_size = from_union(
            [from_float, from_str, from_none], obj.get("external_system_dbFontSize")
        )
        external_system_db_font_weight = from_union(
            [from_float, from_str, from_none], obj.get("external_system_dbFontWeight")
        )
        external_system_queue_bg_color = from_union(
            [from_str, from_none], obj.get("external_system_queue_bg_color")
        )
        external_system_queue_border_color = from_union(
            [from_str, from_none], obj.get("external_system_queue_border_color")
        )
        external_system_queue_font = obj.get("external_system_queueFont")
        external_system_queue_font_family = from_union(
            [from_str, from_none], obj.get("external_system_queueFontFamily")
        )
        external_system_queue_font_size = from_union(
            [from_float, from_str, from_none], obj.get("external_system_queueFontSize")
        )
        external_system_queue_font_weight = from_union(
            [from_float, from_str, from_none], obj.get("external_system_queueFontWeight")
        )
        external_system_font = obj.get("external_systemFont")
        external_system_font_family = from_union(
            [from_str, from_none], obj.get("external_systemFontFamily")
        )
        external_system_font_size = from_union(
            [from_float, from_str, from_none], obj.get("external_systemFontSize")
        )
        external_system_font_weight = from_union(
            [from_float, from_str, from_none], obj.get("external_systemFontWeight")
        )
        message_font = obj.get("messageFont")
        message_font_family = from_union([from_str, from_none], obj.get("messageFontFamily"))
        message_font_size = from_union(
            [from_float, from_str, from_none], obj.get("messageFontSize")
        )
        message_font_weight = from_union(
            [from_float, from_str, from_none], obj.get("messageFontWeight")
        )
        next_line_padding_x = from_union([from_float, from_none], obj.get("nextLinePaddingX"))
        person_bg_color = from_union([from_str, from_none], obj.get("person_bg_color"))
        person_border_color = from_union([from_str, from_none], obj.get("person_border_color"))
        person_font = obj.get("personFont")
        person_font_family = from_union([from_str, from_none], obj.get("personFontFamily"))
        person_font_size = from_union([from_float, from_str, from_none], obj.get("personFontSize"))
        person_font_weight = from_union(
            [from_float, from_str, from_none], obj.get("personFontWeight")
        )
        system_bg_color = from_union([from_str, from_none], obj.get("system_bg_color"))
        system_border_color = from_union([from_str, from_none], obj.get("system_border_color"))
        system_db_bg_color = from_union([from_str, from_none], obj.get("system_db_bg_color"))
        system_db_border_color = from_union(
            [from_str, from_none], obj.get("system_db_border_color")
        )
        system_db_font = obj.get("system_dbFont")
        system_db_font_family = from_union([from_str, from_none], obj.get("system_dbFontFamily"))
        system_db_font_size = from_union(
            [from_float, from_str, from_none], obj.get("system_dbFontSize")
        )
        system_db_font_weight = from_union(
            [from_float, from_str, from_none], obj.get("system_dbFontWeight")
        )
        system_queue_bg_color = from_union([from_str, from_none], obj.get("system_queue_bg_color"))
        system_queue_border_color = from_union(
            [from_str, from_none], obj.get("system_queue_border_color")
        )
        system_queue_font = obj.get("system_queueFont")
        system_queue_font_family = from_union(
            [from_str, from_none], obj.get("system_queueFontFamily")
        )
        system_queue_font_size = from_union(
            [from_float, from_str, from_none], obj.get("system_queueFontSize")
        )
        system_queue_font_weight = from_union(
            [from_float, from_str, from_none], obj.get("system_queueFontWeight")
        )
        system_font = obj.get("systemFont")
        system_font_family = from_union([from_str, from_none], obj.get("systemFontFamily"))
        system_font_size = from_union([from_float, from_str, from_none], obj.get("systemFontSize"))
        system_font_weight = from_union(
            [from_float, from_str, from_none], obj.get("systemFontWeight")
        )
        wrap = from_union([from_bool, from_none], obj.get("wrap"))
        wrap_padding = from_union([from_float, from_none], obj.get("wrapPadding"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        look = from_union([Look, from_none], obj.get("look"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return C4DiagramConfig(
            box_margin,
            c4_boundary_in_row,
            c4_shape_in_row,
            c4_shape_margin,
            c4_shape_padding,
            diagram_margin_x,
            diagram_margin_y,
            height,
            width,
            use_max_width,
            boundary_font,
            boundary_font_family,
            boundary_font_size,
            boundary_font_weight,
            component_bg_color,
            component_border_color,
            component_db_bg_color,
            component_db_border_color,
            component_db_font,
            component_db_font_family,
            component_db_font_size,
            component_db_font_weight,
            component_queue_bg_color,
            component_queue_border_color,
            component_queue_font,
            component_queue_font_family,
            component_queue_font_size,
            component_queue_font_weight,
            component_font,
            component_font_family,
            component_font_size,
            component_font_weight,
            container_bg_color,
            container_border_color,
            container_db_bg_color,
            container_db_border_color,
            container_db_font,
            container_db_font_family,
            container_db_font_size,
            container_db_font_weight,
            container_queue_bg_color,
            container_queue_border_color,
            container_queue_font,
            container_queue_font_family,
            container_queue_font_size,
            container_queue_font_weight,
            container_font,
            container_font_family,
            container_font_size,
            container_font_weight,
            external_component_bg_color,
            external_component_border_color,
            external_component_db_bg_color,
            external_component_db_border_color,
            external_component_db_font,
            external_component_db_font_family,
            external_component_db_font_size,
            external_component_db_font_weight,
            external_component_queue_bg_color,
            external_component_queue_border_color,
            external_component_queue_font,
            external_component_queue_font_family,
            external_component_queue_font_size,
            external_component_queue_font_weight,
            external_component_font,
            external_component_font_family,
            external_component_font_size,
            external_component_font_weight,
            external_container_bg_color,
            external_container_border_color,
            external_container_db_bg_color,
            external_container_db_border_color,
            external_container_db_font,
            external_container_db_font_family,
            external_container_db_font_size,
            external_container_db_font_weight,
            external_container_queue_bg_color,
            external_container_queue_border_color,
            external_container_queue_font,
            external_container_queue_font_family,
            external_container_queue_font_size,
            external_container_queue_font_weight,
            external_container_font,
            external_container_font_family,
            external_container_font_size,
            external_container_font_weight,
            external_person_bg_color,
            external_person_border_color,
            external_person_font,
            external_person_font_family,
            external_person_font_size,
            external_person_font_weight,
            external_system_bg_color,
            external_system_border_color,
            external_system_db_bg_color,
            external_system_db_border_color,
            external_system_db_font,
            external_system_db_font_family,
            external_system_db_font_size,
            external_system_db_font_weight,
            external_system_queue_bg_color,
            external_system_queue_border_color,
            external_system_queue_font,
            external_system_queue_font_family,
            external_system_queue_font_size,
            external_system_queue_font_weight,
            external_system_font,
            external_system_font_family,
            external_system_font_size,
            external_system_font_weight,
            message_font,
            message_font_family,
            message_font_size,
            message_font_weight,
            next_line_padding_x,
            person_bg_color,
            person_border_color,
            person_font,
            person_font_family,
            person_font_size,
            person_font_weight,
            system_bg_color,
            system_border_color,
            system_db_bg_color,
            system_db_border_color,
            system_db_font,
            system_db_font_family,
            system_db_font_size,
            system_db_font_weight,
            system_queue_bg_color,
            system_queue_border_color,
            system_queue_font,
            system_queue_font_family,
            system_queue_font_size,
            system_queue_font_weight,
            system_font,
            system_font_family,
            system_font_size,
            system_font_weight,
            wrap,
            wrap_padding,
            layout,
            look,
            theme,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["boxMargin"] = from_int(self.box_margin)
        result["c4BoundaryInRow"] = from_int(self.c4_boundary_in_row)
        result["c4ShapeInRow"] = from_int(self.c4_shape_in_row)
        result["c4ShapeMargin"] = from_int(self.c4_shape_margin)
        result["c4ShapePadding"] = from_int(self.c4_shape_padding)
        result["diagramMarginX"] = from_int(self.diagram_margin_x)
        result["diagramMarginY"] = from_int(self.diagram_margin_y)
        result["height"] = from_int(self.height)
        result["width"] = from_int(self.width)
        result["useMaxWidth"] = from_bool(self.use_max_width)
        if self.boundary_font is not None:
            result["boundaryFont"] = self.boundary_font
        if self.boundary_font_family is not None:
            result["boundaryFontFamily"] = from_union(
                [from_str, from_none], self.boundary_font_family
            )
        if self.boundary_font_size is not None:
            result["boundaryFontSize"] = from_union(
                [to_float, from_str, from_none], self.boundary_font_size
            )
        if self.boundary_font_weight is not None:
            result["boundaryFontWeight"] = from_union(
                [to_float, from_str, from_none], self.boundary_font_weight
            )
        if self.component_bg_color is not None:
            result["component_bg_color"] = from_union(
                [from_str, from_none], self.component_bg_color
            )
        if self.component_border_color is not None:
            result["component_border_color"] = from_union(
                [from_str, from_none], self.component_border_color
            )
        if self.component_db_bg_color is not None:
            result["component_db_bg_color"] = from_union(
                [from_str, from_none], self.component_db_bg_color
            )
        if self.component_db_border_color is not None:
            result["component_db_border_color"] = from_union(
                [from_str, from_none], self.component_db_border_color
            )
        if self.component_db_font is not None:
            result["component_dbFont"] = self.component_db_font
        if self.component_db_font_family is not None:
            result["component_dbFontFamily"] = from_union(
                [from_str, from_none], self.component_db_font_family
            )
        if self.component_db_font_size is not None:
            result["component_dbFontSize"] = from_union(
                [to_float, from_str, from_none], self.component_db_font_size
            )
        if self.component_db_font_weight is not None:
            result["component_dbFontWeight"] = from_union(
                [to_float, from_str, from_none], self.component_db_font_weight
            )
        if self.component_queue_bg_color is not None:
            result["component_queue_bg_color"] = from_union(
                [from_str, from_none], self.component_queue_bg_color
            )
        if self.component_queue_border_color is not None:
            result["component_queue_border_color"] = from_union(
                [from_str, from_none], self.component_queue_border_color
            )
        if self.component_queue_font is not None:
            result["component_queueFont"] = self.component_queue_font
        if self.component_queue_font_family is not None:
            result["component_queueFontFamily"] = from_union(
                [from_str, from_none], self.component_queue_font_family
            )
        if self.component_queue_font_size is not None:
            result["component_queueFontSize"] = from_union(
                [to_float, from_str, from_none], self.component_queue_font_size
            )
        if self.component_queue_font_weight is not None:
            result["component_queueFontWeight"] = from_union(
                [to_float, from_str, from_none], self.component_queue_font_weight
            )
        if self.component_font is not None:
            result["componentFont"] = self.component_font
        if self.component_font_family is not None:
            result["componentFontFamily"] = from_union(
                [from_str, from_none], self.component_font_family
            )
        if self.component_font_size is not None:
            result["componentFontSize"] = from_union(
                [to_float, from_str, from_none], self.component_font_size
            )
        if self.component_font_weight is not None:
            result["componentFontWeight"] = from_union(
                [to_float, from_str, from_none], self.component_font_weight
            )
        if self.container_bg_color is not None:
            result["container_bg_color"] = from_union(
                [from_str, from_none], self.container_bg_color
            )
        if self.container_border_color is not None:
            result["container_border_color"] = from_union(
                [from_str, from_none], self.container_border_color
            )
        if self.container_db_bg_color is not None:
            result["container_db_bg_color"] = from_union(
                [from_str, from_none], self.container_db_bg_color
            )
        if self.container_db_border_color is not None:
            result["container_db_border_color"] = from_union(
                [from_str, from_none], self.container_db_border_color
            )
        if self.container_db_font is not None:
            result["container_dbFont"] = self.container_db_font
        if self.container_db_font_family is not None:
            result["container_dbFontFamily"] = from_union(
                [from_str, from_none], self.container_db_font_family
            )
        if self.container_db_font_size is not None:
            result["container_dbFontSize"] = from_union(
                [to_float, from_str, from_none], self.container_db_font_size
            )
        if self.container_db_font_weight is not None:
            result["container_dbFontWeight"] = from_union(
                [to_float, from_str, from_none], self.container_db_font_weight
            )
        if self.container_queue_bg_color is not None:
            result["container_queue_bg_color"] = from_union(
                [from_str, from_none], self.container_queue_bg_color
            )
        if self.container_queue_border_color is not None:
            result["container_queue_border_color"] = from_union(
                [from_str, from_none], self.container_queue_border_color
            )
        if self.container_queue_font is not None:
            result["container_queueFont"] = self.container_queue_font
        if self.container_queue_font_family is not None:
            result["container_queueFontFamily"] = from_union(
                [from_str, from_none], self.container_queue_font_family
            )
        if self.container_queue_font_size is not None:
            result["container_queueFontSize"] = from_union(
                [to_float, from_str, from_none], self.container_queue_font_size
            )
        if self.container_queue_font_weight is not None:
            result["container_queueFontWeight"] = from_union(
                [to_float, from_str, from_none], self.container_queue_font_weight
            )
        if self.container_font is not None:
            result["containerFont"] = self.container_font
        if self.container_font_family is not None:
            result["containerFontFamily"] = from_union(
                [from_str, from_none], self.container_font_family
            )
        if self.container_font_size is not None:
            result["containerFontSize"] = from_union(
                [to_float, from_str, from_none], self.container_font_size
            )
        if self.container_font_weight is not None:
            result["containerFontWeight"] = from_union(
                [to_float, from_str, from_none], self.container_font_weight
            )
        if self.external_component_bg_color is not None:
            result["external_component_bg_color"] = from_union(
                [from_str, from_none], self.external_component_bg_color
            )
        if self.external_component_border_color is not None:
            result["external_component_border_color"] = from_union(
                [from_str, from_none], self.external_component_border_color
            )
        if self.external_component_db_bg_color is not None:
            result["external_component_db_bg_color"] = from_union(
                [from_str, from_none], self.external_component_db_bg_color
            )
        if self.external_component_db_border_color is not None:
            result["external_component_db_border_color"] = from_union(
                [from_str, from_none], self.external_component_db_border_color
            )
        if self.external_component_db_font is not None:
            result["external_component_dbFont"] = self.external_component_db_font
        if self.external_component_db_font_family is not None:
            result["external_component_dbFontFamily"] = from_union(
                [from_str, from_none], self.external_component_db_font_family
            )
        if self.external_component_db_font_size is not None:
            result["external_component_dbFontSize"] = from_union(
                [to_float, from_str, from_none], self.external_component_db_font_size
            )
        if self.external_component_db_font_weight is not None:
            result["external_component_dbFontWeight"] = from_union(
                [to_float, from_str, from_none], self.external_component_db_font_weight
            )
        if self.external_component_queue_bg_color is not None:
            result["external_component_queue_bg_color"] = from_union(
                [from_str, from_none], self.external_component_queue_bg_color
            )
        if self.external_component_queue_border_color is not None:
            result["external_component_queue_border_color"] = from_union(
                [from_str, from_none], self.external_component_queue_border_color
            )
        if self.external_component_queue_font is not None:
            result["external_component_queueFont"] = self.external_component_queue_font
        if self.external_component_queue_font_family is not None:
            result["external_component_queueFontFamily"] = from_union(
                [from_str, from_none], self.external_component_queue_font_family
            )
        if self.external_component_queue_font_size is not None:
            result["external_component_queueFontSize"] = from_union(
                [to_float, from_str, from_none], self.external_component_queue_font_size
            )
        if self.external_component_queue_font_weight is not None:
            result["external_component_queueFontWeight"] = from_union(
                [to_float, from_str, from_none], self.external_component_queue_font_weight
            )
        if self.external_component_font is not None:
            result["external_componentFont"] = self.external_component_font
        if self.external_component_font_family is not None:
            result["external_componentFontFamily"] = from_union(
                [from_str, from_none], self.external_component_font_family
            )
        if self.external_component_font_size is not None:
            result["external_componentFontSize"] = from_union(
                [to_float, from_str, from_none], self.external_component_font_size
            )
        if self.external_component_font_weight is not None:
            result["external_componentFontWeight"] = from_union(
                [to_float, from_str, from_none], self.external_component_font_weight
            )
        if self.external_container_bg_color is not None:
            result["external_container_bg_color"] = from_union(
                [from_str, from_none], self.external_container_bg_color
            )
        if self.external_container_border_color is not None:
            result["external_container_border_color"] = from_union(
                [from_str, from_none], self.external_container_border_color
            )
        if self.external_container_db_bg_color is not None:
            result["external_container_db_bg_color"] = from_union(
                [from_str, from_none], self.external_container_db_bg_color
            )
        if self.external_container_db_border_color is not None:
            result["external_container_db_border_color"] = from_union(
                [from_str, from_none], self.external_container_db_border_color
            )
        if self.external_container_db_font is not None:
            result["external_container_dbFont"] = self.external_container_db_font
        if self.external_container_db_font_family is not None:
            result["external_container_dbFontFamily"] = from_union(
                [from_str, from_none], self.external_container_db_font_family
            )
        if self.external_container_db_font_size is not None:
            result["external_container_dbFontSize"] = from_union(
                [to_float, from_str, from_none], self.external_container_db_font_size
            )
        if self.external_container_db_font_weight is not None:
            result["external_container_dbFontWeight"] = from_union(
                [to_float, from_str, from_none], self.external_container_db_font_weight
            )
        if self.external_container_queue_bg_color is not None:
            result["external_container_queue_bg_color"] = from_union(
                [from_str, from_none], self.external_container_queue_bg_color
            )
        if self.external_container_queue_border_color is not None:
            result["external_container_queue_border_color"] = from_union(
                [from_str, from_none], self.external_container_queue_border_color
            )
        if self.external_container_queue_font is not None:
            result["external_container_queueFont"] = self.external_container_queue_font
        if self.external_container_queue_font_family is not None:
            result["external_container_queueFontFamily"] = from_union(
                [from_str, from_none], self.external_container_queue_font_family
            )
        if self.external_container_queue_font_size is not None:
            result["external_container_queueFontSize"] = from_union(
                [to_float, from_str, from_none], self.external_container_queue_font_size
            )
        if self.external_container_queue_font_weight is not None:
            result["external_container_queueFontWeight"] = from_union(
                [to_float, from_str, from_none], self.external_container_queue_font_weight
            )
        if self.external_container_font is not None:
            result["external_containerFont"] = self.external_container_font
        if self.external_container_font_family is not None:
            result["external_containerFontFamily"] = from_union(
                [from_str, from_none], self.external_container_font_family
            )
        if self.external_container_font_size is not None:
            result["external_containerFontSize"] = from_union(
                [to_float, from_str, from_none], self.external_container_font_size
            )
        if self.external_container_font_weight is not None:
            result["external_containerFontWeight"] = from_union(
                [to_float, from_str, from_none], self.external_container_font_weight
            )
        if self.external_person_bg_color is not None:
            result["external_person_bg_color"] = from_union(
                [from_str, from_none], self.external_person_bg_color
            )
        if self.external_person_border_color is not None:
            result["external_person_border_color"] = from_union(
                [from_str, from_none], self.external_person_border_color
            )
        if self.external_person_font is not None:
            result["external_personFont"] = self.external_person_font
        if self.external_person_font_family is not None:
            result["external_personFontFamily"] = from_union(
                [from_str, from_none], self.external_person_font_family
            )
        if self.external_person_font_size is not None:
            result["external_personFontSize"] = from_union(
                [to_float, from_str, from_none], self.external_person_font_size
            )
        if self.external_person_font_weight is not None:
            result["external_personFontWeight"] = from_union(
                [to_float, from_str, from_none], self.external_person_font_weight
            )
        if self.external_system_bg_color is not None:
            result["external_system_bg_color"] = from_union(
                [from_str, from_none], self.external_system_bg_color
            )
        if self.external_system_border_color is not None:
            result["external_system_border_color"] = from_union(
                [from_str, from_none], self.external_system_border_color
            )
        if self.external_system_db_bg_color is not None:
            result["external_system_db_bg_color"] = from_union(
                [from_str, from_none], self.external_system_db_bg_color
            )
        if self.external_system_db_border_color is not None:
            result["external_system_db_border_color"] = from_union(
                [from_str, from_none], self.external_system_db_border_color
            )
        if self.external_system_db_font is not None:
            result["external_system_dbFont"] = self.external_system_db_font
        if self.external_system_db_font_family is not None:
            result["external_system_dbFontFamily"] = from_union(
                [from_str, from_none], self.external_system_db_font_family
            )
        if self.external_system_db_font_size is not None:
            result["external_system_dbFontSize"] = from_union(
                [to_float, from_str, from_none], self.external_system_db_font_size
            )
        if self.external_system_db_font_weight is not None:
            result["external_system_dbFontWeight"] = from_union(
                [to_float, from_str, from_none], self.external_system_db_font_weight
            )
        if self.external_system_queue_bg_color is not None:
            result["external_system_queue_bg_color"] = from_union(
                [from_str, from_none], self.external_system_queue_bg_color
            )
        if self.external_system_queue_border_color is not None:
            result["external_system_queue_border_color"] = from_union(
                [from_str, from_none], self.external_system_queue_border_color
            )
        if self.external_system_queue_font is not None:
            result["external_system_queueFont"] = self.external_system_queue_font
        if self.external_system_queue_font_family is not None:
            result["external_system_queueFontFamily"] = from_union(
                [from_str, from_none], self.external_system_queue_font_family
            )
        if self.external_system_queue_font_size is not None:
            result["external_system_queueFontSize"] = from_union(
                [to_float, from_str, from_none], self.external_system_queue_font_size
            )
        if self.external_system_queue_font_weight is not None:
            result["external_system_queueFontWeight"] = from_union(
                [to_float, from_str, from_none], self.external_system_queue_font_weight
            )
        if self.external_system_font is not None:
            result["external_systemFont"] = self.external_system_font
        if self.external_system_font_family is not None:
            result["external_systemFontFamily"] = from_union(
                [from_str, from_none], self.external_system_font_family
            )
        if self.external_system_font_size is not None:
            result["external_systemFontSize"] = from_union(
                [to_float, from_str, from_none], self.external_system_font_size
            )
        if self.external_system_font_weight is not None:
            result["external_systemFontWeight"] = from_union(
                [to_float, from_str, from_none], self.external_system_font_weight
            )
        if self.message_font is not None:
            result["messageFont"] = self.message_font
        if self.message_font_family is not None:
            result["messageFontFamily"] = from_union(
                [from_str, from_none], self.message_font_family
            )
        if self.message_font_size is not None:
            result["messageFontSize"] = from_union(
                [to_float, from_str, from_none], self.message_font_size
            )
        if self.message_font_weight is not None:
            result["messageFontWeight"] = from_union(
                [to_float, from_str, from_none], self.message_font_weight
            )
        if self.next_line_padding_x is not None:
            result["nextLinePaddingX"] = from_union([to_float, from_none], self.next_line_padding_x)
        if self.person_bg_color is not None:
            result["person_bg_color"] = from_union([from_str, from_none], self.person_bg_color)
        if self.person_border_color is not None:
            result["person_border_color"] = from_union(
                [from_str, from_none], self.person_border_color
            )
        if self.person_font is not None:
            result["personFont"] = self.person_font
        if self.person_font_family is not None:
            result["personFontFamily"] = from_union([from_str, from_none], self.person_font_family)
        if self.person_font_size is not None:
            result["personFontSize"] = from_union(
                [to_float, from_str, from_none], self.person_font_size
            )
        if self.person_font_weight is not None:
            result["personFontWeight"] = from_union(
                [to_float, from_str, from_none], self.person_font_weight
            )
        if self.system_bg_color is not None:
            result["system_bg_color"] = from_union([from_str, from_none], self.system_bg_color)
        if self.system_border_color is not None:
            result["system_border_color"] = from_union(
                [from_str, from_none], self.system_border_color
            )
        if self.system_db_bg_color is not None:
            result["system_db_bg_color"] = from_union(
                [from_str, from_none], self.system_db_bg_color
            )
        if self.system_db_border_color is not None:
            result["system_db_border_color"] = from_union(
                [from_str, from_none], self.system_db_border_color
            )
        if self.system_db_font is not None:
            result["system_dbFont"] = self.system_db_font
        if self.system_db_font_family is not None:
            result["system_dbFontFamily"] = from_union(
                [from_str, from_none], self.system_db_font_family
            )
        if self.system_db_font_size is not None:
            result["system_dbFontSize"] = from_union(
                [to_float, from_str, from_none], self.system_db_font_size
            )
        if self.system_db_font_weight is not None:
            result["system_dbFontWeight"] = from_union(
                [to_float, from_str, from_none], self.system_db_font_weight
            )
        if self.system_queue_bg_color is not None:
            result["system_queue_bg_color"] = from_union(
                [from_str, from_none], self.system_queue_bg_color
            )
        if self.system_queue_border_color is not None:
            result["system_queue_border_color"] = from_union(
                [from_str, from_none], self.system_queue_border_color
            )
        if self.system_queue_font is not None:
            result["system_queueFont"] = self.system_queue_font
        if self.system_queue_font_family is not None:
            result["system_queueFontFamily"] = from_union(
                [from_str, from_none], self.system_queue_font_family
            )
        if self.system_queue_font_size is not None:
            result["system_queueFontSize"] = from_union(
                [to_float, from_str, from_none], self.system_queue_font_size
            )
        if self.system_queue_font_weight is not None:
            result["system_queueFontWeight"] = from_union(
                [to_float, from_str, from_none], self.system_queue_font_weight
            )
        if self.system_font is not None:
            result["systemFont"] = self.system_font
        if self.system_font_family is not None:
            result["systemFontFamily"] = from_union([from_str, from_none], self.system_font_family)
        if self.system_font_size is not None:
            result["systemFontSize"] = from_union(
                [to_float, from_str, from_none], self.system_font_size
            )
        if self.system_font_weight is not None:
            result["systemFontWeight"] = from_union(
                [to_float, from_str, from_none], self.system_font_weight
            )
        if self.wrap is not None:
            result["wrap"] = from_union([from_bool, from_none], self.wrap)
        if self.wrap_padding is not None:
            result["wrapPadding"] = from_union([to_float, from_none], self.wrap_padding)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


@dataclass
class CynefinDiagramConfig(DataModelHelper):
    """Configuration for Cynefin framework diagrams."""

    boundary_amplitude: Optional[float] = None
    """Waviness amplitude of domain boundaries (0 for straight)."""

    height: Optional[float] = None
    """The height of the Cynefin diagram."""

    padding: Optional[float] = None
    """Padding around the diagram."""

    seed: Optional[float] = None
    """Deterministic seed for boundary waviness. When 0 (default) the seed is derived
    from the diagram's SVG element id, which varies per render. Set any non-zero
    number to produce identical boundaries on every render — required for visual
    regression tests to be stable.
    """
    show_domain_descriptions: Optional[bool] = None
    """Show decision model and practice type labels."""

    width: Optional[float] = None
    """The width of the Cynefin diagram."""

    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_max_width: Optional[bool] = None
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "CynefinDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        boundary_amplitude = from_union([from_float, from_none], obj.get("boundaryAmplitude"))
        height = from_union([from_float, from_none], obj.get("height"))
        padding = from_union([from_float, from_none], obj.get("padding"))
        seed = from_union([from_float, from_none], obj.get("seed"))
        show_domain_descriptions = from_union(
            [from_bool, from_none], obj.get("showDomainDescriptions")
        )
        width = from_union([from_float, from_none], obj.get("width"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        look = from_union([Look, from_none], obj.get("look"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_max_width = from_union([from_bool, from_none], obj.get("useMaxWidth"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return CynefinDiagramConfig(
            boundary_amplitude,
            height,
            padding,
            seed,
            show_domain_descriptions,
            width,
            layout,
            look,
            theme,
            use_max_width,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.boundary_amplitude is not None:
            result["boundaryAmplitude"] = from_union([to_float, from_none], self.boundary_amplitude)
        if self.height is not None:
            result["height"] = from_union([to_float, from_none], self.height)
        if self.padding is not None:
            result["padding"] = from_union([to_float, from_none], self.padding)
        if self.seed is not None:
            result["seed"] = from_union([to_float, from_none], self.seed)
        if self.show_domain_descriptions is not None:
            result["showDomainDescriptions"] = from_union(
                [from_bool, from_none], self.show_domain_descriptions
            )
        if self.width is not None:
            result["width"] = from_union([to_float, from_none], self.width)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_max_width is not None:
            result["useMaxWidth"] = from_union([from_bool, from_none], self.use_max_width)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


class ConsiderModelOrder(Enum):
    """Preserves the order of nodes and edges in the model file if this does not lead to
    additional edge crossings. Depending on the strategy this is not always possible since
    the node and edge order might be conflicting.
    """

    NODES_AND_EDGES = "NODES_AND_EDGES"
    NONE = "NONE"
    PREFER_EDGES = "PREFER_EDGES"
    PREFER_NODES = "PREFER_NODES"


class CycleBreakingStrategy(Enum):
    """This strategy decides how to find cycles in the graph and deciding which edges need
    adjustment to break loops.
    """

    DEPTH_FIRST = "DEPTH_FIRST"
    GREEDY = "GREEDY"
    GREEDY_MODEL_ORDER = "GREEDY_MODEL_ORDER"
    INTERACTIVE = "INTERACTIVE"
    MODEL_ORDER = "MODEL_ORDER"


class LayeringStrategy(Enum):
    """Elk specific option deciding which layer each node is assigned to — the
    column in a left-to-right diagram, the row in a top-down one. This is
    the coarsest of the three placement decisions, so changing it moves
    nodes further than anything else short of altering spacing.

    NETWORK_SIMPLEX aims for the fewest long edges. LONGEST_PATH pushes
    every node as late as it can go. COFFMAN_GRAHAM bounds how many nodes
    share a layer, giving a more even, block-like shape on wide graphs.
    MIN_WIDTH and STRETCH_WIDTH trade edge length for a narrower or wider
    drawing. INTERACTIVE honours positions already on the nodes.
    """

    COFFMAN_GRAHAM = "COFFMAN_GRAHAM"
    INTERACTIVE = "INTERACTIVE"
    LONGEST_PATH = "LONGEST_PATH"
    LONGEST_PATH_SOURCE = "LONGEST_PATH_SOURCE"
    MIN_WIDTH = "MIN_WIDTH"
    NETWORK_SIMPLEX = "NETWORK_SIMPLEX"
    STRETCH_WIDTH = "STRETCH_WIDTH"


class LineHopsEnum(Enum):
    ARC = "arc"
    GAP = "gap"


class NodePlacementAlignment(Enum):
    """Elk specific option affecting Brandes-Koepf node placement alignment.
    BALANCED combines the four directional alignments; NONE picks the
    smallest result. Defaults to BALANCED for the default preset and NONE
    for named non-default presets.
    """

    BALANCED = "BALANCED"
    LEFTDOWN = "LEFTDOWN"
    LEFTUP = "LEFTUP"
    NONE = "NONE"
    RIGHTDOWN = "RIGHTDOWN"
    RIGHTUP = "RIGHTUP"


class NodePlacementStrategy(Enum):
    """Elk specific option affecting how nodes are placed."""

    BRANDES_KOEPF = "BRANDES_KOEPF"
    LINEAR_SEGMENTS = "LINEAR_SEGMENTS"
    NETWORK_SIMPLEX = "NETWORK_SIMPLEX"
    SIMPLE = "SIMPLE"


class Preset(Enum):
    """Named combination of layering, node placement, placement alignment
    and cycle breaking options. Explicit options override the preset for
    that option; the remaining preset values still apply.

    `default` — network simplex layering, balanced Brandes-Koepf placement
    at the top level and inside subgraphs, and depth-first cycle breaking.
    Balanced placement favors centered branches and composite-state entries,
    sometimes at the cost of a wider or taller drawing. It does not
    guarantee that every edge attaches to the center of its target.

    `legacy` — Brandes-Koepf placement with NONE alignment and ELK's own
    greedy cycle breaking. Reproduces the rendering before presets existed.

    `modelOrder` — network simplex layering and top-level placement,
    Brandes-Koepf placement inside subgraphs, NONE alignment, and greedy
    model-order cycle breaking, which favors declaration order.

    `depthFirst` — the previous default: network simplex layering and
    top-level placement, Brandes-Koepf placement inside subgraphs, NONE
    alignment, and depth-first cycle breaking.

    Setting `layeringStrategy`, `nodePlacementStrategy`,
    `nodePlacementAlignment` or `cycleBreakingStrategy` explicitly overrides
    the preset for that option, including an explicit NONE alignment.
    """

    DEFAULT = "default"
    DEPTH_FIRST = "depthFirst"
    LEGACY = "legacy"
    MODEL_ORDER = "modelOrder"


@dataclass
class Elk(DataModelHelper):
    consider_model_order: Optional[ConsiderModelOrder] = None
    """Preserves the order of nodes and edges in the model file if this does not lead to
    additional edge crossings. Depending on the strategy this is not always possible since
    the node and edge order might be conflicting.
    """
    cycle_breaking_strategy: Optional[CycleBreakingStrategy] = None
    """This strategy decides how to find cycles in the graph and deciding which edges need
    adjustment to break loops.
    """
    force_node_model_order: Optional[bool] = None
    """The node order given by the model does not change to produce a better layout. E.g. if
    node A is before node B in the model this is not changed during crossing minimization.
    This assumes that the node model order is already respected before crossing minimization.
    This can be achieved by setting considerModelOrder.strategy to NODES_AND_EDGES.
    """
    keep_entry_node_on_top: Optional[bool] = None
    """Elk specific option that keeps the entry node of a recursive flow at the top of the
    layout.
    
    When a flow loops back on itself (a back-edge to an earlier node), ELK's degree-based
    cycle-breaking has no notion of an "entry point" and may rank the first-declared node in
    the middle, scrambling the reading order. When enabled, the entry node of each cyclic
    component is pinned to the first layer so the diagram still reads from its entry. Acyclic
    flows always have a natural source, so this has no effect on them.
    
    Only applies when the cyclic flow has no node without incoming edges: if the loop is fed
    from outside (e.g. a start node pointing into it), that component already has a natural
    source and nothing is pinned. Detection is also scoped per container, so cycles that
    cross a subgraph boundary are not detected.
    """
    layering_layer_bound: Optional[float] = None
    """Elk specific option capping how many nodes COFFMAN_GRAHAM will put in
    one layer. Ignored by every other layering strategy. Lower values give
    a taller, narrower drawing.
    """
    layering_strategy: Optional[LayeringStrategy] = None
    """Elk specific option deciding which layer each node is assigned to — the
    column in a left-to-right diagram, the row in a top-down one. This is
    the coarsest of the three placement decisions, so changing it moves
    nodes further than anything else short of altering spacing.
    
    NETWORK_SIMPLEX aims for the fewest long edges. LONGEST_PATH pushes
    every node as late as it can go. COFFMAN_GRAHAM bounds how many nodes
    share a layer, giving a more even, block-like shape on wide graphs.
    MIN_WIDTH and STRETCH_WIDTH trade edge length for a narrower or wider
    drawing. INTERACTIVE honours positions already on the nodes.
    """
    line_hops: Optional[Union[bool, LineHopsEnum]] = None
    """Renders edge crossings as small arcs ("hops") or visible gaps, so that
    it is clear which line passes over which where two edges meet.
    
    The edge that gives way loses its corner rounding for the segment
    carrying the hop, which is the trade for a readable crossing. Curved
    edges are skipped rather than rewritten, to avoid corrupting their
    geometry. Set to `false` to draw plain crossings.
    """
    merge_edges: Optional[bool] = None
    """Elk specific option that allows edges to share path where it convenient. It can make for
    pretty diagrams but can also make it harder to read the diagram.
    """
    node_placement_alignment: Optional[NodePlacementAlignment] = None
    """Elk specific option affecting Brandes-Koepf node placement alignment.
    BALANCED combines the four directional alignments; NONE picks the
    smallest result. Defaults to BALANCED for the default preset and NONE
    for named non-default presets.
    """
    node_placement_strategy: Optional[NodePlacementStrategy] = None
    """Elk specific option affecting how nodes are placed."""

    orient_feedback_edges: Optional[bool] = None
    """Routes an edge that re-enters a subgraph downstream instead of around the subgraph.
    
    ELK lays out a subgraph as one node of its parent graph. A node outside a subgraph that
    both receives an edge from it and sends one back into it therefore closes a cycle there,
    even when the nodes inside do not. ELK breaks that cycle by reversing one of the edges
    and routes it into the subgraph's input side, around the outside of the subgraph.
    
    When enabled, such edges are found before layout, on the graph with each subgraph
    collapsed, and handed to ELK in the other direction. The edge is drawn with its arrowhead
    at its real target. Cycles between plain nodes are left to `cycleBreakingStrategy`.
    """
    preset: Optional[Preset] = None
    """Named combination of layering, node placement, placement alignment
    and cycle breaking options. Explicit options override the preset for
    that option; the remaining preset values still apply.
    
    `default` — network simplex layering, balanced Brandes-Koepf placement
    at the top level and inside subgraphs, and depth-first cycle breaking.
    Balanced placement favors centered branches and composite-state entries,
    sometimes at the cost of a wider or taller drawing. It does not
    guarantee that every edge attaches to the center of its target.
    
    `legacy` — Brandes-Koepf placement with NONE alignment and ELK's own
    greedy cycle breaking. Reproduces the rendering before presets existed.
    
    `modelOrder` — network simplex layering and top-level placement,
    Brandes-Koepf placement inside subgraphs, NONE alignment, and greedy
    model-order cycle breaking, which favors declaration order.
    
    `depthFirst` — the previous default: network simplex layering and
    top-level placement, Brandes-Koepf placement inside subgraphs, NONE
    alignment, and depth-first cycle breaking.
    
    Setting `layeringStrategy`, `nodePlacementStrategy`,
    `nodePlacementAlignment` or `cycleBreakingStrategy` explicitly overrides
    the preset for that option, including an explicit NONE alignment.
    """
    straighten_edges: Optional[bool] = None
    """Straightens an edge that leaves or enters a node with a tiny step.
    
    ELK spreads an edge's port evenly along a node's side but routes the
    edge down a channel whose row rarely lines up with that port exactly,
    leaving a staircase of a few pixels right at the border. With rounded
    corners the two micro-bends land on top of each other and read as a
    kink. Enabling this moves the channel onto the port's row and drops
    the step, so the edge draws as one straight line and both ports stay
    exactly where the layout put them.
    
    Only the step next to a node is touched, and only when the edge
    continues the same way afterwards, so a real turn is never collapsed.
    An edge is left alone entirely when moving its run would drag the far
    port, or would introduce a crossing.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Elk":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        consider_model_order = from_union(
            [ConsiderModelOrder, from_none], obj.get("considerModelOrder")
        )
        cycle_breaking_strategy = from_union(
            [CycleBreakingStrategy, from_none], obj.get("cycleBreakingStrategy")
        )
        force_node_model_order = from_union([from_bool, from_none], obj.get("forceNodeModelOrder"))
        keep_entry_node_on_top = from_union([from_bool, from_none], obj.get("keepEntryNodeOnTop"))
        layering_layer_bound = from_union([from_float, from_none], obj.get("layeringLayerBound"))
        layering_strategy = from_union([LayeringStrategy, from_none], obj.get("layeringStrategy"))
        line_hops = from_union([from_bool, LineHopsEnum, from_none], obj.get("lineHops"))
        merge_edges = from_union([from_bool, from_none], obj.get("mergeEdges"))
        node_placement_alignment = from_union(
            [NodePlacementAlignment, from_none], obj.get("nodePlacementAlignment")
        )
        node_placement_strategy = from_union(
            [NodePlacementStrategy, from_none], obj.get("nodePlacementStrategy")
        )
        orient_feedback_edges = from_union([from_bool, from_none], obj.get("orientFeedbackEdges"))
        preset = from_union([Preset, from_none], obj.get("preset"))
        straighten_edges = from_union([from_bool, from_none], obj.get("straightenEdges"))
        return Elk(
            consider_model_order,
            cycle_breaking_strategy,
            force_node_model_order,
            keep_entry_node_on_top,
            layering_layer_bound,
            layering_strategy,
            line_hops,
            merge_edges,
            node_placement_alignment,
            node_placement_strategy,
            orient_feedback_edges,
            preset,
            straighten_edges,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.consider_model_order is not None:
            result["considerModelOrder"] = from_union(
                [lambda x: to_enum(ConsiderModelOrder, x), from_none], self.consider_model_order
            )
        if self.cycle_breaking_strategy is not None:
            result["cycleBreakingStrategy"] = from_union(
                [lambda x: to_enum(CycleBreakingStrategy, x), from_none],
                self.cycle_breaking_strategy,
            )
        if self.force_node_model_order is not None:
            result["forceNodeModelOrder"] = from_union(
                [from_bool, from_none], self.force_node_model_order
            )
        if self.keep_entry_node_on_top is not None:
            result["keepEntryNodeOnTop"] = from_union(
                [from_bool, from_none], self.keep_entry_node_on_top
            )
        if self.layering_layer_bound is not None:
            result["layeringLayerBound"] = from_union(
                [to_float, from_none], self.layering_layer_bound
            )
        if self.layering_strategy is not None:
            result["layeringStrategy"] = from_union(
                [lambda x: to_enum(LayeringStrategy, x), from_none], self.layering_strategy
            )
        if self.line_hops is not None:
            result["lineHops"] = from_union(
                [from_bool, lambda x: to_enum(LineHopsEnum, x), from_none], self.line_hops
            )
        if self.merge_edges is not None:
            result["mergeEdges"] = from_union([from_bool, from_none], self.merge_edges)
        if self.node_placement_alignment is not None:
            result["nodePlacementAlignment"] = from_union(
                [lambda x: to_enum(NodePlacementAlignment, x), from_none],
                self.node_placement_alignment,
            )
        if self.node_placement_strategy is not None:
            result["nodePlacementStrategy"] = from_union(
                [lambda x: to_enum(NodePlacementStrategy, x), from_none],
                self.node_placement_strategy,
            )
        if self.orient_feedback_edges is not None:
            result["orientFeedbackEdges"] = from_union(
                [from_bool, from_none], self.orient_feedback_edges
            )
        if self.preset is not None:
            result["preset"] = from_union([lambda x: to_enum(Preset, x), from_none], self.preset)
        if self.straighten_edges is not None:
            result["straightenEdges"] = from_union([from_bool, from_none], self.straighten_edges)
        return result


class LayoutDirection(Enum):
    """Directional bias for layout of entities"""

    BT = "BT"
    LR = "LR"
    RL = "RL"
    TB = "TB"


@dataclass
class ErDiagramConfig(DataModelHelper):
    """The object containing configurations specific for entity relationship diagrams"""

    diagram_padding: int
    """The amount of padding around the diagram as a whole so that embedded
    diagrams have margins, expressed in pixels.
    """
    entity_padding: int
    """The minimum internal padding between text in an entity box and the enclosing box borders.
    Expressed in pixels.
    """
    fill: str
    """Fill color of entity boxes"""

    layout_direction: LayoutDirection
    """Directional bias for layout of entities"""

    min_entity_height: int
    """The minimum height of an entity box. Expressed in pixels."""

    min_entity_width: int
    """The minimum width of an entity box. Expressed in pixels."""

    stroke: str
    """Stroke color of box edges and lines."""

    title_top_margin: int
    use_max_width: bool
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    font_size: Optional[int] = None
    """Font size (expressed as an integer representing a number of pixels)"""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    node_spacing: Optional[int] = None
    rank_spacing: Optional[int] = None
    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ErDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        diagram_padding = from_int(obj.get("diagramPadding"))
        entity_padding = from_int(obj.get("entityPadding"))
        fill = from_str(obj.get("fill"))
        layout_direction = LayoutDirection(obj.get("layoutDirection"))
        min_entity_height = from_int(obj.get("minEntityHeight"))
        min_entity_width = from_int(obj.get("minEntityWidth"))
        stroke = from_str(obj.get("stroke"))
        title_top_margin = from_int(obj.get("titleTopMargin"))
        use_max_width = from_bool(obj.get("useMaxWidth"))
        font_size = from_union([from_int, from_none], obj.get("fontSize"))
        look = from_union([Look, from_none], obj.get("look"))
        node_spacing = from_union([from_int, from_none], obj.get("nodeSpacing"))
        rank_spacing = from_union([from_int, from_none], obj.get("rankSpacing"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return ErDiagramConfig(
            diagram_padding,
            entity_padding,
            fill,
            layout_direction,
            min_entity_height,
            min_entity_width,
            stroke,
            title_top_margin,
            use_max_width,
            font_size,
            look,
            node_spacing,
            rank_spacing,
            theme,
            layout,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["diagramPadding"] = from_int(self.diagram_padding)
        result["entityPadding"] = from_int(self.entity_padding)
        result["fill"] = from_str(self.fill)
        result["layoutDirection"] = to_enum(LayoutDirection, self.layout_direction)
        result["minEntityHeight"] = from_int(self.min_entity_height)
        result["minEntityWidth"] = from_int(self.min_entity_width)
        result["stroke"] = from_str(self.stroke)
        result["titleTopMargin"] = from_int(self.title_top_margin)
        result["useMaxWidth"] = from_bool(self.use_max_width)
        if self.font_size is not None:
            result["fontSize"] = from_union([from_int, from_none], self.font_size)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.node_spacing is not None:
            result["nodeSpacing"] = from_union([from_int, from_none], self.node_spacing)
        if self.rank_spacing is not None:
            result["rankSpacing"] = from_union([from_int, from_none], self.rank_spacing)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


@dataclass
class EventModelingDiagramConfig(DataModelHelper):
    """The object containing configurations specific for Event Modeling diagrams."""

    padding: Optional[float] = None
    """The padding around the Event Modeling diagram."""

    row_height: Optional[float] = None
    """The height of each row in the Event Modeling diagram."""

    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_max_width: Optional[bool] = None
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "EventModelingDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        padding = from_union([from_float, from_none], obj.get("padding"))
        row_height = from_union([from_float, from_none], obj.get("rowHeight"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        look = from_union([Look, from_none], obj.get("look"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_max_width = from_union([from_bool, from_none], obj.get("useMaxWidth"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return EventModelingDiagramConfig(
            padding, row_height, layout, look, theme, use_max_width, use_width
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.padding is not None:
            result["padding"] = from_union([to_float, from_none], self.padding)
        if self.row_height is not None:
            result["rowHeight"] = from_union([to_float, from_none], self.row_height)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_max_width is not None:
            result["useMaxWidth"] = from_union([from_bool, from_none], self.use_max_width)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


class Curve(Enum):
    """Defines how mermaid renders curves for flowcharts."""

    BASIS = "basis"
    BUMP_X = "bumpX"
    BUMP_Y = "bumpY"
    CARDINAL = "cardinal"
    CATMULL_ROM = "catmullRom"
    LINEAR = "linear"
    MONOTONE_X = "monotoneX"
    MONOTONE_Y = "monotoneY"
    NATURAL = "natural"
    ROUNDED = "rounded"
    STEP = "step"
    STEP_AFTER = "stepAfter"
    STEP_BEFORE = "stepBefore"


@dataclass
class SubGraphTitleMargin(DataModelHelper):
    """Defines a top/bottom margin for subgraph titles"""

    bottom: Optional[int] = None
    top: Optional[int] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "SubGraphTitleMargin":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        bottom = from_union([from_int, from_none], obj.get("bottom"))
        top = from_union([from_int, from_none], obj.get("top"))
        return SubGraphTitleMargin(bottom, top)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.bottom is not None:
            result["bottom"] = from_union([from_int, from_none], self.bottom)
        if self.top is not None:
            result["top"] = from_union([from_int, from_none], self.top)
        return result


@dataclass
class FlowchartDiagramConfig(DataModelHelper):
    """The object containing configurations specific for flowcharts"""

    curve: Curve
    """Defines how mermaid renders curves for flowcharts."""

    diagram_padding: int
    min_node_width: float
    """Minimum width of the label area of a node.
    
    Labels narrower than this are widened to it, so nodes with short text
    get a uniform width; the node's own padding is added on top, the same
    way it is for `wrappingWidth`. Nodes with an explicit width are not
    affected.
    """
    node_spacing: int
    """Defines the spacing between nodes on the same level
    
    Pertains to horizontal spacing for TB (top to bottom) or BT (bottom to top) graphs,
    and the vertical spacing for LR as well as RL graphs.
    """
    rank_spacing: int
    """Defines the spacing between nodes on different levels
    
    Pertains to horizontal spacing for TB (top to bottom) or BT (bottom to top) graphs,
    and the vertical spacing for LR as well as RL graphs.
    """
    sub_graph_title_margin: SubGraphTitleMargin
    """Defines a top/bottom margin for subgraph titles"""

    title_top_margin: int
    wrapping_width: float
    """Width of nodes where text is wrapped.
    
    When using markdown strings the text is wrapped automatically, this
    value sets the max width of a text before it continues on a new line.
    """
    use_max_width: bool
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    arrow_marker_absolute: Optional[bool] = None
    html_labels: Optional[bool] = None
    """**DEPRECATED: Use global `htmlLabels` instead.**
    
    Flag for setting whether or not a html tag should be used for rendering labels on nodes
    and edges.
    This property is deprecated.
    Please use the global `htmlLabels` configuration instead.
    """
    inherit_dir: Optional[bool] = None
    """If true, subgraphs without explicit direction will inherit the global graph direction
    (e.g., LR, TB, RL, BT). Defaults to false to preserve legacy layout behavior.
    """
    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    padding: Optional[float] = None
    """Represents the padding between the labels and the shape
    
    **Only used in new experimental rendering.**
    """
    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "FlowchartDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        curve = Curve(obj.get("curve"))
        diagram_padding = from_int(obj.get("diagramPadding"))
        min_node_width = from_float(obj.get("minNodeWidth"))
        node_spacing = from_int(obj.get("nodeSpacing"))
        rank_spacing = from_int(obj.get("rankSpacing"))
        sub_graph_title_margin = SubGraphTitleMargin.from_dict(obj.get("subGraphTitleMargin"))
        title_top_margin = from_int(obj.get("titleTopMargin"))
        wrapping_width = from_float(obj.get("wrappingWidth"))
        use_max_width = from_bool(obj.get("useMaxWidth"))
        arrow_marker_absolute = from_union([from_bool, from_none], obj.get("arrowMarkerAbsolute"))
        html_labels = from_union([from_bool, from_none], obj.get("htmlLabels"))
        inherit_dir = from_union([from_bool, from_none], obj.get("inheritDir"))
        look = from_union([Look, from_none], obj.get("look"))
        padding = from_union([from_float, from_none], obj.get("padding"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return FlowchartDiagramConfig(
            curve,
            diagram_padding,
            min_node_width,
            node_spacing,
            rank_spacing,
            sub_graph_title_margin,
            title_top_margin,
            wrapping_width,
            use_max_width,
            arrow_marker_absolute,
            html_labels,
            inherit_dir,
            look,
            padding,
            theme,
            layout,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["curve"] = to_enum(Curve, self.curve)
        result["diagramPadding"] = from_int(self.diagram_padding)
        result["minNodeWidth"] = to_float(self.min_node_width)
        result["nodeSpacing"] = from_int(self.node_spacing)
        result["rankSpacing"] = from_int(self.rank_spacing)
        result["subGraphTitleMargin"] = to_class(SubGraphTitleMargin, self.sub_graph_title_margin)
        result["titleTopMargin"] = from_int(self.title_top_margin)
        result["wrappingWidth"] = to_float(self.wrapping_width)
        result["useMaxWidth"] = from_bool(self.use_max_width)
        if self.arrow_marker_absolute is not None:
            result["arrowMarkerAbsolute"] = from_union(
                [from_bool, from_none], self.arrow_marker_absolute
            )
        if self.html_labels is not None:
            result["htmlLabels"] = from_union([from_bool, from_none], self.html_labels)
        if self.inherit_dir is not None:
            result["inheritDir"] = from_union([from_bool, from_none], self.inherit_dir)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.padding is not None:
            result["padding"] = from_union([to_float, from_none], self.padding)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


class DisplayMode(Enum):
    """Controls the display mode."""

    COMPACT = "compact"
    EMPTY = ""


class Weekday(Enum):
    """On which day a week-based interval should start"""

    FRIDAY = "friday"
    MONDAY = "monday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"
    THURSDAY = "thursday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"


@dataclass
class GanttDiagramConfig(DataModelHelper):
    """The object containing configurations specific for gantt diagrams"""

    axis_format: str
    """Date/time format of the axis
    
    This might need adjustment to match your locale and preferences.
    """
    bar_height: int
    """The height of the bars in the graph"""

    font_size: int
    """Font size"""

    grid_line_start_padding: int
    """Vertical starting position of the grid lines"""

    left_padding: int
    """The space allocated for the section name to the left of the activities"""

    number_section_styles: int
    """The number of alternating section styles"""

    right_padding: int
    """The space allocated for the section name to the right of the activities"""

    section_font_size: int
    """Font size for sections"""

    title_top_margin: int
    top_axis: bool
    """When this flag is set, date labels will be added to the top of the chart"""

    top_padding: int
    """Margin between title and gantt diagram and between axis and gantt diagram."""

    weekday: Weekday
    """On which day a week-based interval should start"""

    use_max_width: bool
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    bar_gap: Optional[int] = None
    """The margin between the different activities in the gantt diagram"""

    display_mode: Optional[DisplayMode] = None
    """Controls the display mode."""

    tick_interval: Optional[str] = None
    """axis ticks
    
    Pattern is:
    
    ```javascript
    /^([1-9][0-9]*)(millisecond|second|minute|hour|day|week|month)$/
    ```
    """
    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "GanttDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        axis_format = from_str(obj.get("axisFormat"))
        bar_height = from_int(obj.get("barHeight"))
        font_size = from_int(obj.get("fontSize"))
        grid_line_start_padding = from_int(obj.get("gridLineStartPadding"))
        left_padding = from_int(obj.get("leftPadding"))
        number_section_styles = from_int(obj.get("numberSectionStyles"))
        right_padding = from_int(obj.get("rightPadding"))
        section_font_size = from_int(obj.get("sectionFontSize"))
        title_top_margin = from_int(obj.get("titleTopMargin"))
        top_axis = from_bool(obj.get("topAxis"))
        top_padding = from_int(obj.get("topPadding"))
        weekday = Weekday(obj.get("weekday"))
        use_max_width = from_bool(obj.get("useMaxWidth"))
        bar_gap = from_union([from_int, from_none], obj.get("barGap"))
        display_mode = from_union([DisplayMode, from_none], obj.get("displayMode"))
        tick_interval = from_union([from_str, from_none], obj.get("tickInterval"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        look = from_union([Look, from_none], obj.get("look"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return GanttDiagramConfig(
            axis_format,
            bar_height,
            font_size,
            grid_line_start_padding,
            left_padding,
            number_section_styles,
            right_padding,
            section_font_size,
            title_top_margin,
            top_axis,
            top_padding,
            weekday,
            use_max_width,
            bar_gap,
            display_mode,
            tick_interval,
            layout,
            look,
            theme,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["axisFormat"] = from_str(self.axis_format)
        result["barHeight"] = from_int(self.bar_height)
        result["fontSize"] = from_int(self.font_size)
        result["gridLineStartPadding"] = from_int(self.grid_line_start_padding)
        result["leftPadding"] = from_int(self.left_padding)
        result["numberSectionStyles"] = from_int(self.number_section_styles)
        result["rightPadding"] = from_int(self.right_padding)
        result["sectionFontSize"] = from_int(self.section_font_size)
        result["titleTopMargin"] = from_int(self.title_top_margin)
        result["topAxis"] = from_bool(self.top_axis)
        result["topPadding"] = from_int(self.top_padding)
        result["weekday"] = to_enum(Weekday, self.weekday)
        result["useMaxWidth"] = from_bool(self.use_max_width)
        if self.bar_gap is not None:
            result["barGap"] = from_union([from_int, from_none], self.bar_gap)
        if self.display_mode is not None:
            result["displayMode"] = from_union(
                [lambda x: to_enum(DisplayMode, x), from_none], self.display_mode
            )
        if self.tick_interval is not None:
            result["tickInterval"] = from_union([from_str, from_none], self.tick_interval)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


@dataclass
class NodeLabel(DataModelHelper):
    height: Optional[float] = None
    width: Optional[float] = None
    x: Optional[float] = None
    y: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "NodeLabel":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        height = from_union([from_float, from_none], obj.get("height"))
        width = from_union([from_float, from_none], obj.get("width"))
        x = from_union([from_float, from_none], obj.get("x"))
        y = from_union([from_float, from_none], obj.get("y"))
        return NodeLabel(height, width, x, y)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.height is not None:
            result["height"] = from_union([to_float, from_none], self.height)
        if self.width is not None:
            result["width"] = from_union([to_float, from_none], self.width)
        if self.x is not None:
            result["x"] = from_union([to_float, from_none], self.x)
        if self.y is not None:
            result["y"] = from_union([to_float, from_none], self.y)
        return result


@dataclass
class GitGraphDiagramConfig(DataModelHelper):
    title_top_margin: int
    """Margin top for the text over the diagram"""

    arrow_marker_absolute: Optional[bool] = None
    """Controls whether or arrow markers in html code are absolute paths or anchors.
    This matters if you are using base tag settings.
    """
    diagram_padding: Optional[float] = None
    main_branch_name: Optional[str] = None
    main_branch_order: Optional[float] = None
    node_label: Optional[NodeLabel] = None
    parallel_commits: Optional[bool] = None
    rotate_commit_label: Optional[bool] = None
    show_branches: Optional[bool] = None
    show_commit_label: Optional[bool] = None
    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_max_width: Optional[bool] = None
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "GitGraphDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        title_top_margin = from_int(obj.get("titleTopMargin"))
        arrow_marker_absolute = from_union([from_bool, from_none], obj.get("arrowMarkerAbsolute"))
        diagram_padding = from_union([from_float, from_none], obj.get("diagramPadding"))
        main_branch_name = from_union([from_str, from_none], obj.get("mainBranchName"))
        main_branch_order = from_union([from_float, from_none], obj.get("mainBranchOrder"))
        node_label = from_union([NodeLabel.from_dict, from_none], obj.get("nodeLabel"))
        parallel_commits = from_union([from_bool, from_none], obj.get("parallelCommits"))
        rotate_commit_label = from_union([from_bool, from_none], obj.get("rotateCommitLabel"))
        show_branches = from_union([from_bool, from_none], obj.get("showBranches"))
        show_commit_label = from_union([from_bool, from_none], obj.get("showCommitLabel"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        look = from_union([Look, from_none], obj.get("look"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_max_width = from_union([from_bool, from_none], obj.get("useMaxWidth"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return GitGraphDiagramConfig(
            title_top_margin,
            arrow_marker_absolute,
            diagram_padding,
            main_branch_name,
            main_branch_order,
            node_label,
            parallel_commits,
            rotate_commit_label,
            show_branches,
            show_commit_label,
            layout,
            look,
            theme,
            use_max_width,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["titleTopMargin"] = from_int(self.title_top_margin)
        if self.arrow_marker_absolute is not None:
            result["arrowMarkerAbsolute"] = from_union(
                [from_bool, from_none], self.arrow_marker_absolute
            )
        if self.diagram_padding is not None:
            result["diagramPadding"] = from_union([to_float, from_none], self.diagram_padding)
        if self.main_branch_name is not None:
            result["mainBranchName"] = from_union([from_str, from_none], self.main_branch_name)
        if self.main_branch_order is not None:
            result["mainBranchOrder"] = from_union([to_float, from_none], self.main_branch_order)
        if self.node_label is not None:
            result["nodeLabel"] = from_union(
                [lambda x: to_class(NodeLabel, x), from_none], self.node_label
            )
        if self.parallel_commits is not None:
            result["parallelCommits"] = from_union([from_bool, from_none], self.parallel_commits)
        if self.rotate_commit_label is not None:
            result["rotateCommitLabel"] = from_union(
                [from_bool, from_none], self.rotate_commit_label
            )
        if self.show_branches is not None:
            result["showBranches"] = from_union([from_bool, from_none], self.show_branches)
        if self.show_commit_label is not None:
            result["showCommitLabel"] = from_union([from_bool, from_none], self.show_commit_label)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_max_width is not None:
            result["useMaxWidth"] = from_union([from_bool, from_none], self.use_max_width)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


@dataclass
class IshikawaDiagramConfig(DataModelHelper):
    """The object containing configurations specific for ishikawa diagrams"""

    diagram_padding: Optional[int] = None
    """The amount of padding around the diagram as a whole so that embedded
    diagrams have margins, expressed in pixels.
    """
    use_max_width: Optional[bool] = None
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "IshikawaDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        diagram_padding = from_union([from_int, from_none], obj.get("diagramPadding"))
        use_max_width = from_union([from_bool, from_none], obj.get("useMaxWidth"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        look = from_union([Look, from_none], obj.get("look"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return IshikawaDiagramConfig(diagram_padding, use_max_width, layout, look, theme, use_width)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.diagram_padding is not None:
            result["diagramPadding"] = from_union([from_int, from_none], self.diagram_padding)
        if self.use_max_width is not None:
            result["useMaxWidth"] = from_union([from_bool, from_none], self.use_max_width)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


class EAlign(Enum):
    """Multiline message alignment

    This sets the text alignment of actor-attached notes
    """

    CENTER = "center"
    LEFT = "left"
    RIGHT = "right"


@dataclass
class JourneyDiagramConfig(DataModelHelper):
    """The object containing configurations specific for journey diagrams"""

    bottom_margin_adj: int
    """Prolongs the edge of the diagram downwards.
    
    Depending on css styling this might need adjustment.
    """
    box_margin: int
    """Margin around loop boxes"""

    box_text_margin: int
    """Margin around the text in loop/alt/opt boxes"""

    diagram_margin_x: int
    diagram_margin_y: int
    height: int
    """Height of actor boxes"""

    left_margin: int
    """Margin between actors"""

    message_align: EAlign
    """Multiline message alignment"""

    message_margin: int
    """Space between messages."""

    note_margin: int
    """Margin around notes"""

    right_angles: bool
    """Curved Arrows become Right Angles
    
    This will display arrows that start and begin at the same node as
    right angles, rather than as curves.
    """
    title_color: str
    """Color of the title text in Journey Diagrams"""

    title_font_family: str
    """Font family to be used for the title text in Journey Diagrams"""

    title_font_size: str
    """Font size to be used for the title text in Journey Diagrams"""

    width: int
    """Width of actor boxes"""

    use_max_width: bool
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    activation_width: Optional[float] = None
    """Width of activation box"""

    actor_colours: Optional[List[str]] = None
    max_label_width: Optional[int] = None
    """Maximum width of actor labels"""

    section_colours: Optional[List[str]] = None
    section_fills: Optional[List[str]] = None
    task_font_family: Optional[str] = None
    task_font_size: Optional[Union[float, str]] = None
    task_margin: Optional[float] = None
    text_placement: Optional[str] = None
    """text placement as: tspan | fo | old only text as before"""

    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "JourneyDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        bottom_margin_adj = from_int(obj.get("bottomMarginAdj"))
        box_margin = from_int(obj.get("boxMargin"))
        box_text_margin = from_int(obj.get("boxTextMargin"))
        diagram_margin_x = from_int(obj.get("diagramMarginX"))
        diagram_margin_y = from_int(obj.get("diagramMarginY"))
        height = from_int(obj.get("height"))
        left_margin = from_int(obj.get("leftMargin"))
        message_align = EAlign(obj.get("messageAlign"))
        message_margin = from_int(obj.get("messageMargin"))
        note_margin = from_int(obj.get("noteMargin"))
        right_angles = from_bool(obj.get("rightAngles"))
        title_color = from_str(obj.get("titleColor"))
        title_font_family = from_str(obj.get("titleFontFamily"))
        title_font_size = from_str(obj.get("titleFontSize"))
        width = from_int(obj.get("width"))
        use_max_width = from_bool(obj.get("useMaxWidth"))
        activation_width = from_union([from_float, from_none], obj.get("activationWidth"))
        actor_colours = from_union(
            [lambda x: from_list(from_str, x), from_none], obj.get("actorColours")
        )
        max_label_width = from_union([from_int, from_none], obj.get("maxLabelWidth"))
        section_colours = from_union(
            [lambda x: from_list(from_str, x), from_none], obj.get("sectionColours")
        )
        section_fills = from_union(
            [lambda x: from_list(from_str, x), from_none], obj.get("sectionFills")
        )
        task_font_family = from_union([from_str, from_none], obj.get("taskFontFamily"))
        task_font_size = from_union([from_float, from_str, from_none], obj.get("taskFontSize"))
        task_margin = from_union([from_float, from_none], obj.get("taskMargin"))
        text_placement = from_union([from_str, from_none], obj.get("textPlacement"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        look = from_union([Look, from_none], obj.get("look"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return JourneyDiagramConfig(
            bottom_margin_adj,
            box_margin,
            box_text_margin,
            diagram_margin_x,
            diagram_margin_y,
            height,
            left_margin,
            message_align,
            message_margin,
            note_margin,
            right_angles,
            title_color,
            title_font_family,
            title_font_size,
            width,
            use_max_width,
            activation_width,
            actor_colours,
            max_label_width,
            section_colours,
            section_fills,
            task_font_family,
            task_font_size,
            task_margin,
            text_placement,
            layout,
            look,
            theme,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["bottomMarginAdj"] = from_int(self.bottom_margin_adj)
        result["boxMargin"] = from_int(self.box_margin)
        result["boxTextMargin"] = from_int(self.box_text_margin)
        result["diagramMarginX"] = from_int(self.diagram_margin_x)
        result["diagramMarginY"] = from_int(self.diagram_margin_y)
        result["height"] = from_int(self.height)
        result["leftMargin"] = from_int(self.left_margin)
        result["messageAlign"] = to_enum(EAlign, self.message_align)
        result["messageMargin"] = from_int(self.message_margin)
        result["noteMargin"] = from_int(self.note_margin)
        result["rightAngles"] = from_bool(self.right_angles)
        result["titleColor"] = from_str(self.title_color)
        result["titleFontFamily"] = from_str(self.title_font_family)
        result["titleFontSize"] = from_str(self.title_font_size)
        result["width"] = from_int(self.width)
        result["useMaxWidth"] = from_bool(self.use_max_width)
        if self.activation_width is not None:
            result["activationWidth"] = from_union([to_float, from_none], self.activation_width)
        if self.actor_colours is not None:
            result["actorColours"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.actor_colours
            )
        if self.max_label_width is not None:
            result["maxLabelWidth"] = from_union([from_int, from_none], self.max_label_width)
        if self.section_colours is not None:
            result["sectionColours"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.section_colours
            )
        if self.section_fills is not None:
            result["sectionFills"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.section_fills
            )
        if self.task_font_family is not None:
            result["taskFontFamily"] = from_union([from_str, from_none], self.task_font_family)
        if self.task_font_size is not None:
            result["taskFontSize"] = from_union(
                [to_float, from_str, from_none], self.task_font_size
            )
        if self.task_margin is not None:
            result["taskMargin"] = from_union([to_float, from_none], self.task_margin)
        if self.text_placement is not None:
            result["textPlacement"] = from_union([from_str, from_none], self.text_placement)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


@dataclass
class KanbanDiagramConfig(DataModelHelper):
    """The object containing configurations specific for kanban diagrams"""

    padding: Optional[float] = None
    section_width: Optional[float] = None
    ticket_base_url: Optional[str] = None
    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_max_width: Optional[bool] = None
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "KanbanDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        padding = from_union([from_float, from_none], obj.get("padding"))
        section_width = from_union([from_float, from_none], obj.get("sectionWidth"))
        ticket_base_url = from_union([from_str, from_none], obj.get("ticketBaseUrl"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        look = from_union([Look, from_none], obj.get("look"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_max_width = from_union([from_bool, from_none], obj.get("useMaxWidth"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return KanbanDiagramConfig(
            padding, section_width, ticket_base_url, layout, look, theme, use_max_width, use_width
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.padding is not None:
            result["padding"] = from_union([to_float, from_none], self.padding)
        if self.section_width is not None:
            result["sectionWidth"] = from_union([to_float, from_none], self.section_width)
        if self.ticket_base_url is not None:
            result["ticketBaseUrl"] = from_union([from_str, from_none], self.ticket_base_url)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_max_width is not None:
            result["useMaxWidth"] = from_union([from_bool, from_none], self.use_max_width)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


class LogLevelEnum(Enum):
    DEBUG = "debug"
    ERROR = "error"
    FATAL = "fatal"
    INFO = "info"
    TRACE = "trace"
    WARN = "warn"


@dataclass
class ClassDiagramConfig(DataModelHelper):
    title_top_margin: int
    use_max_width: bool
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    arrow_marker_absolute: Optional[bool] = None
    """Controls whether or arrow markers in html code are absolute paths or anchors.
    This matters if you are using base tag settings.
    """
    diagram_padding: Optional[int] = None
    divider_margin: Optional[float] = None
    hide_empty_members_box: Optional[bool] = None
    hierarchical_namespaces: Optional[bool] = None
    """When true (default), nested namespaces render as hierarchical clusters,
    with each segment of a dotted name (e.g. `A.B.C`) becoming its own nested
    box. When false, namespaces render in compact mode: only explicitly
    declared namespaces are emitted and their full qualified name is used as
    a single flat label.
    """
    html_labels: Optional[bool] = None
    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    node_spacing: Optional[int] = None
    padding: Optional[float] = None
    rank_spacing: Optional[int] = None
    text_height: Optional[float] = None
    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ClassDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        title_top_margin = from_int(obj.get("titleTopMargin"))
        use_max_width = from_bool(obj.get("useMaxWidth"))
        arrow_marker_absolute = from_union([from_bool, from_none], obj.get("arrowMarkerAbsolute"))
        diagram_padding = from_union([from_int, from_none], obj.get("diagramPadding"))
        divider_margin = from_union([from_float, from_none], obj.get("dividerMargin"))
        hide_empty_members_box = from_union([from_bool, from_none], obj.get("hideEmptyMembersBox"))
        hierarchical_namespaces = from_union(
            [from_bool, from_none], obj.get("hierarchicalNamespaces")
        )
        html_labels = from_union([from_bool, from_none], obj.get("htmlLabels"))
        look = from_union([Look, from_none], obj.get("look"))
        node_spacing = from_union([from_int, from_none], obj.get("nodeSpacing"))
        padding = from_union([from_float, from_none], obj.get("padding"))
        rank_spacing = from_union([from_int, from_none], obj.get("rankSpacing"))
        text_height = from_union([from_float, from_none], obj.get("textHeight"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return ClassDiagramConfig(
            title_top_margin,
            use_max_width,
            arrow_marker_absolute,
            diagram_padding,
            divider_margin,
            hide_empty_members_box,
            hierarchical_namespaces,
            html_labels,
            look,
            node_spacing,
            padding,
            rank_spacing,
            text_height,
            theme,
            layout,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["titleTopMargin"] = from_int(self.title_top_margin)
        result["useMaxWidth"] = from_bool(self.use_max_width)
        if self.arrow_marker_absolute is not None:
            result["arrowMarkerAbsolute"] = from_union(
                [from_bool, from_none], self.arrow_marker_absolute
            )
        if self.diagram_padding is not None:
            result["diagramPadding"] = from_union([from_int, from_none], self.diagram_padding)
        if self.divider_margin is not None:
            result["dividerMargin"] = from_union([to_float, from_none], self.divider_margin)
        if self.hide_empty_members_box is not None:
            result["hideEmptyMembersBox"] = from_union(
                [from_bool, from_none], self.hide_empty_members_box
            )
        if self.hierarchical_namespaces is not None:
            result["hierarchicalNamespaces"] = from_union(
                [from_bool, from_none], self.hierarchical_namespaces
            )
        if self.html_labels is not None:
            result["htmlLabels"] = from_union([from_bool, from_none], self.html_labels)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.node_spacing is not None:
            result["nodeSpacing"] = from_union([from_int, from_none], self.node_spacing)
        if self.padding is not None:
            result["padding"] = from_union([to_float, from_none], self.padding)
        if self.rank_spacing is not None:
            result["rankSpacing"] = from_union([from_int, from_none], self.rank_spacing)
        if self.text_height is not None:
            result["textHeight"] = from_union([to_float, from_none], self.text_height)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


@dataclass
class MindmapDiagramConfig(DataModelHelper):
    """The object containing configurations specific for mindmap diagrams"""

    layout_algorithm: str
    """Layout algorithm to use for positioning mindmap nodes"""

    max_node_width: float
    padding: float
    use_max_width: bool
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "MindmapDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        layout_algorithm = from_str(obj.get("layoutAlgorithm"))
        max_node_width = from_float(obj.get("maxNodeWidth"))
        padding = from_float(obj.get("padding"))
        use_max_width = from_bool(obj.get("useMaxWidth"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        look = from_union([Look, from_none], obj.get("look"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return MindmapDiagramConfig(
            layout_algorithm, max_node_width, padding, use_max_width, layout, look, theme, use_width
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["layoutAlgorithm"] = from_str(self.layout_algorithm)
        result["maxNodeWidth"] = to_float(self.max_node_width)
        result["padding"] = to_float(self.padding)
        result["useMaxWidth"] = from_bool(self.use_max_width)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


class BitOrder(Enum):
    """The direction each row is numbered in. `descending` mirrors every row so it reads from
    that row's highest bit on the left down to its lowest bit on the right, the convention
    used for hardware registers. Fields are still declared lowest bit first, and keep their
    width.
    """

    ASCENDING = "ascending"
    DESCENDING = "descending"


@dataclass
class PacketDiagramConfig(DataModelHelper):
    """The object containing configurations specific for packet diagrams."""

    bit_order: Optional[BitOrder] = None
    """The direction each row is numbered in. `descending` mirrors every row so it reads from
    that row's highest bit on the left down to its lowest bit on the right, the convention
    used for hardware registers. Fields are still declared lowest bit first, and keep their
    width.
    """
    bits_per_row: Optional[float] = None
    """The number of bits to display per row."""

    bit_width: Optional[float] = None
    """The width of each bit in the packet diagram."""

    padding_x: Optional[float] = None
    """The horizontal padding between the blocks in a row."""

    padding_y: Optional[float] = None
    """The vertical padding between the rows."""

    row_height: Optional[float] = None
    """The height of each row in the packet diagram."""

    show_bits: Optional[bool] = None
    """Toggle to display or hide bit numbers."""

    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_max_width: Optional[bool] = None
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "PacketDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        bit_order = from_union([BitOrder, from_none], obj.get("bitOrder"))
        bits_per_row = from_union([from_float, from_none], obj.get("bitsPerRow"))
        bit_width = from_union([from_float, from_none], obj.get("bitWidth"))
        padding_x = from_union([from_float, from_none], obj.get("paddingX"))
        padding_y = from_union([from_float, from_none], obj.get("paddingY"))
        row_height = from_union([from_float, from_none], obj.get("rowHeight"))
        show_bits = from_union([from_bool, from_none], obj.get("showBits"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        look = from_union([Look, from_none], obj.get("look"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_max_width = from_union([from_bool, from_none], obj.get("useMaxWidth"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return PacketDiagramConfig(
            bit_order,
            bits_per_row,
            bit_width,
            padding_x,
            padding_y,
            row_height,
            show_bits,
            layout,
            look,
            theme,
            use_max_width,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.bit_order is not None:
            result["bitOrder"] = from_union(
                [lambda x: to_enum(BitOrder, x), from_none], self.bit_order
            )
        if self.bits_per_row is not None:
            result["bitsPerRow"] = from_union([to_float, from_none], self.bits_per_row)
        if self.bit_width is not None:
            result["bitWidth"] = from_union([to_float, from_none], self.bit_width)
        if self.padding_x is not None:
            result["paddingX"] = from_union([to_float, from_none], self.padding_x)
        if self.padding_y is not None:
            result["paddingY"] = from_union([to_float, from_none], self.padding_y)
        if self.row_height is not None:
            result["rowHeight"] = from_union([to_float, from_none], self.row_height)
        if self.show_bits is not None:
            result["showBits"] = from_union([from_bool, from_none], self.show_bits)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_max_width is not None:
            result["useMaxWidth"] = from_union([from_bool, from_none], self.use_max_width)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


class LegendPosition(Enum):
    """Legend's position relative to the chart. Default to right."""

    BOTTOM = "bottom"
    CENTER = "center"
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"


@dataclass
class PieDiagramConfig(DataModelHelper):
    donut_hole: Optional[float] = None
    """Donut hole ratio. Valid value are from 0 to 0.9. Default to 0."""

    highlight_slice: Optional[str] = None
    """Highlight specific slice with matching label. Set to 'hover' to highlight hovered slice."""

    legend_position: Optional[LegendPosition] = None
    """Legend's position relative to the chart. Default to right."""

    text_position: Optional[float] = None
    """Axial position of slice's label from zero at the center to 1 at the outside edges."""

    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_max_width: Optional[bool] = None
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "PieDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        donut_hole = from_union([from_float, from_none], obj.get("donutHole"))
        highlight_slice = from_union([from_str, from_none], obj.get("highlightSlice"))
        legend_position = from_union([LegendPosition, from_none], obj.get("legendPosition"))
        text_position = from_union([from_float, from_none], obj.get("textPosition"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        look = from_union([Look, from_none], obj.get("look"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_max_width = from_union([from_bool, from_none], obj.get("useMaxWidth"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return PieDiagramConfig(
            donut_hole,
            highlight_slice,
            legend_position,
            text_position,
            layout,
            look,
            theme,
            use_max_width,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.donut_hole is not None:
            result["donutHole"] = from_union([to_float, from_none], self.donut_hole)
        if self.highlight_slice is not None:
            result["highlightSlice"] = from_union([from_str, from_none], self.highlight_slice)
        if self.legend_position is not None:
            result["legendPosition"] = from_union(
                [lambda x: to_enum(LegendPosition, x), from_none], self.legend_position
            )
        if self.text_position is not None:
            result["textPosition"] = from_union([to_float, from_none], self.text_position)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_max_width is not None:
            result["useMaxWidth"] = from_union([from_bool, from_none], self.use_max_width)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


class XAxisPosition(Enum):
    """position of x-axis labels"""

    BOTTOM = "bottom"
    TOP = "top"


class YAxisPosition(Enum):
    """position of y-axis labels"""

    LEFT = "left"
    RIGHT = "right"


@dataclass
class QuadrantChartConfig(DataModelHelper):
    chart_height: float
    """Height of the chart"""

    chart_width: float
    """Width of the chart"""

    point_label_font_size: float
    """point title font size"""

    point_radius: float
    """radius of the point to be drawn"""

    point_text_padding: float
    """padding between point and point label"""

    quadrant_external_border_stroke_width: float
    """stroke width of edges of the box that are outside the quadrant"""

    quadrant_internal_border_stroke_width: float
    """stroke width of edges of the box that are inside the quadrant"""

    quadrant_label_font_size: float
    """quadrant title font size"""

    quadrant_padding: float
    """quadrant title padding from top if the quadrant is rendered on top"""

    quadrant_text_top_padding: float
    """quadrant title padding from top if the quadrant is rendered on top"""

    title_font_size: float
    """Chart title top and bottom padding"""

    title_padding: float
    """Padding around the quadrant square"""

    x_axis_label_font_size: float
    """x-axis label font size"""

    x_axis_label_padding: float
    """Padding around x-axis labels"""

    x_axis_position: XAxisPosition
    """position of x-axis labels"""

    y_axis_label_font_size: float
    """y-axis label font size"""

    y_axis_label_padding: float
    """Padding around y-axis labels"""

    y_axis_position: YAxisPosition
    """position of y-axis labels"""

    use_max_width: bool
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "QuadrantChartConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        chart_height = from_float(obj.get("chartHeight"))
        chart_width = from_float(obj.get("chartWidth"))
        point_label_font_size = from_float(obj.get("pointLabelFontSize"))
        point_radius = from_float(obj.get("pointRadius"))
        point_text_padding = from_float(obj.get("pointTextPadding"))
        quadrant_external_border_stroke_width = from_float(
            obj.get("quadrantExternalBorderStrokeWidth")
        )
        quadrant_internal_border_stroke_width = from_float(
            obj.get("quadrantInternalBorderStrokeWidth")
        )
        quadrant_label_font_size = from_float(obj.get("quadrantLabelFontSize"))
        quadrant_padding = from_float(obj.get("quadrantPadding"))
        quadrant_text_top_padding = from_float(obj.get("quadrantTextTopPadding"))
        title_font_size = from_float(obj.get("titleFontSize"))
        title_padding = from_float(obj.get("titlePadding"))
        x_axis_label_font_size = from_float(obj.get("xAxisLabelFontSize"))
        x_axis_label_padding = from_float(obj.get("xAxisLabelPadding"))
        x_axis_position = XAxisPosition(obj.get("xAxisPosition"))
        y_axis_label_font_size = from_float(obj.get("yAxisLabelFontSize"))
        y_axis_label_padding = from_float(obj.get("yAxisLabelPadding"))
        y_axis_position = YAxisPosition(obj.get("yAxisPosition"))
        use_max_width = from_bool(obj.get("useMaxWidth"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        look = from_union([Look, from_none], obj.get("look"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return QuadrantChartConfig(
            chart_height,
            chart_width,
            point_label_font_size,
            point_radius,
            point_text_padding,
            quadrant_external_border_stroke_width,
            quadrant_internal_border_stroke_width,
            quadrant_label_font_size,
            quadrant_padding,
            quadrant_text_top_padding,
            title_font_size,
            title_padding,
            x_axis_label_font_size,
            x_axis_label_padding,
            x_axis_position,
            y_axis_label_font_size,
            y_axis_label_padding,
            y_axis_position,
            use_max_width,
            layout,
            look,
            theme,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["chartHeight"] = to_float(self.chart_height)
        result["chartWidth"] = to_float(self.chart_width)
        result["pointLabelFontSize"] = to_float(self.point_label_font_size)
        result["pointRadius"] = to_float(self.point_radius)
        result["pointTextPadding"] = to_float(self.point_text_padding)
        result["quadrantExternalBorderStrokeWidth"] = to_float(
            self.quadrant_external_border_stroke_width
        )
        result["quadrantInternalBorderStrokeWidth"] = to_float(
            self.quadrant_internal_border_stroke_width
        )
        result["quadrantLabelFontSize"] = to_float(self.quadrant_label_font_size)
        result["quadrantPadding"] = to_float(self.quadrant_padding)
        result["quadrantTextTopPadding"] = to_float(self.quadrant_text_top_padding)
        result["titleFontSize"] = to_float(self.title_font_size)
        result["titlePadding"] = to_float(self.title_padding)
        result["xAxisLabelFontSize"] = to_float(self.x_axis_label_font_size)
        result["xAxisLabelPadding"] = to_float(self.x_axis_label_padding)
        result["xAxisPosition"] = to_enum(XAxisPosition, self.x_axis_position)
        result["yAxisLabelFontSize"] = to_float(self.y_axis_label_font_size)
        result["yAxisLabelPadding"] = to_float(self.y_axis_label_padding)
        result["yAxisPosition"] = to_enum(YAxisPosition, self.y_axis_position)
        result["useMaxWidth"] = from_bool(self.use_max_width)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


@dataclass
class RadarDiagramConfig(DataModelHelper):
    """The object containing configurations specific for radar diagrams."""

    axis_label_factor: Optional[float] = None
    """The scale factor of the axis label."""

    axis_scale_factor: Optional[float] = None
    """The scale factor of the axis."""

    curve_tension: Optional[float] = None
    """The tension factor for the Catmull-Rom spline conversion to cubic Bézier curves."""

    height: Optional[float] = None
    """The size of the radar diagram."""

    margin_bottom: Optional[float] = None
    """The margin from the bottom of the radar diagram."""

    margin_left: Optional[float] = None
    """The margin from the left of the radar diagram."""

    margin_right: Optional[float] = None
    """The margin from the right of the radar diagram."""

    margin_top: Optional[float] = None
    """The margin from the top of the radar diagram."""

    width: Optional[float] = None
    """The size of the radar diagram."""

    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_max_width: Optional[bool] = None
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "RadarDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        axis_label_factor = from_union([from_float, from_none], obj.get("axisLabelFactor"))
        axis_scale_factor = from_union([from_float, from_none], obj.get("axisScaleFactor"))
        curve_tension = from_union([from_float, from_none], obj.get("curveTension"))
        height = from_union([from_float, from_none], obj.get("height"))
        margin_bottom = from_union([from_float, from_none], obj.get("marginBottom"))
        margin_left = from_union([from_float, from_none], obj.get("marginLeft"))
        margin_right = from_union([from_float, from_none], obj.get("marginRight"))
        margin_top = from_union([from_float, from_none], obj.get("marginTop"))
        width = from_union([from_float, from_none], obj.get("width"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        look = from_union([Look, from_none], obj.get("look"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_max_width = from_union([from_bool, from_none], obj.get("useMaxWidth"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return RadarDiagramConfig(
            axis_label_factor,
            axis_scale_factor,
            curve_tension,
            height,
            margin_bottom,
            margin_left,
            margin_right,
            margin_top,
            width,
            layout,
            look,
            theme,
            use_max_width,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.axis_label_factor is not None:
            result["axisLabelFactor"] = from_union([to_float, from_none], self.axis_label_factor)
        if self.axis_scale_factor is not None:
            result["axisScaleFactor"] = from_union([to_float, from_none], self.axis_scale_factor)
        if self.curve_tension is not None:
            result["curveTension"] = from_union([to_float, from_none], self.curve_tension)
        if self.height is not None:
            result["height"] = from_union([to_float, from_none], self.height)
        if self.margin_bottom is not None:
            result["marginBottom"] = from_union([to_float, from_none], self.margin_bottom)
        if self.margin_left is not None:
            result["marginLeft"] = from_union([to_float, from_none], self.margin_left)
        if self.margin_right is not None:
            result["marginRight"] = from_union([to_float, from_none], self.margin_right)
        if self.margin_top is not None:
            result["marginTop"] = from_union([to_float, from_none], self.margin_top)
        if self.width is not None:
            result["width"] = from_union([to_float, from_none], self.width)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_max_width is not None:
            result["useMaxWidth"] = from_union([from_bool, from_none], self.use_max_width)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


@dataclass
class RailroadDiagramConfig(DataModelHelper):
    """Configuration for Railroad (Syntax) Diagrams"""

    arc_radius: Optional[float] = None
    """Radius for curved paths"""

    comment_fill: Optional[str] = None
    """Fill color for comments"""

    comment_stroke: Optional[str] = None
    """Stroke color for comments"""

    comment_text_color: Optional[str] = None
    """Text color for comments"""

    compact_mode: Optional[bool] = None
    """Use compact layout mode"""

    font_family: Optional[str] = None
    """Font family for text"""

    font_size: Optional[float] = None
    """Font size for text"""

    horizontal_separation: Optional[float] = None
    """Horizontal separation between elements"""

    line_color: Optional[str] = None
    """Color for connection lines"""

    marker_fill: Optional[str] = None
    """Fill color for start/end markers"""

    marker_radius: Optional[float] = None
    """Radius of start/end markers"""

    non_terminal_fill: Optional[str] = None
    """Fill color for non-terminal elements"""

    non_terminal_stroke: Optional[str] = None
    """Stroke color for non-terminal elements"""

    non_terminal_text_color: Optional[str] = None
    """Text color for non-terminal elements"""

    padding: Optional[float] = None
    """Padding around elements"""

    rule_name_color: Optional[str] = None
    """Color for rule names"""

    show_markers: Optional[bool] = None
    """Show start/end markers"""

    special_fill: Optional[str] = None
    """Fill color for special sequences"""

    special_stroke: Optional[str] = None
    """Stroke color for special sequences"""

    stroke_width: Optional[float] = None
    """Width of strokes"""

    terminal_fill: Optional[str] = None
    """Fill color for terminal elements"""

    terminal_stroke: Optional[str] = None
    """Stroke color for terminal elements"""

    terminal_text_color: Optional[str] = None
    """Text color for terminal elements"""

    vertical_separation: Optional[float] = None
    """Vertical separation between elements"""

    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_max_width: Optional[bool] = None
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "RailroadDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        arc_radius = from_union([from_float, from_none], obj.get("arcRadius"))
        comment_fill = from_union([from_str, from_none], obj.get("commentFill"))
        comment_stroke = from_union([from_str, from_none], obj.get("commentStroke"))
        comment_text_color = from_union([from_str, from_none], obj.get("commentTextColor"))
        compact_mode = from_union([from_bool, from_none], obj.get("compactMode"))
        font_family = from_union([from_str, from_none], obj.get("fontFamily"))
        font_size = from_union([from_float, from_none], obj.get("fontSize"))
        horizontal_separation = from_union([from_float, from_none], obj.get("horizontalSeparation"))
        line_color = from_union([from_str, from_none], obj.get("lineColor"))
        marker_fill = from_union([from_str, from_none], obj.get("markerFill"))
        marker_radius = from_union([from_float, from_none], obj.get("markerRadius"))
        non_terminal_fill = from_union([from_str, from_none], obj.get("nonTerminalFill"))
        non_terminal_stroke = from_union([from_str, from_none], obj.get("nonTerminalStroke"))
        non_terminal_text_color = from_union([from_str, from_none], obj.get("nonTerminalTextColor"))
        padding = from_union([from_float, from_none], obj.get("padding"))
        rule_name_color = from_union([from_str, from_none], obj.get("ruleNameColor"))
        show_markers = from_union([from_bool, from_none], obj.get("showMarkers"))
        special_fill = from_union([from_str, from_none], obj.get("specialFill"))
        special_stroke = from_union([from_str, from_none], obj.get("specialStroke"))
        stroke_width = from_union([from_float, from_none], obj.get("strokeWidth"))
        terminal_fill = from_union([from_str, from_none], obj.get("terminalFill"))
        terminal_stroke = from_union([from_str, from_none], obj.get("terminalStroke"))
        terminal_text_color = from_union([from_str, from_none], obj.get("terminalTextColor"))
        vertical_separation = from_union([from_float, from_none], obj.get("verticalSeparation"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        look = from_union([Look, from_none], obj.get("look"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_max_width = from_union([from_bool, from_none], obj.get("useMaxWidth"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return RailroadDiagramConfig(
            arc_radius,
            comment_fill,
            comment_stroke,
            comment_text_color,
            compact_mode,
            font_family,
            font_size,
            horizontal_separation,
            line_color,
            marker_fill,
            marker_radius,
            non_terminal_fill,
            non_terminal_stroke,
            non_terminal_text_color,
            padding,
            rule_name_color,
            show_markers,
            special_fill,
            special_stroke,
            stroke_width,
            terminal_fill,
            terminal_stroke,
            terminal_text_color,
            vertical_separation,
            layout,
            look,
            theme,
            use_max_width,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.arc_radius is not None:
            result["arcRadius"] = from_union([to_float, from_none], self.arc_radius)
        if self.comment_fill is not None:
            result["commentFill"] = from_union([from_str, from_none], self.comment_fill)
        if self.comment_stroke is not None:
            result["commentStroke"] = from_union([from_str, from_none], self.comment_stroke)
        if self.comment_text_color is not None:
            result["commentTextColor"] = from_union([from_str, from_none], self.comment_text_color)
        if self.compact_mode is not None:
            result["compactMode"] = from_union([from_bool, from_none], self.compact_mode)
        if self.font_family is not None:
            result["fontFamily"] = from_union([from_str, from_none], self.font_family)
        if self.font_size is not None:
            result["fontSize"] = from_union([to_float, from_none], self.font_size)
        if self.horizontal_separation is not None:
            result["horizontalSeparation"] = from_union(
                [to_float, from_none], self.horizontal_separation
            )
        if self.line_color is not None:
            result["lineColor"] = from_union([from_str, from_none], self.line_color)
        if self.marker_fill is not None:
            result["markerFill"] = from_union([from_str, from_none], self.marker_fill)
        if self.marker_radius is not None:
            result["markerRadius"] = from_union([to_float, from_none], self.marker_radius)
        if self.non_terminal_fill is not None:
            result["nonTerminalFill"] = from_union([from_str, from_none], self.non_terminal_fill)
        if self.non_terminal_stroke is not None:
            result["nonTerminalStroke"] = from_union(
                [from_str, from_none], self.non_terminal_stroke
            )
        if self.non_terminal_text_color is not None:
            result["nonTerminalTextColor"] = from_union(
                [from_str, from_none], self.non_terminal_text_color
            )
        if self.padding is not None:
            result["padding"] = from_union([to_float, from_none], self.padding)
        if self.rule_name_color is not None:
            result["ruleNameColor"] = from_union([from_str, from_none], self.rule_name_color)
        if self.show_markers is not None:
            result["showMarkers"] = from_union([from_bool, from_none], self.show_markers)
        if self.special_fill is not None:
            result["specialFill"] = from_union([from_str, from_none], self.special_fill)
        if self.special_stroke is not None:
            result["specialStroke"] = from_union([from_str, from_none], self.special_stroke)
        if self.stroke_width is not None:
            result["strokeWidth"] = from_union([to_float, from_none], self.stroke_width)
        if self.terminal_fill is not None:
            result["terminalFill"] = from_union([from_str, from_none], self.terminal_fill)
        if self.terminal_stroke is not None:
            result["terminalStroke"] = from_union([from_str, from_none], self.terminal_stroke)
        if self.terminal_text_color is not None:
            result["terminalTextColor"] = from_union(
                [from_str, from_none], self.terminal_text_color
            )
        if self.vertical_separation is not None:
            result["verticalSeparation"] = from_union(
                [to_float, from_none], self.vertical_separation
            )
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_max_width is not None:
            result["useMaxWidth"] = from_union([from_bool, from_none], self.use_max_width)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


@dataclass
class RequirementDiagramConfig(DataModelHelper):
    """The object containing configurations specific for req diagrams"""

    use_max_width: bool
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    font_size: Optional[float] = None
    line_height: Optional[float] = None
    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    rect_border_color: Optional[str] = None
    rect_border_size: Optional[str] = None
    rect_fill: Optional[str] = None
    rect_min_height: Optional[float] = None
    rect_min_width: Optional[float] = None
    rect_padding: Optional[float] = None
    text_color: Optional[str] = None
    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "RequirementDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        use_max_width = from_bool(obj.get("useMaxWidth"))
        font_size = from_union([from_float, from_none], obj.get("fontSize"))
        line_height = from_union([from_float, from_none], obj.get("line_height"))
        look = from_union([Look, from_none], obj.get("look"))
        rect_border_color = from_union([from_str, from_none], obj.get("rect_border_color"))
        rect_border_size = from_union([from_str, from_none], obj.get("rect_border_size"))
        rect_fill = from_union([from_str, from_none], obj.get("rect_fill"))
        rect_min_height = from_union([from_float, from_none], obj.get("rect_min_height"))
        rect_min_width = from_union([from_float, from_none], obj.get("rect_min_width"))
        rect_padding = from_union([from_float, from_none], obj.get("rect_padding"))
        text_color = from_union([from_str, from_none], obj.get("text_color"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return RequirementDiagramConfig(
            use_max_width,
            font_size,
            line_height,
            look,
            rect_border_color,
            rect_border_size,
            rect_fill,
            rect_min_height,
            rect_min_width,
            rect_padding,
            text_color,
            theme,
            layout,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["useMaxWidth"] = from_bool(self.use_max_width)
        if self.font_size is not None:
            result["fontSize"] = from_union([to_float, from_none], self.font_size)
        if self.line_height is not None:
            result["line_height"] = from_union([to_float, from_none], self.line_height)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.rect_border_color is not None:
            result["rect_border_color"] = from_union([from_str, from_none], self.rect_border_color)
        if self.rect_border_size is not None:
            result["rect_border_size"] = from_union([from_str, from_none], self.rect_border_size)
        if self.rect_fill is not None:
            result["rect_fill"] = from_union([from_str, from_none], self.rect_fill)
        if self.rect_min_height is not None:
            result["rect_min_height"] = from_union([to_float, from_none], self.rect_min_height)
        if self.rect_min_width is not None:
            result["rect_min_width"] = from_union([to_float, from_none], self.rect_min_width)
        if self.rect_padding is not None:
            result["rect_padding"] = from_union([to_float, from_none], self.rect_padding)
        if self.text_color is not None:
            result["text_color"] = from_union([from_str, from_none], self.text_color)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


class LabelStyle(Enum):
    """The style of labels in the sankey diagram. 'outlined' provides better readability with a
    white stroke behind the text.


    The style of labels in the sankey diagram.
    """

    LEGACY = "legacy"
    OUTLINED = "outlined"


class NodeAlignment(Enum):
    """Controls the alignment of the Sankey diagrams.

    See <https://github.com/d3/d3-sankey#alignments>.
    """

    CENTER = "center"
    JUSTIFY = "justify"
    LEFT = "left"
    RIGHT = "right"


@dataclass
class SankeyDiagramConfig(DataModelHelper):
    """The object containing configurations specific for sankey diagrams."""

    height: Optional[float] = None
    label_style: Optional[LabelStyle] = None
    """The style of labels in the sankey diagram. 'outlined' provides better readability with a
    white stroke behind the text.
    """
    link_color: Optional[str] = None
    """The color of the links in the sankey diagram."""

    node_alignment: Optional[NodeAlignment] = None
    node_colors: Optional[Dict[str, str]] = None
    """A mapping of node IDs to their colors. Nodes not specified will use the default color
    scheme.
    """
    node_padding: Optional[float] = None
    """The padding between nodes in the sankey diagram."""

    node_width: Optional[float] = None
    """The width of the nodes in the sankey diagram."""

    prefix: Optional[str] = None
    """The prefix to use for values"""

    show_values: Optional[bool] = None
    """Toggle to display or hide values along with title."""

    suffix: Optional[str] = None
    """The suffix to use for values"""

    use_max_width: Optional[bool] = None
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    width: Optional[float] = None
    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "SankeyDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        height = from_union([from_float, from_none], obj.get("height"))
        label_style = from_union([LabelStyle, from_none], obj.get("labelStyle"))
        link_color = from_union([from_str, from_none], obj.get("linkColor"))
        node_alignment = from_union([NodeAlignment, from_none], obj.get("nodeAlignment"))
        node_colors = from_union(
            [lambda x: from_dict(from_str, x), from_none], obj.get("nodeColors")
        )
        node_padding = from_union([from_float, from_none], obj.get("nodePadding"))
        node_width = from_union([from_float, from_none], obj.get("nodeWidth"))
        prefix = from_union([from_str, from_none], obj.get("prefix"))
        show_values = from_union([from_bool, from_none], obj.get("showValues"))
        suffix = from_union([from_str, from_none], obj.get("suffix"))
        use_max_width = from_union([from_bool, from_none], obj.get("useMaxWidth"))
        width = from_union([from_float, from_none], obj.get("width"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        look = from_union([Look, from_none], obj.get("look"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return SankeyDiagramConfig(
            height,
            label_style,
            link_color,
            node_alignment,
            node_colors,
            node_padding,
            node_width,
            prefix,
            show_values,
            suffix,
            use_max_width,
            width,
            layout,
            look,
            theme,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.height is not None:
            result["height"] = from_union([to_float, from_none], self.height)
        if self.label_style is not None:
            result["labelStyle"] = from_union(
                [lambda x: to_enum(LabelStyle, x), from_none], self.label_style
            )
        if self.link_color is not None:
            result["linkColor"] = from_union([from_str, from_none], self.link_color)
        if self.node_alignment is not None:
            result["nodeAlignment"] = from_union(
                [lambda x: to_enum(NodeAlignment, x), from_none], self.node_alignment
            )
        if self.node_colors is not None:
            result["nodeColors"] = from_union(
                [lambda x: from_dict(from_str, x), from_none], self.node_colors
            )
        if self.node_padding is not None:
            result["nodePadding"] = from_union([to_float, from_none], self.node_padding)
        if self.node_width is not None:
            result["nodeWidth"] = from_union([to_float, from_none], self.node_width)
        if self.prefix is not None:
            result["prefix"] = from_union([from_str, from_none], self.prefix)
        if self.show_values is not None:
            result["showValues"] = from_union([from_bool, from_none], self.show_values)
        if self.suffix is not None:
            result["suffix"] = from_union([from_str, from_none], self.suffix)
        if self.use_max_width is not None:
            result["useMaxWidth"] = from_union([from_bool, from_none], self.use_max_width)
        if self.width is not None:
            result["width"] = from_union([to_float, from_none], self.width)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


class SecurityLevel(Enum):
    """Level of trust for parsed diagram"""

    ANTISCRIPT = "antiscript"
    LOOSE = "loose"
    SANDBOX = "sandbox"
    STRICT = "strict"


@dataclass
class SequenceDiagramConfig(DataModelHelper):
    """The object containing configurations specific for sequence diagrams"""

    activation_width: int
    """Width of the activation rect"""

    actor_font_family: str
    """This sets the font family of the actor's description"""

    actor_font_size: Union[float, str]
    """This sets the font size of the actor's description"""

    actor_font_weight: Union[float, str]
    """This sets the font weight of the actor's description"""

    actor_margin: int
    """Margin between actors"""

    bottom_margin_adj: int
    box_margin: int
    box_text_margin: int
    diagram_margin_x: int
    """Margin to the right and left of the sequence diagram"""

    diagram_margin_y: int
    """Margin to the over and under the sequence diagram"""

    force_menus: bool
    """forces actor popup menus to always be visible (to support E2E testing)."""

    height: int
    message_align: EAlign
    message_font_family: str
    """This sets the font family of actor messages"""

    message_font_size: Union[float, str]
    """This sets the font size of actor messages"""

    message_font_weight: Union[float, str]
    """This sets the font weight of actor messages"""

    message_margin: int
    mirror_actors: bool
    """Mirror actors under diagram"""

    note_align: EAlign
    """This sets the text alignment of actor-attached notes"""

    note_font_family: str
    """This sets the font family of actor-attached notes"""

    note_font_size: Union[float, str]
    """This sets the font size of actor-attached notes"""

    note_font_weight: Union[float, str]
    """This sets the font weight of actor-attached notes"""

    note_margin: int
    right_angles: bool
    show_sequence_numbers: bool
    """This will show the node numbers"""

    width: int
    use_max_width: bool
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    actor_font: Any
    arrow_marker_absolute: Optional[bool] = None
    hide_unused_participants: Optional[bool] = None
    label_box_height: Optional[float] = None
    """This sets the height of the loop-box (loop, alt, opt, par)"""

    label_box_width: Optional[float] = None
    """This sets the width of the loop-box (loop, alt, opt, par)"""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    message_font: Any = None
    note_font: Any = None
    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    wrap: Optional[bool] = None
    """This sets the auto-wrap state for the diagram"""

    wrap_padding: Optional[float] = None
    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "SequenceDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        activation_width = from_int(obj.get("activationWidth"))
        actor_font_family = from_str(obj.get("actorFontFamily"))
        actor_font_size = from_union([from_float, from_str], obj.get("actorFontSize"))
        actor_font_weight = from_union([from_float, from_str], obj.get("actorFontWeight"))
        actor_margin = from_int(obj.get("actorMargin"))
        bottom_margin_adj = from_int(obj.get("bottomMarginAdj"))
        box_margin = from_int(obj.get("boxMargin"))
        box_text_margin = from_int(obj.get("boxTextMargin"))
        diagram_margin_x = from_int(obj.get("diagramMarginX"))
        diagram_margin_y = from_int(obj.get("diagramMarginY"))
        force_menus = from_bool(obj.get("forceMenus"))
        height = from_int(obj.get("height"))
        message_align = EAlign(obj.get("messageAlign"))
        message_font_family = from_str(obj.get("messageFontFamily"))
        message_font_size = from_union([from_float, from_str], obj.get("messageFontSize"))
        message_font_weight = from_union([from_float, from_str], obj.get("messageFontWeight"))
        message_margin = from_int(obj.get("messageMargin"))
        mirror_actors = from_bool(obj.get("mirrorActors"))
        note_align = EAlign(obj.get("noteAlign"))
        note_font_family = from_str(obj.get("noteFontFamily"))
        note_font_size = from_union([from_float, from_str], obj.get("noteFontSize"))
        note_font_weight = from_union([from_float, from_str], obj.get("noteFontWeight"))
        note_margin = from_int(obj.get("noteMargin"))
        right_angles = from_bool(obj.get("rightAngles"))
        show_sequence_numbers = from_bool(obj.get("showSequenceNumbers"))
        width = from_int(obj.get("width"))
        use_max_width = from_bool(obj.get("useMaxWidth"))
        actor_font = obj.get("actorFont")
        arrow_marker_absolute = from_union([from_bool, from_none], obj.get("arrowMarkerAbsolute"))
        hide_unused_participants = from_union(
            [from_bool, from_none], obj.get("hideUnusedParticipants")
        )
        label_box_height = from_union([from_float, from_none], obj.get("labelBoxHeight"))
        label_box_width = from_union([from_float, from_none], obj.get("labelBoxWidth"))
        look = from_union([Look, from_none], obj.get("look"))
        message_font = obj.get("messageFont")
        note_font = obj.get("noteFont")
        theme = from_union([Theme, from_none], obj.get("theme"))
        wrap = from_union([from_bool, from_none], obj.get("wrap"))
        wrap_padding = from_union([from_float, from_none], obj.get("wrapPadding"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return SequenceDiagramConfig(
            activation_width,
            actor_font_family,
            actor_font_size,
            actor_font_weight,
            actor_margin,
            bottom_margin_adj,
            box_margin,
            box_text_margin,
            diagram_margin_x,
            diagram_margin_y,
            force_menus,
            height,
            message_align,
            message_font_family,
            message_font_size,
            message_font_weight,
            message_margin,
            mirror_actors,
            note_align,
            note_font_family,
            note_font_size,
            note_font_weight,
            note_margin,
            right_angles,
            show_sequence_numbers,
            width,
            use_max_width,
            actor_font,
            arrow_marker_absolute,
            hide_unused_participants,
            label_box_height,
            label_box_width,
            look,
            message_font,
            note_font,
            theme,
            wrap,
            wrap_padding,
            layout,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["activationWidth"] = from_int(self.activation_width)
        result["actorFontFamily"] = from_str(self.actor_font_family)
        result["actorFontSize"] = from_union([to_float, from_str], self.actor_font_size)
        result["actorFontWeight"] = from_union([to_float, from_str], self.actor_font_weight)
        result["actorMargin"] = from_int(self.actor_margin)
        result["bottomMarginAdj"] = from_int(self.bottom_margin_adj)
        result["boxMargin"] = from_int(self.box_margin)
        result["boxTextMargin"] = from_int(self.box_text_margin)
        result["diagramMarginX"] = from_int(self.diagram_margin_x)
        result["diagramMarginY"] = from_int(self.diagram_margin_y)
        result["forceMenus"] = from_bool(self.force_menus)
        result["height"] = from_int(self.height)
        result["messageAlign"] = to_enum(EAlign, self.message_align)
        result["messageFontFamily"] = from_str(self.message_font_family)
        result["messageFontSize"] = from_union([to_float, from_str], self.message_font_size)
        result["messageFontWeight"] = from_union([to_float, from_str], self.message_font_weight)
        result["messageMargin"] = from_int(self.message_margin)
        result["mirrorActors"] = from_bool(self.mirror_actors)
        result["noteAlign"] = to_enum(EAlign, self.note_align)
        result["noteFontFamily"] = from_str(self.note_font_family)
        result["noteFontSize"] = from_union([to_float, from_str], self.note_font_size)
        result["noteFontWeight"] = from_union([to_float, from_str], self.note_font_weight)
        result["noteMargin"] = from_int(self.note_margin)
        result["rightAngles"] = from_bool(self.right_angles)
        result["showSequenceNumbers"] = from_bool(self.show_sequence_numbers)
        result["width"] = from_int(self.width)
        result["useMaxWidth"] = from_bool(self.use_max_width)
        if self.actor_font is not None:
            result["actorFont"] = self.actor_font
        if self.arrow_marker_absolute is not None:
            result["arrowMarkerAbsolute"] = from_union(
                [from_bool, from_none], self.arrow_marker_absolute
            )
        if self.hide_unused_participants is not None:
            result["hideUnusedParticipants"] = from_union(
                [from_bool, from_none], self.hide_unused_participants
            )
        if self.label_box_height is not None:
            result["labelBoxHeight"] = from_union([to_float, from_none], self.label_box_height)
        if self.label_box_width is not None:
            result["labelBoxWidth"] = from_union([to_float, from_none], self.label_box_width)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.message_font is not None:
            result["messageFont"] = self.message_font
        if self.note_font is not None:
            result["noteFont"] = self.note_font
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.wrap is not None:
            result["wrap"] = from_union([from_bool, from_none], self.wrap)
        if self.wrap_padding is not None:
            result["wrapPadding"] = from_union([to_float, from_none], self.wrap_padding)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


@dataclass
class StateDiagramConfig(DataModelHelper):
    """The object containing configurations specific for entity relationship diagrams"""

    min_node_width: float
    """Minimum width of the label area of a node.
    
    Labels narrower than this are widened to it, so nodes with short text
    get a uniform width; the node's own padding is added on top, the same
    way it is for `wrappingWidth`. Nodes with an explicit width are not
    affected.
    """
    title_top_margin: int
    wrapping_width: float
    """Width of nodes where text is wrapped.
    
    When using markdown strings the text is wrapped automatically, this
    value sets the max width of a text before it continues on a new line.
    """
    use_max_width: bool
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    arrow_marker_absolute: Optional[bool] = None
    composit_title_size: Optional[float] = None
    divider_margin: Optional[float] = None
    edge_length_factor: Optional[str] = None
    font_size: Optional[float] = None
    font_size_factor: Optional[float] = None
    """Font size factor, this is used to guess the width of the edges labels
    before rendering by dagre layout.
    This might need updating if/when switching font
    """
    fork_height: Optional[float] = None
    fork_width: Optional[float] = None
    label_height: Optional[float] = None
    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    mini_padding: Optional[float] = None
    node_spacing: Optional[int] = None
    note_margin: Optional[float] = None
    padding: Optional[float] = None
    radius: Optional[float] = None
    rank_spacing: Optional[int] = None
    size_unit: Optional[float] = None
    text_height: Optional[float] = None
    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    title_shift: Optional[float] = None
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "StateDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        min_node_width = from_float(obj.get("minNodeWidth"))
        title_top_margin = from_int(obj.get("titleTopMargin"))
        wrapping_width = from_float(obj.get("wrappingWidth"))
        use_max_width = from_bool(obj.get("useMaxWidth"))
        arrow_marker_absolute = from_union([from_bool, from_none], obj.get("arrowMarkerAbsolute"))
        composit_title_size = from_union([from_float, from_none], obj.get("compositTitleSize"))
        divider_margin = from_union([from_float, from_none], obj.get("dividerMargin"))
        edge_length_factor = from_union([from_str, from_none], obj.get("edgeLengthFactor"))
        font_size = from_union([from_float, from_none], obj.get("fontSize"))
        font_size_factor = from_union([from_float, from_none], obj.get("fontSizeFactor"))
        fork_height = from_union([from_float, from_none], obj.get("forkHeight"))
        fork_width = from_union([from_float, from_none], obj.get("forkWidth"))
        label_height = from_union([from_float, from_none], obj.get("labelHeight"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        look = from_union([Look, from_none], obj.get("look"))
        mini_padding = from_union([from_float, from_none], obj.get("miniPadding"))
        node_spacing = from_union([from_int, from_none], obj.get("nodeSpacing"))
        note_margin = from_union([from_float, from_none], obj.get("noteMargin"))
        padding = from_union([from_float, from_none], obj.get("padding"))
        radius = from_union([from_float, from_none], obj.get("radius"))
        rank_spacing = from_union([from_int, from_none], obj.get("rankSpacing"))
        size_unit = from_union([from_float, from_none], obj.get("sizeUnit"))
        text_height = from_union([from_float, from_none], obj.get("textHeight"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        title_shift = from_union([from_float, from_none], obj.get("titleShift"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return StateDiagramConfig(
            min_node_width,
            title_top_margin,
            wrapping_width,
            use_max_width,
            arrow_marker_absolute,
            composit_title_size,
            divider_margin,
            edge_length_factor,
            font_size,
            font_size_factor,
            fork_height,
            fork_width,
            label_height,
            layout,
            look,
            mini_padding,
            node_spacing,
            note_margin,
            padding,
            radius,
            rank_spacing,
            size_unit,
            text_height,
            theme,
            title_shift,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["minNodeWidth"] = to_float(self.min_node_width)
        result["titleTopMargin"] = from_int(self.title_top_margin)
        result["wrappingWidth"] = to_float(self.wrapping_width)
        result["useMaxWidth"] = from_bool(self.use_max_width)
        if self.arrow_marker_absolute is not None:
            result["arrowMarkerAbsolute"] = from_union(
                [from_bool, from_none], self.arrow_marker_absolute
            )
        if self.composit_title_size is not None:
            result["compositTitleSize"] = from_union(
                [to_float, from_none], self.composit_title_size
            )
        if self.divider_margin is not None:
            result["dividerMargin"] = from_union([to_float, from_none], self.divider_margin)
        if self.edge_length_factor is not None:
            result["edgeLengthFactor"] = from_union([from_str, from_none], self.edge_length_factor)
        if self.font_size is not None:
            result["fontSize"] = from_union([to_float, from_none], self.font_size)
        if self.font_size_factor is not None:
            result["fontSizeFactor"] = from_union([to_float, from_none], self.font_size_factor)
        if self.fork_height is not None:
            result["forkHeight"] = from_union([to_float, from_none], self.fork_height)
        if self.fork_width is not None:
            result["forkWidth"] = from_union([to_float, from_none], self.fork_width)
        if self.label_height is not None:
            result["labelHeight"] = from_union([to_float, from_none], self.label_height)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.mini_padding is not None:
            result["miniPadding"] = from_union([to_float, from_none], self.mini_padding)
        if self.node_spacing is not None:
            result["nodeSpacing"] = from_union([from_int, from_none], self.node_spacing)
        if self.note_margin is not None:
            result["noteMargin"] = from_union([to_float, from_none], self.note_margin)
        if self.padding is not None:
            result["padding"] = from_union([to_float, from_none], self.padding)
        if self.radius is not None:
            result["radius"] = from_union([to_float, from_none], self.radius)
        if self.rank_spacing is not None:
            result["rankSpacing"] = from_union([from_int, from_none], self.rank_spacing)
        if self.size_unit is not None:
            result["sizeUnit"] = from_union([to_float, from_none], self.size_unit)
        if self.text_height is not None:
            result["textHeight"] = from_union([to_float, from_none], self.text_height)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.title_shift is not None:
            result["titleShift"] = from_union([to_float, from_none], self.title_shift)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


@dataclass
class SwimlaneDiagramConfig(DataModelHelper):
    """The object containing configurations specific for the swimlanes diagram type.

    Swimlanes reuses the flowchart renderer and flowchart config for shared
    options (curve, htmlLabels, spacing, …); this block holds the knobs that
    only affect the swimlanes layout pipeline.
    """

    automatic_lane_ordering: Optional[bool] = None
    """Automatically reorders top-level swimlanes with a deterministic
    weighted-linear-arrangement heuristic. Disabled by default because
    source swimlane order can carry semantic meaning.
    """
    ignore_cross_lane_edges: Optional[bool] = None
    """Ignores edges that cross swimlane boundaries during swimlane layer
    assignment. This can improve rank quality for diagrams with many
    cross-lane links.
    """
    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    line_hops: Optional[Union[bool, LineHopsEnum]] = None
    """Renders edge crossings as small arcs ("hops") or visible gaps so that
    overlapping edges are easier to read. Set to `false` to disable. Edges
    rendered as curves are skipped to avoid corrupting the geometry.
    """
    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    optimize_ranks_by_crossings: Optional[bool] = None
    """Enables a crossing-aware rank optimization pass for swimlane layouts."""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_max_width: Optional[bool] = None
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "SwimlaneDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        automatic_lane_ordering = from_union(
            [from_bool, from_none], obj.get("automaticLaneOrdering")
        )
        ignore_cross_lane_edges = from_union(
            [from_bool, from_none], obj.get("ignoreCrossLaneEdges")
        )
        layout = from_union([from_str, from_none], obj.get("layout"))
        line_hops = from_union([from_bool, LineHopsEnum, from_none], obj.get("lineHops"))
        look = from_union([Look, from_none], obj.get("look"))
        optimize_ranks_by_crossings = from_union(
            [from_bool, from_none], obj.get("optimizeRanksByCrossings")
        )
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_max_width = from_union([from_bool, from_none], obj.get("useMaxWidth"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return SwimlaneDiagramConfig(
            automatic_lane_ordering,
            ignore_cross_lane_edges,
            layout,
            line_hops,
            look,
            optimize_ranks_by_crossings,
            theme,
            use_max_width,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.automatic_lane_ordering is not None:
            result["automaticLaneOrdering"] = from_union(
                [from_bool, from_none], self.automatic_lane_ordering
            )
        if self.ignore_cross_lane_edges is not None:
            result["ignoreCrossLaneEdges"] = from_union(
                [from_bool, from_none], self.ignore_cross_lane_edges
            )
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.line_hops is not None:
            result["lineHops"] = from_union(
                [from_bool, lambda x: to_enum(LineHopsEnum, x), from_none], self.line_hops
            )
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.optimize_ranks_by_crossings is not None:
            result["optimizeRanksByCrossings"] = from_union(
                [from_bool, from_none], self.optimize_ranks_by_crossings
            )
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_max_width is not None:
            result["useMaxWidth"] = from_union([from_bool, from_none], self.use_max_width)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


@dataclass
class TimelineDiagramConfig(DataModelHelper):
    bottom_margin_adj: int
    """Prolongs the edge of the diagram downwards.
    
    Depending on css styling this might need adjustment.
    """
    box_margin: int
    """Margin around loop boxes"""

    box_text_margin: int
    """Margin around the text in loop/alt/opt boxes"""

    diagram_margin_x: int
    diagram_margin_y: int
    height: int
    """Height of actor boxes"""

    left_margin: int
    """Margin between actors"""

    message_align: EAlign
    """Multiline message alignment"""

    message_margin: int
    """Space between messages."""

    note_margin: int
    """Margin around notes"""

    width: int
    """Width of actor boxes"""

    use_max_width: bool
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    activation_width: Optional[float] = None
    """Width of activation box"""

    actor_colours: Optional[List[str]] = None
    disable_multicolor: Optional[bool] = None
    padding: Optional[float] = None
    right_angles: Optional[bool] = None
    """Curved Arrows become Right Angles
    
    This will display arrows that start and begin at the same node as
    right angles, rather than as curves.
    """
    section_colours: Optional[List[str]] = None
    section_fills: Optional[List[str]] = None
    task_font_family: Optional[str] = None
    task_font_size: Optional[Union[float, str]] = None
    task_margin: Optional[float] = None
    text_placement: Optional[str] = None
    """text placement as: tspan | fo | old only text as before"""

    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "TimelineDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        bottom_margin_adj = from_int(obj.get("bottomMarginAdj"))
        box_margin = from_int(obj.get("boxMargin"))
        box_text_margin = from_int(obj.get("boxTextMargin"))
        diagram_margin_x = from_int(obj.get("diagramMarginX"))
        diagram_margin_y = from_int(obj.get("diagramMarginY"))
        height = from_int(obj.get("height"))
        left_margin = from_int(obj.get("leftMargin"))
        message_align = EAlign(obj.get("messageAlign"))
        message_margin = from_int(obj.get("messageMargin"))
        note_margin = from_int(obj.get("noteMargin"))
        width = from_int(obj.get("width"))
        use_max_width = from_bool(obj.get("useMaxWidth"))
        activation_width = from_union([from_float, from_none], obj.get("activationWidth"))
        actor_colours = from_union(
            [lambda x: from_list(from_str, x), from_none], obj.get("actorColours")
        )
        disable_multicolor = from_union([from_bool, from_none], obj.get("disableMulticolor"))
        padding = from_union([from_float, from_none], obj.get("padding"))
        right_angles = from_union([from_bool, from_none], obj.get("rightAngles"))
        section_colours = from_union(
            [lambda x: from_list(from_str, x), from_none], obj.get("sectionColours")
        )
        section_fills = from_union(
            [lambda x: from_list(from_str, x), from_none], obj.get("sectionFills")
        )
        task_font_family = from_union([from_str, from_none], obj.get("taskFontFamily"))
        task_font_size = from_union([from_float, from_str, from_none], obj.get("taskFontSize"))
        task_margin = from_union([from_float, from_none], obj.get("taskMargin"))
        text_placement = from_union([from_str, from_none], obj.get("textPlacement"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        look = from_union([Look, from_none], obj.get("look"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return TimelineDiagramConfig(
            bottom_margin_adj,
            box_margin,
            box_text_margin,
            diagram_margin_x,
            diagram_margin_y,
            height,
            left_margin,
            message_align,
            message_margin,
            note_margin,
            width,
            use_max_width,
            activation_width,
            actor_colours,
            disable_multicolor,
            padding,
            right_angles,
            section_colours,
            section_fills,
            task_font_family,
            task_font_size,
            task_margin,
            text_placement,
            layout,
            look,
            theme,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["bottomMarginAdj"] = from_int(self.bottom_margin_adj)
        result["boxMargin"] = from_int(self.box_margin)
        result["boxTextMargin"] = from_int(self.box_text_margin)
        result["diagramMarginX"] = from_int(self.diagram_margin_x)
        result["diagramMarginY"] = from_int(self.diagram_margin_y)
        result["height"] = from_int(self.height)
        result["leftMargin"] = from_int(self.left_margin)
        result["messageAlign"] = to_enum(EAlign, self.message_align)
        result["messageMargin"] = from_int(self.message_margin)
        result["noteMargin"] = from_int(self.note_margin)
        result["width"] = from_int(self.width)
        result["useMaxWidth"] = from_bool(self.use_max_width)
        if self.activation_width is not None:
            result["activationWidth"] = from_union([to_float, from_none], self.activation_width)
        if self.actor_colours is not None:
            result["actorColours"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.actor_colours
            )
        if self.disable_multicolor is not None:
            result["disableMulticolor"] = from_union(
                [from_bool, from_none], self.disable_multicolor
            )
        if self.padding is not None:
            result["padding"] = from_union([to_float, from_none], self.padding)
        if self.right_angles is not None:
            result["rightAngles"] = from_union([from_bool, from_none], self.right_angles)
        if self.section_colours is not None:
            result["sectionColours"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.section_colours
            )
        if self.section_fills is not None:
            result["sectionFills"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.section_fills
            )
        if self.task_font_family is not None:
            result["taskFontFamily"] = from_union([from_str, from_none], self.task_font_family)
        if self.task_font_size is not None:
            result["taskFontSize"] = from_union(
                [to_float, from_str, from_none], self.task_font_size
            )
        if self.task_margin is not None:
            result["taskMargin"] = from_union([to_float, from_none], self.task_margin)
        if self.text_placement is not None:
            result["textPlacement"] = from_union([from_str, from_none], self.text_placement)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


@dataclass
class TreeViewDiagramConfig(DataModelHelper):
    """The object containing configurations specific for treeView diagrams."""

    default_icon_pack: Optional[str] = None
    """Name of a registered iconify pack used to resolve unprefixed icon
    references — `icon(name)` annotations and `filenameIcons`/
    `extensionIcons` values without a `pack:` prefix. The pack must be
    registered with `registerIconPacks`. When empty, unprefixed names
    resolve to the built-in file/folder icons.
    """
    extension_icons: Optional[Dict[str, str]] = None
    """File-extension → icon map used to pick a file's icon when
    `showIcons` is enabled, e.g.
    `{ ".ts": "material-icon-theme:typescript" }`. Keys are
    lowercase and may include or omit the leading dot.
    Values are resolved like `icon()` references: `pack:name` is used
    as-is, unprefixed names resolve via `defaultIconPack`, and `none`
    hides the icon for matching files.
    """
    filename_icons: Optional[Dict[str, str]] = None
    """Exact-filename → icon map used to pick a file's icon when
    `showIcons` is enabled, e.g.
    `{ "Dockerfile": "material-icon-theme:docker" }`.
    Values are resolved like `icon()` references: `pack:name` is used
    as-is, unprefixed names resolve via `defaultIconPack`, and `none`
    hides the icon for matching files.
    """
    line_thickness: Optional[float] = None
    """Thickness of the line"""

    padding_x: Optional[float] = None
    """Horizontal padding of label"""

    padding_y: Optional[float] = None
    """Vertical padding of label"""

    row_indent: Optional[float] = None
    """Horizontal distance between rows differing by one level"""

    show_icons: Optional[bool] = None
    """Whether to show the default file/folder icons next to labels.
    Explicit `icon()` annotations always render, regardless of this setting.
    """
    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_max_width: Optional[bool] = None
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "TreeViewDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        default_icon_pack = from_union([from_str, from_none], obj.get("defaultIconPack"))
        extension_icons = from_union(
            [lambda x: from_dict(from_str, x), from_none], obj.get("extensionIcons")
        )
        filename_icons = from_union(
            [lambda x: from_dict(from_str, x), from_none], obj.get("filenameIcons")
        )
        line_thickness = from_union([from_float, from_none], obj.get("lineThickness"))
        padding_x = from_union([from_float, from_none], obj.get("paddingX"))
        padding_y = from_union([from_float, from_none], obj.get("paddingY"))
        row_indent = from_union([from_float, from_none], obj.get("rowIndent"))
        show_icons = from_union([from_bool, from_none], obj.get("showIcons"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        look = from_union([Look, from_none], obj.get("look"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_max_width = from_union([from_bool, from_none], obj.get("useMaxWidth"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return TreeViewDiagramConfig(
            default_icon_pack,
            extension_icons,
            filename_icons,
            line_thickness,
            padding_x,
            padding_y,
            row_indent,
            show_icons,
            layout,
            look,
            theme,
            use_max_width,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.default_icon_pack is not None:
            result["defaultIconPack"] = from_union([from_str, from_none], self.default_icon_pack)
        if self.extension_icons is not None:
            result["extensionIcons"] = from_union(
                [lambda x: from_dict(from_str, x), from_none], self.extension_icons
            )
        if self.filename_icons is not None:
            result["filenameIcons"] = from_union(
                [lambda x: from_dict(from_str, x), from_none], self.filename_icons
            )
        if self.line_thickness is not None:
            result["lineThickness"] = from_union([to_float, from_none], self.line_thickness)
        if self.padding_x is not None:
            result["paddingX"] = from_union([to_float, from_none], self.padding_x)
        if self.padding_y is not None:
            result["paddingY"] = from_union([to_float, from_none], self.padding_y)
        if self.row_indent is not None:
            result["rowIndent"] = from_union([to_float, from_none], self.row_indent)
        if self.show_icons is not None:
            result["showIcons"] = from_union([from_bool, from_none], self.show_icons)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_max_width is not None:
            result["useMaxWidth"] = from_union([from_bool, from_none], self.use_max_width)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


class ColorScheme(Enum):
    """How a use case diagram takes its colours from the active theme.

    `role` (the default) gives every element of a kind one colour, read from the
    `usecaseActorBkg` / `usecaseActorBorder`, `usecaseBkg` / `usecaseBorder`, and
    `usecaseBoundaryBkg` / `usecaseBoundaryBorder` theme variables. Colour then says
    what an element *is*, and it is invariant under insertion, reordering, and
    renaming -- adding one use case in the middle does not recolour the ones after it,
    so diffs, documentation screenshots, and visual baselines stay stable.

    `rotate` instead gives each actor, use case, and system boundary its own slot from
    the theme's categorical palette (`borderColorArray` / `bkgColorArray`), the way ER
    entities and class boxes are coloured. Actors and use cases share one cycle, and
    system boundaries run a second one from zero, so a boundary is never forced to
    match an element inside it. Within the shared cycle the actors are numbered first
    and the use cases after them, each in declaration order -- an interleaved
    `actor A`, `usecase U`, `actor B` is therefore numbered A, B, U rather than
    A, U, B. This buys per-instance variety at the cost of the stability `role` has:
    inserting an element shifts the colour of every later element of its own kind, and
    inserting an actor shifts the use cases too. Only the colour themes
    (`redux-color`, `redux-dark-color`) carry a palette, so on every other theme the
    two settings render identically.

    `classDef` and `style` keep overriding both, whichever is set.
    """

    ROLE = "role"
    ROTATE = "rotate"


@dataclass
class UsecaseDiagramConfig(DataModelHelper):
    """The object containing configurations specific for usecase diagrams."""

    min_node_width: float
    wrapping_width: float
    use_max_width: bool
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    actor_font_family: Optional[str] = None
    """Font family for actor labels.
    
    Written verbatim into an inline CSS custom property, so the characters that could
    terminate a declaration or open a new one are excluded: `;`, `<`, `>`, `(`, `)`,
    `{`, `}`, and `\`. Quotes, commas, and spaces stay allowed for font stacks such as
    `"Open Sans", sans-serif`.
    """
    actor_font_size: Optional[float] = None
    """Font size for actor labels"""

    actor_font_weight: Optional[str] = None
    """Font weight for actor labels.
    
    Restricted to the CSS `font-weight` keywords and numeric weights, since this value
    is written verbatim into an inline CSS custom property.
    """
    color_scheme: Optional[ColorScheme] = None
    """How a use case diagram takes its colours from the active theme.
    
    `role` (the default) gives every element of a kind one colour, read from the
    `usecaseActorBkg` / `usecaseActorBorder`, `usecaseBkg` / `usecaseBorder`, and
    `usecaseBoundaryBkg` / `usecaseBoundaryBorder` theme variables. Colour then says
    what an element *is*, and it is invariant under insertion, reordering, and
    renaming -- adding one use case in the middle does not recolour the ones after it,
    so diffs, documentation screenshots, and visual baselines stay stable.
    
    `rotate` instead gives each actor, use case, and system boundary its own slot from
    the theme's categorical palette (`borderColorArray` / `bkgColorArray`), the way ER
    entities and class boxes are coloured. Actors and use cases share one cycle, and
    system boundaries run a second one from zero, so a boundary is never forced to
    match an element inside it. Within the shared cycle the actors are numbered first
    and the use cases after them, each in declaration order -- an interleaved
    `actor A`, `usecase U`, `actor B` is therefore numbered A, B, U rather than
    A, U, B. This buys per-instance variety at the cost of the stability `role` has:
    inserting an element shifts the colour of every later element of its own kind, and
    inserting an actor shifts the use cases too. Only the colour themes
    (`redux-color`, `redux-dark-color`) carry a palette, so on every other theme the
    two settings render identically.
    
    `classDef` and `style` keep overriding both, whichever is set.
    """
    diagram_padding: Optional[float] = None
    """Padding around the entire diagram"""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    node_spacing: Optional[float] = None
    """Spacing between nodes on the same level"""

    rank_spacing: Optional[float] = None
    """Spacing between nodes on different levels"""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    usecase_font_family: Optional[str] = None
    """Font family for usecase labels.
    
    Constrained the same way as `actorFontFamily`.
    """
    usecase_font_size: Optional[float] = None
    """Font size for usecase labels"""

    usecase_font_weight: Optional[str] = None
    """Font weight for usecase labels.
    
    Constrained the same way as `actorFontWeight`.
    """
    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "UsecaseDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        min_node_width = from_float(obj.get("minNodeWidth"))
        wrapping_width = from_float(obj.get("wrappingWidth"))
        use_max_width = from_bool(obj.get("useMaxWidth"))
        actor_font_family = from_union([from_str, from_none], obj.get("actorFontFamily"))
        actor_font_size = from_union([from_float, from_none], obj.get("actorFontSize"))
        actor_font_weight = from_union([from_str, from_none], obj.get("actorFontWeight"))
        color_scheme = from_union([ColorScheme, from_none], obj.get("colorScheme"))
        diagram_padding = from_union([from_float, from_none], obj.get("diagramPadding"))
        look = from_union([Look, from_none], obj.get("look"))
        node_spacing = from_union([from_float, from_none], obj.get("nodeSpacing"))
        rank_spacing = from_union([from_float, from_none], obj.get("rankSpacing"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        usecase_font_family = from_union([from_str, from_none], obj.get("usecaseFontFamily"))
        usecase_font_size = from_union([from_float, from_none], obj.get("usecaseFontSize"))
        usecase_font_weight = from_union([from_str, from_none], obj.get("usecaseFontWeight"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return UsecaseDiagramConfig(
            min_node_width,
            wrapping_width,
            use_max_width,
            actor_font_family,
            actor_font_size,
            actor_font_weight,
            color_scheme,
            diagram_padding,
            look,
            node_spacing,
            rank_spacing,
            theme,
            usecase_font_family,
            usecase_font_size,
            usecase_font_weight,
            layout,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["minNodeWidth"] = to_float(self.min_node_width)
        result["wrappingWidth"] = to_float(self.wrapping_width)
        result["useMaxWidth"] = from_bool(self.use_max_width)
        if self.actor_font_family is not None:
            result["actorFontFamily"] = from_union([from_str, from_none], self.actor_font_family)
        if self.actor_font_size is not None:
            result["actorFontSize"] = from_union([to_float, from_none], self.actor_font_size)
        if self.actor_font_weight is not None:
            result["actorFontWeight"] = from_union([from_str, from_none], self.actor_font_weight)
        if self.color_scheme is not None:
            result["colorScheme"] = from_union(
                [lambda x: to_enum(ColorScheme, x), from_none], self.color_scheme
            )
        if self.diagram_padding is not None:
            result["diagramPadding"] = from_union([to_float, from_none], self.diagram_padding)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.node_spacing is not None:
            result["nodeSpacing"] = from_union([to_float, from_none], self.node_spacing)
        if self.rank_spacing is not None:
            result["rankSpacing"] = from_union([to_float, from_none], self.rank_spacing)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.usecase_font_family is not None:
            result["usecaseFontFamily"] = from_union(
                [from_str, from_none], self.usecase_font_family
            )
        if self.usecase_font_size is not None:
            result["usecaseFontSize"] = from_union([to_float, from_none], self.usecase_font_size)
        if self.usecase_font_weight is not None:
            result["usecaseFontWeight"] = from_union(
                [from_str, from_none], self.usecase_font_weight
            )
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


@dataclass
class VennDiagramConfig(DataModelHelper):
    """The object containing configurations specific for Venn diagrams."""

    height: Optional[float] = None
    """The height of the Venn diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    padding: Optional[float] = None
    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_debug_layout: Optional[bool] = None
    width: Optional[float] = None
    """The width of the Venn diagram."""

    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    use_max_width: Optional[bool] = None
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "VennDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        height = from_union([from_float, from_none], obj.get("height"))
        look = from_union([Look, from_none], obj.get("look"))
        padding = from_union([from_float, from_none], obj.get("padding"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_debug_layout = from_union([from_bool, from_none], obj.get("useDebugLayout"))
        width = from_union([from_float, from_none], obj.get("width"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        use_max_width = from_union([from_bool, from_none], obj.get("useMaxWidth"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return VennDiagramConfig(
            height, look, padding, theme, use_debug_layout, width, layout, use_max_width, use_width
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.height is not None:
            result["height"] = from_union([to_float, from_none], self.height)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.padding is not None:
            result["padding"] = from_union([to_float, from_none], self.padding)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_debug_layout is not None:
            result["useDebugLayout"] = from_union([from_bool, from_none], self.use_debug_layout)
        if self.width is not None:
            result["width"] = from_union([to_float, from_none], self.width)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.use_max_width is not None:
            result["useMaxWidth"] = from_union([from_bool, from_none], self.use_max_width)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


@dataclass
class WardleyDiagramConfig(DataModelHelper):
    """The object containing configurations specific for Wardley Maps diagrams."""

    axis_font_size: float
    """The font size for axis labels."""

    height: float
    """The height of the Wardley diagram canvas."""

    label_font_size: float
    """The font size for component labels."""

    node_radius: float
    """The radius of component nodes."""

    padding: float
    """The padding around the Wardley diagram."""

    width: float
    """The width of the Wardley diagram canvas."""

    node_label_offset: Optional[float] = None
    """The offset distance for node labels."""

    show_grid: Optional[bool] = None
    """Whether to display a background grid."""

    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_max_width: Optional[bool] = None
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "WardleyDiagramConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        axis_font_size = from_float(obj.get("axisFontSize"))
        height = from_float(obj.get("height"))
        label_font_size = from_float(obj.get("labelFontSize"))
        node_radius = from_float(obj.get("nodeRadius"))
        padding = from_float(obj.get("padding"))
        width = from_float(obj.get("width"))
        node_label_offset = from_union([from_float, from_none], obj.get("nodeLabelOffset"))
        show_grid = from_union([from_bool, from_none], obj.get("showGrid"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        look = from_union([Look, from_none], obj.get("look"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_max_width = from_union([from_bool, from_none], obj.get("useMaxWidth"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return WardleyDiagramConfig(
            axis_font_size,
            height,
            label_font_size,
            node_radius,
            padding,
            width,
            node_label_offset,
            show_grid,
            layout,
            look,
            theme,
            use_max_width,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["axisFontSize"] = to_float(self.axis_font_size)
        result["height"] = to_float(self.height)
        result["labelFontSize"] = to_float(self.label_font_size)
        result["nodeRadius"] = to_float(self.node_radius)
        result["padding"] = to_float(self.padding)
        result["width"] = to_float(self.width)
        if self.node_label_offset is not None:
            result["nodeLabelOffset"] = from_union([to_float, from_none], self.node_label_offset)
        if self.show_grid is not None:
            result["showGrid"] = from_union([from_bool, from_none], self.show_grid)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_max_width is not None:
            result["useMaxWidth"] = from_union([from_bool, from_none], self.use_max_width)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


@dataclass
class XYChartAxisConfig(DataModelHelper):
    """This object contains configuration for XYChart axis config"""

    axis_line_width: float
    """Width of the axis line"""

    label_font_size: float
    """font size of the axis labels (tick text)"""

    label_padding: float
    """top and bottom space from axis label (tick text)"""

    label_rotation: float
    """Label rotation in degrees"""

    show_axis_line: bool
    """Show line across the axis"""

    show_label: bool
    """Should show the axis labels (tick text)"""

    show_tick: bool
    """Should show the axis tick lines"""

    show_title: bool
    """Should show the axis title"""

    tick_length: float
    """length of the axis tick lines"""

    tick_width: float
    """width of the axis tick lines"""

    title_font_size: float
    """font size of the axis title"""

    title_padding: float
    """top and bottom space from axis title"""

    @classmethod
    def from_dict(cls, obj: Any) -> "XYChartAxisConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        axis_line_width = from_float(obj.get("axisLineWidth"))
        label_font_size = from_float(obj.get("labelFontSize"))
        label_padding = from_float(obj.get("labelPadding"))
        label_rotation = from_float(obj.get("labelRotation"))
        show_axis_line = from_bool(obj.get("showAxisLine"))
        show_label = from_bool(obj.get("showLabel"))
        show_tick = from_bool(obj.get("showTick"))
        show_title = from_bool(obj.get("showTitle"))
        tick_length = from_float(obj.get("tickLength"))
        tick_width = from_float(obj.get("tickWidth"))
        title_font_size = from_float(obj.get("titleFontSize"))
        title_padding = from_float(obj.get("titlePadding"))
        return XYChartAxisConfig(
            axis_line_width,
            label_font_size,
            label_padding,
            label_rotation,
            show_axis_line,
            show_label,
            show_tick,
            show_title,
            tick_length,
            tick_width,
            title_font_size,
            title_padding,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["axisLineWidth"] = to_float(self.axis_line_width)
        result["labelFontSize"] = to_float(self.label_font_size)
        result["labelPadding"] = to_float(self.label_padding)
        result["labelRotation"] = to_float(self.label_rotation)
        result["showAxisLine"] = from_bool(self.show_axis_line)
        result["showLabel"] = from_bool(self.show_label)
        result["showTick"] = from_bool(self.show_tick)
        result["showTitle"] = from_bool(self.show_title)
        result["tickLength"] = to_float(self.tick_length)
        result["tickWidth"] = to_float(self.tick_width)
        result["titleFontSize"] = to_float(self.title_font_size)
        result["titlePadding"] = to_float(self.title_padding)
        return result


@dataclass
class XYChartConfig(DataModelHelper):
    """This object contains configuration specific to XYCharts"""

    chart_orientation: Any
    """How to plot will be drawn horizontal or vertical"""

    height: float
    """height of the chart"""

    plot_reserved_space_percent: float
    """Minimum percent of space plots of the chart will take"""

    show_title: bool
    """Should show the chart title"""

    title_font_size: float
    """Font size of the chart title"""

    title_padding: float
    """Top and bottom space from the chart title"""

    width: float
    """width of the chart"""

    x_axis: XYChartAxisConfig
    y_axis: XYChartAxisConfig
    legend_font_size: Optional[float] = None
    """Font size of the legend text"""

    legend_padding: Optional[float] = None
    """Padding around the legend"""

    show_data_label: Optional[bool] = None
    """Should show the value corresponding to the bar within the bar"""

    show_data_label_outside_bar: Optional[bool] = None
    """If showing data label then show it outside the bar"""

    show_legend: Optional[bool] = None
    """Should show a legend for named plots"""

    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram."""

    look: Optional[Look] = None
    """Defines which main look to use for the diagram."""

    theme: Optional[Theme] = None
    """Theme, the CSS style sheet.
    You may also use `themeCSS` to override this value.
    """
    use_max_width: Optional[bool] = None
    """When this flag is set to `true`, the height and width is set to 100%
    and is then scaled with the available space.
    If set to `false`, the absolute space required is used.
    """
    use_width: Optional[float] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "XYChartConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        chart_orientation = obj.get("chartOrientation")
        height = from_float(obj.get("height"))
        plot_reserved_space_percent = from_float(obj.get("plotReservedSpacePercent"))
        show_title = from_bool(obj.get("showTitle"))
        title_font_size = from_float(obj.get("titleFontSize"))
        title_padding = from_float(obj.get("titlePadding"))
        width = from_float(obj.get("width"))
        x_axis = XYChartAxisConfig.from_dict(obj.get("xAxis"))
        y_axis = XYChartAxisConfig.from_dict(obj.get("yAxis"))
        legend_font_size = from_union([from_float, from_none], obj.get("legendFontSize"))
        legend_padding = from_union([from_float, from_none], obj.get("legendPadding"))
        show_data_label = from_union([from_bool, from_none], obj.get("showDataLabel"))
        show_data_label_outside_bar = from_union(
            [from_bool, from_none], obj.get("showDataLabelOutsideBar")
        )
        show_legend = from_union([from_bool, from_none], obj.get("showLegend"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        look = from_union([Look, from_none], obj.get("look"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        use_max_width = from_union([from_bool, from_none], obj.get("useMaxWidth"))
        use_width = from_union([from_float, from_none], obj.get("useWidth"))
        return XYChartConfig(
            chart_orientation,
            height,
            plot_reserved_space_percent,
            show_title,
            title_font_size,
            title_padding,
            width,
            x_axis,
            y_axis,
            legend_font_size,
            legend_padding,
            show_data_label,
            show_data_label_outside_bar,
            show_legend,
            layout,
            look,
            theme,
            use_max_width,
            use_width,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["chartOrientation"] = self.chart_orientation
        result["height"] = to_float(self.height)
        result["plotReservedSpacePercent"] = to_float(self.plot_reserved_space_percent)
        result["showTitle"] = from_bool(self.show_title)
        result["titleFontSize"] = to_float(self.title_font_size)
        result["titlePadding"] = to_float(self.title_padding)
        result["width"] = to_float(self.width)
        result["xAxis"] = to_class(XYChartAxisConfig, self.x_axis)
        result["yAxis"] = to_class(XYChartAxisConfig, self.y_axis)
        if self.legend_font_size is not None:
            result["legendFontSize"] = from_union([to_float, from_none], self.legend_font_size)
        if self.legend_padding is not None:
            result["legendPadding"] = from_union([to_float, from_none], self.legend_padding)
        if self.show_data_label is not None:
            result["showDataLabel"] = from_union([from_bool, from_none], self.show_data_label)
        if self.show_data_label_outside_bar is not None:
            result["showDataLabelOutsideBar"] = from_union(
                [from_bool, from_none], self.show_data_label_outside_bar
            )
        if self.show_legend is not None:
            result["showLegend"] = from_union([from_bool, from_none], self.show_legend)
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.use_max_width is not None:
            result["useMaxWidth"] = from_union([from_bool, from_none], self.use_max_width)
        if self.use_width is not None:
            result["useWidth"] = from_union([to_float, from_none], self.use_width)
        return result


@dataclass
class MermaidConfig(DataModelHelper):
    """Optional. The Mermaid configuration object (local copy of the official schema, with
    `required` removed).
    """

    agentflow: Optional[AgentflowDiagramConfig] = None
    alt_font_family: Optional[str] = None
    architecture: Optional[ArchitectureDiagramConfig] = None
    arrow_marker_absolute: Optional[bool] = None
    """Controls whether or arrow markers in html code are absolute paths or anchors.
    This matters if you are using base tag settings.
    """
    block: Optional[BlockDiagramConfig] = None
    c4: Optional[C4DiagramConfig] = None
    mermaid_config_class: Optional[ClassDiagramConfig] = None
    cynefin: Optional[CynefinDiagramConfig] = None
    dark_mode: Optional[bool] = None
    deterministic_ids: Optional[bool] = None
    """This option controls if the generated ids of nodes in the SVG are
    generated randomly or based on a seed.
    If set to `false`, the IDs are generated based on the current date and
    thus are not deterministic. This is the default behavior.
    
    This matters if your files are checked into source control e.g. git and
    should not change unless content is changed.
    """
    deterministic_id_seed: Optional[str] = None
    """This option is the optional seed for deterministic ids.
    If set to `undefined` but deterministicIds is `true`, a simple number iterator is used.
    You can set this attribute to base the seed on a static string.
    """
    dompurify_config: Optional[Dict[str, Any]] = None
    """Configuration options to pass to the `dompurify` library."""

    elk: Optional[Elk] = None
    er: Optional[ErDiagramConfig] = None
    eventmodeling: Optional[EventModelingDiagramConfig] = None
    flowchart: Optional[FlowchartDiagramConfig] = None
    font_family: Optional[str] = None
    """Specifies the font to be used in the rendered diagrams.
    Can be any possible CSS `font-family`.
    See https://developer.mozilla.org/en-US/docs/Web/CSS/font-family
    """
    font_size: Optional[float] = None
    force_legacy_math_ml: Optional[bool] = None
    """This option forces Mermaid to rely on KaTeX's own stylesheet for rendering MathML. Due to
    differences between OS
    fonts and browser's MathML implementation, this option is recommended if consistent
    rendering is important.
    If set to true, ignores legacyMathML.
    """
    gantt: Optional[GanttDiagramConfig] = None
    git_graph: Optional[GitGraphDiagramConfig] = None
    hand_drawn_seed: Optional[float] = None
    """Defines the seed to be used when using handDrawn look. This is important for the
    automated tests as they will always find differences without the seed. The default value
    is 0 which gives a random seed.
    """
    html_labels: Optional[bool] = None
    """Flag for setting whether or not a html tag should be used for rendering labels on nodes
    and edges.
    **Note:** Diagram-specific `htmlLabels` settings (e.g., `flowchart.htmlLabels`) are
    deprecated.
    Use this root-level `htmlLabels` setting instead. The root-level `htmlLabels` takes
    precedence
    over any diagram-specific settings.
    """
    ishikawa: Optional[IshikawaDiagramConfig] = None
    journey: Optional[JourneyDiagramConfig] = None
    kanban: Optional[KanbanDiagramConfig] = None
    layout: Optional[str] = None
    """Defines which layout algorithm to use for rendering the diagram.
    
    Defaults to `elk`, which is bundled with mermaid. The `tiny` build omits
    ELK to stay small and falls back to `dagre`.
    """
    legacy_math_ml: Optional[bool] = None
    """This option specifies if Mermaid can expect the dependent to include KaTeX stylesheets
    for browsers
    without their own MathML implementation. If this option is disabled and MathML is not
    supported, the math
    equations are replaced with a warning. If this option is enabled and MathML is not
    supported, Mermaid will
    fall back to legacy rendering for KaTeX.
    """
    log_level: Optional[Union[float, LogLevelEnum]] = None
    """This option decides the amount of logging to be used by mermaid."""

    look: Optional[Look] = None
    markdown_auto_wrap: Optional[bool] = None
    max_edges: Optional[int] = None
    """Defines the maximum number of edges that can be drawn in a graph."""

    max_text_size: Optional[float] = None
    """The maximum allowed size of the users text diagram"""

    mindmap: Optional[MindmapDiagramConfig] = None
    packet: Optional[PacketDiagramConfig] = None
    pie: Optional[PieDiagramConfig] = None
    quadrant_chart: Optional[QuadrantChartConfig] = None
    radar: Optional[RadarDiagramConfig] = None
    railroad: Optional[RailroadDiagramConfig] = None
    requirement: Optional[RequirementDiagramConfig] = None
    sankey: Optional[SankeyDiagramConfig] = None
    secure: Optional[List[str]] = None
    """This option controls which `currentConfig` keys are considered secure and
    can only be changed via call to `mermaid.initialize`.
    This prevents malicious graph directives from overriding a site's default security.
    """
    security_level: Optional[SecurityLevel] = None
    """Level of trust for parsed diagram"""

    sequence: Optional[SequenceDiagramConfig] = None
    start_on_load: Optional[bool] = None
    """Dictates whether mermaid starts on Page load"""

    state: Optional[StateDiagramConfig] = None
    suppress_error_rendering: Optional[bool] = None
    """Suppresses inserting 'Syntax error' diagram in the DOM.
    This is useful when you want to control how to handle syntax errors in your application.
    """
    swimlane: Optional[SwimlaneDiagramConfig] = None
    theme: Optional[Theme] = None
    theme_css: Optional[str] = None
    theme_variables: Any = None
    timeline: Optional[TimelineDiagramConfig] = None
    tree_view: Optional[TreeViewDiagramConfig] = None
    usecase: Optional[UsecaseDiagramConfig] = None
    venn: Optional[VennDiagramConfig] = None
    wardley_beta: Optional[WardleyDiagramConfig] = None
    wrap: Optional[bool] = None
    xy_chart: Optional[XYChartConfig] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "MermaidConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        agentflow = from_union([AgentflowDiagramConfig.from_dict, from_none], obj.get("agentflow"))
        alt_font_family = from_union([from_str, from_none], obj.get("altFontFamily"))
        architecture = from_union(
            [ArchitectureDiagramConfig.from_dict, from_none], obj.get("architecture")
        )
        arrow_marker_absolute = from_union([from_bool, from_none], obj.get("arrowMarkerAbsolute"))
        block = from_union([BlockDiagramConfig.from_dict, from_none], obj.get("block"))
        c4 = from_union([C4DiagramConfig.from_dict, from_none], obj.get("c4"))
        mermaid_config_class = from_union(
            [ClassDiagramConfig.from_dict, from_none], obj.get("class")
        )
        cynefin = from_union([CynefinDiagramConfig.from_dict, from_none], obj.get("cynefin"))
        dark_mode = from_union([from_bool, from_none], obj.get("darkMode"))
        deterministic_ids = from_union([from_bool, from_none], obj.get("deterministicIds"))
        deterministic_id_seed = from_union([from_str, from_none], obj.get("deterministicIDSeed"))
        dompurify_config = from_union(
            [lambda x: from_dict(lambda x: x, x), from_none], obj.get("dompurifyConfig")
        )
        elk = from_union([Elk.from_dict, from_none], obj.get("elk"))
        er = from_union([ErDiagramConfig.from_dict, from_none], obj.get("er"))
        eventmodeling = from_union(
            [EventModelingDiagramConfig.from_dict, from_none], obj.get("eventmodeling")
        )
        flowchart = from_union([FlowchartDiagramConfig.from_dict, from_none], obj.get("flowchart"))
        font_family = from_union([from_str, from_none], obj.get("fontFamily"))
        font_size = from_union([from_float, from_none], obj.get("fontSize"))
        force_legacy_math_ml = from_union([from_bool, from_none], obj.get("forceLegacyMathML"))
        gantt = from_union([GanttDiagramConfig.from_dict, from_none], obj.get("gantt"))
        git_graph = from_union([GitGraphDiagramConfig.from_dict, from_none], obj.get("gitGraph"))
        hand_drawn_seed = from_union([from_float, from_none], obj.get("handDrawnSeed"))
        html_labels = from_union([from_bool, from_none], obj.get("htmlLabels"))
        ishikawa = from_union([IshikawaDiagramConfig.from_dict, from_none], obj.get("ishikawa"))
        journey = from_union([JourneyDiagramConfig.from_dict, from_none], obj.get("journey"))
        kanban = from_union([KanbanDiagramConfig.from_dict, from_none], obj.get("kanban"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        legacy_math_ml = from_union([from_bool, from_none], obj.get("legacyMathML"))
        log_level = from_union([from_float, LogLevelEnum, from_none], obj.get("logLevel"))
        look = from_union([Look, from_none], obj.get("look"))
        markdown_auto_wrap = from_union([from_bool, from_none], obj.get("markdownAutoWrap"))
        max_edges = from_union([from_int, from_none], obj.get("maxEdges"))
        max_text_size = from_union([from_float, from_none], obj.get("maxTextSize"))
        mindmap = from_union([MindmapDiagramConfig.from_dict, from_none], obj.get("mindmap"))
        packet = from_union([PacketDiagramConfig.from_dict, from_none], obj.get("packet"))
        pie = from_union([PieDiagramConfig.from_dict, from_none], obj.get("pie"))
        quadrant_chart = from_union(
            [QuadrantChartConfig.from_dict, from_none], obj.get("quadrantChart")
        )
        radar = from_union([RadarDiagramConfig.from_dict, from_none], obj.get("radar"))
        railroad = from_union([RailroadDiagramConfig.from_dict, from_none], obj.get("railroad"))
        requirement = from_union(
            [RequirementDiagramConfig.from_dict, from_none], obj.get("requirement")
        )
        sankey = from_union([SankeyDiagramConfig.from_dict, from_none], obj.get("sankey"))
        secure = from_union([lambda x: from_list(from_str, x), from_none], obj.get("secure"))
        security_level = from_union([SecurityLevel, from_none], obj.get("securityLevel"))
        sequence = from_union([SequenceDiagramConfig.from_dict, from_none], obj.get("sequence"))
        start_on_load = from_union([from_bool, from_none], obj.get("startOnLoad"))
        state = from_union([StateDiagramConfig.from_dict, from_none], obj.get("state"))
        suppress_error_rendering = from_union(
            [from_bool, from_none], obj.get("suppressErrorRendering")
        )
        swimlane = from_union([SwimlaneDiagramConfig.from_dict, from_none], obj.get("swimlane"))
        theme = from_union([Theme, from_none], obj.get("theme"))
        theme_css = from_union([from_str, from_none], obj.get("themeCSS"))
        theme_variables = obj.get("themeVariables")
        timeline = from_union([TimelineDiagramConfig.from_dict, from_none], obj.get("timeline"))
        tree_view = from_union([TreeViewDiagramConfig.from_dict, from_none], obj.get("treeView"))
        usecase = from_union([UsecaseDiagramConfig.from_dict, from_none], obj.get("usecase"))
        venn = from_union([VennDiagramConfig.from_dict, from_none], obj.get("venn"))
        wardley_beta = from_union(
            [WardleyDiagramConfig.from_dict, from_none], obj.get("wardley-beta")
        )
        wrap = from_union([from_bool, from_none], obj.get("wrap"))
        xy_chart = from_union([XYChartConfig.from_dict, from_none], obj.get("xyChart"))
        return MermaidConfig(
            agentflow,
            alt_font_family,
            architecture,
            arrow_marker_absolute,
            block,
            c4,
            mermaid_config_class,
            cynefin,
            dark_mode,
            deterministic_ids,
            deterministic_id_seed,
            dompurify_config,
            elk,
            er,
            eventmodeling,
            flowchart,
            font_family,
            font_size,
            force_legacy_math_ml,
            gantt,
            git_graph,
            hand_drawn_seed,
            html_labels,
            ishikawa,
            journey,
            kanban,
            layout,
            legacy_math_ml,
            log_level,
            look,
            markdown_auto_wrap,
            max_edges,
            max_text_size,
            mindmap,
            packet,
            pie,
            quadrant_chart,
            radar,
            railroad,
            requirement,
            sankey,
            secure,
            security_level,
            sequence,
            start_on_load,
            state,
            suppress_error_rendering,
            swimlane,
            theme,
            theme_css,
            theme_variables,
            timeline,
            tree_view,
            usecase,
            venn,
            wardley_beta,
            wrap,
            xy_chart,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.agentflow is not None:
            result["agentflow"] = from_union(
                [lambda x: to_class(AgentflowDiagramConfig, x), from_none], self.agentflow
            )
        if self.alt_font_family is not None:
            result["altFontFamily"] = from_union([from_str, from_none], self.alt_font_family)
        if self.architecture is not None:
            result["architecture"] = from_union(
                [lambda x: to_class(ArchitectureDiagramConfig, x), from_none], self.architecture
            )
        if self.arrow_marker_absolute is not None:
            result["arrowMarkerAbsolute"] = from_union(
                [from_bool, from_none], self.arrow_marker_absolute
            )
        if self.block is not None:
            result["block"] = from_union(
                [lambda x: to_class(BlockDiagramConfig, x), from_none], self.block
            )
        if self.c4 is not None:
            result["c4"] = from_union([lambda x: to_class(C4DiagramConfig, x), from_none], self.c4)
        if self.mermaid_config_class is not None:
            result["class"] = from_union(
                [lambda x: to_class(ClassDiagramConfig, x), from_none], self.mermaid_config_class
            )
        if self.cynefin is not None:
            result["cynefin"] = from_union(
                [lambda x: to_class(CynefinDiagramConfig, x), from_none], self.cynefin
            )
        if self.dark_mode is not None:
            result["darkMode"] = from_union([from_bool, from_none], self.dark_mode)
        if self.deterministic_ids is not None:
            result["deterministicIds"] = from_union([from_bool, from_none], self.deterministic_ids)
        if self.deterministic_id_seed is not None:
            result["deterministicIDSeed"] = from_union(
                [from_str, from_none], self.deterministic_id_seed
            )
        if self.dompurify_config is not None:
            result["dompurifyConfig"] = from_union(
                [lambda x: from_dict(lambda x: x, x), from_none], self.dompurify_config
            )
        if self.elk is not None:
            result["elk"] = from_union([lambda x: to_class(Elk, x), from_none], self.elk)
        if self.er is not None:
            result["er"] = from_union([lambda x: to_class(ErDiagramConfig, x), from_none], self.er)
        if self.eventmodeling is not None:
            result["eventmodeling"] = from_union(
                [lambda x: to_class(EventModelingDiagramConfig, x), from_none], self.eventmodeling
            )
        if self.flowchart is not None:
            result["flowchart"] = from_union(
                [lambda x: to_class(FlowchartDiagramConfig, x), from_none], self.flowchart
            )
        if self.font_family is not None:
            result["fontFamily"] = from_union([from_str, from_none], self.font_family)
        if self.font_size is not None:
            result["fontSize"] = from_union([to_float, from_none], self.font_size)
        if self.force_legacy_math_ml is not None:
            result["forceLegacyMathML"] = from_union(
                [from_bool, from_none], self.force_legacy_math_ml
            )
        if self.gantt is not None:
            result["gantt"] = from_union(
                [lambda x: to_class(GanttDiagramConfig, x), from_none], self.gantt
            )
        if self.git_graph is not None:
            result["gitGraph"] = from_union(
                [lambda x: to_class(GitGraphDiagramConfig, x), from_none], self.git_graph
            )
        if self.hand_drawn_seed is not None:
            result["handDrawnSeed"] = from_union([to_float, from_none], self.hand_drawn_seed)
        if self.html_labels is not None:
            result["htmlLabels"] = from_union([from_bool, from_none], self.html_labels)
        if self.ishikawa is not None:
            result["ishikawa"] = from_union(
                [lambda x: to_class(IshikawaDiagramConfig, x), from_none], self.ishikawa
            )
        if self.journey is not None:
            result["journey"] = from_union(
                [lambda x: to_class(JourneyDiagramConfig, x), from_none], self.journey
            )
        if self.kanban is not None:
            result["kanban"] = from_union(
                [lambda x: to_class(KanbanDiagramConfig, x), from_none], self.kanban
            )
        if self.layout is not None:
            result["layout"] = from_union([from_str, from_none], self.layout)
        if self.legacy_math_ml is not None:
            result["legacyMathML"] = from_union([from_bool, from_none], self.legacy_math_ml)
        if self.log_level is not None:
            result["logLevel"] = from_union(
                [to_float, lambda x: to_enum(LogLevelEnum, x), from_none], self.log_level
            )
        if self.look is not None:
            result["look"] = from_union([lambda x: to_enum(Look, x), from_none], self.look)
        if self.markdown_auto_wrap is not None:
            result["markdownAutoWrap"] = from_union([from_bool, from_none], self.markdown_auto_wrap)
        if self.max_edges is not None:
            result["maxEdges"] = from_union([from_int, from_none], self.max_edges)
        if self.max_text_size is not None:
            result["maxTextSize"] = from_union([to_float, from_none], self.max_text_size)
        if self.mindmap is not None:
            result["mindmap"] = from_union(
                [lambda x: to_class(MindmapDiagramConfig, x), from_none], self.mindmap
            )
        if self.packet is not None:
            result["packet"] = from_union(
                [lambda x: to_class(PacketDiagramConfig, x), from_none], self.packet
            )
        if self.pie is not None:
            result["pie"] = from_union(
                [lambda x: to_class(PieDiagramConfig, x), from_none], self.pie
            )
        if self.quadrant_chart is not None:
            result["quadrantChart"] = from_union(
                [lambda x: to_class(QuadrantChartConfig, x), from_none], self.quadrant_chart
            )
        if self.radar is not None:
            result["radar"] = from_union(
                [lambda x: to_class(RadarDiagramConfig, x), from_none], self.radar
            )
        if self.railroad is not None:
            result["railroad"] = from_union(
                [lambda x: to_class(RailroadDiagramConfig, x), from_none], self.railroad
            )
        if self.requirement is not None:
            result["requirement"] = from_union(
                [lambda x: to_class(RequirementDiagramConfig, x), from_none], self.requirement
            )
        if self.sankey is not None:
            result["sankey"] = from_union(
                [lambda x: to_class(SankeyDiagramConfig, x), from_none], self.sankey
            )
        if self.secure is not None:
            result["secure"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.secure
            )
        if self.security_level is not None:
            result["securityLevel"] = from_union(
                [lambda x: to_enum(SecurityLevel, x), from_none], self.security_level
            )
        if self.sequence is not None:
            result["sequence"] = from_union(
                [lambda x: to_class(SequenceDiagramConfig, x), from_none], self.sequence
            )
        if self.start_on_load is not None:
            result["startOnLoad"] = from_union([from_bool, from_none], self.start_on_load)
        if self.state is not None:
            result["state"] = from_union(
                [lambda x: to_class(StateDiagramConfig, x), from_none], self.state
            )
        if self.suppress_error_rendering is not None:
            result["suppressErrorRendering"] = from_union(
                [from_bool, from_none], self.suppress_error_rendering
            )
        if self.swimlane is not None:
            result["swimlane"] = from_union(
                [lambda x: to_class(SwimlaneDiagramConfig, x), from_none], self.swimlane
            )
        if self.theme is not None:
            result["theme"] = from_union([lambda x: to_enum(Theme, x), from_none], self.theme)
        if self.theme_css is not None:
            result["themeCSS"] = from_union([from_str, from_none], self.theme_css)
        if self.theme_variables is not None:
            result["themeVariables"] = self.theme_variables
        if self.timeline is not None:
            result["timeline"] = from_union(
                [lambda x: to_class(TimelineDiagramConfig, x), from_none], self.timeline
            )
        if self.tree_view is not None:
            result["treeView"] = from_union(
                [lambda x: to_class(TreeViewDiagramConfig, x), from_none], self.tree_view
            )
        if self.usecase is not None:
            result["usecase"] = from_union(
                [lambda x: to_class(UsecaseDiagramConfig, x), from_none], self.usecase
            )
        if self.venn is not None:
            result["venn"] = from_union(
                [lambda x: to_class(VennDiagramConfig, x), from_none], self.venn
            )
        if self.wardley_beta is not None:
            result["wardley-beta"] = from_union(
                [lambda x: to_class(WardleyDiagramConfig, x), from_none], self.wardley_beta
            )
        if self.wrap is not None:
            result["wrap"] = from_union([from_bool, from_none], self.wrap)
        if self.xy_chart is not None:
            result["xyChart"] = from_union(
                [lambda x: to_class(XYChartConfig, x), from_none], self.xy_chart
            )
        return result


class DiagramType(Enum):
    """The diagram body type. Each value names a body schema that is generated independently in
    its own file. Populated with `flowchart` for now; more values are added as body types are
    modeled.
    """

    FLOWCHART = "flowchart"


@dataclass
class MermaidDirectives(DataModelHelper):
    """Optional. Pre-render directives.

    Mermaid pre-render directives (the `%%{ ... }%%` block). API docs:
    https://mermaid.ai/open-source/config/directives.html . Placeholder: a single generic
    `init` object for now, to be refined later.
    """

    init: Dict[str, Any]
    """The `%%{init: ...}%%` directive payload. Generic object for now; to be refined later."""

    @classmethod
    def from_dict(cls, obj: Any) -> "MermaidDirectives":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        init = from_dict(lambda x: x, obj.get("init"))
        return MermaidDirectives(init)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["init"] = from_dict(lambda x: x, self.init)
        return result


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
