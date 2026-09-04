# =============================================================================
# AUTO-GENERATED FILE — DO NOT EDIT
# Generated from JSON Schema via quicktype. Any manual edits will be
# overwritten the next time codegen runs (make codegen-all).
# To modify, update the source schema in schema/schemas/ and re-run codegen.
# =============================================================================

from dataclasses import dataclass
from enum import Enum
from typing import Any, TypeVar

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

T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


@dataclass
class PresentationColor(DataModelHelper):
    """Primary accent color used for borders, outlines, indicators, icons, or other visual
    emphasis.

    A presentation color represented by RGB channel values, an optional opacity, and a
    human-readable color name. RGB values are authoritative; the name is a descriptive label.
    Opacity defaults to fully opaque when omitted.

    Background or fill color used with the accent treatment.

    Text color intended to be rendered on top of the accent background.

    Primary presentation background color.

    Secondary text color for supporting descriptions, metadata, labels, and lower-emphasis
    content.

    Primary presentation text color used for titles, headings, and high-emphasis content.
    """

    b: int
    """Blue channel value from 0 to 255."""

    g: int
    """Green channel value from 0 to 255."""

    name: str
    """Human-readable descriptive name for the color."""

    r: int
    """Red channel value from 0 to 255."""

    opacity: float | None = None
    """Optional opacity from 0 to 1, where 0 is fully transparent and 1 is fully opaque."""

    @classmethod
    def from_dict(cls, obj: Any) -> "PresentationColor":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        b = from_int(obj.get("b"))
        g = from_int(obj.get("g"))
        name = from_str(obj.get("name"))
        r = from_int(obj.get("r"))
        opacity = from_union([from_float, from_none], obj.get("opacity"))
        return PresentationColor(b, g, name, r, opacity)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["b"] = from_int(self.b)
        result["g"] = from_int(self.g)
        result["name"] = from_str(self.name)
        result["r"] = from_int(self.r)
        if self.opacity is not None:
            result["opacity"] = from_union([to_float, from_none], self.opacity)
        return result


@dataclass
class PresentationAccent(DataModelHelper):
    """Semantic treatment for caution, emerging risks, trends, and attention-worthy
    information.

    Semantic presentation accent consisting of a primary accent color, a supporting
    background color, and a text color intended to remain legible when rendered over the
    accent background.

    Semantic treatment for informational content, neutral emphasis, and reference data.

    Semantic treatment for positive outcomes, recommendations, completed work, and healthy
    states.

    Neutral treatment for secondary information, structural elements, borders, dividers,
    disabled states, metadata, and other low-emphasis content.

    Semantic treatment for specialized, exploratory, analytical, or distinctive content that
    benefits from visual differentiation.

    Semantic treatment for failures, risks, incidents, warnings, and urgent information.

    Semantic treatment for secondary emphasis, technical content, systems, data flows, and
    supporting information.

    Semantic treatment for attention, highlights, pending states, notable changes, and
    information requiring visual emphasis.
    """

    accent: PresentationColor
    """Primary accent color used for borders, outlines, indicators, icons, or other visual
    emphasis.
    """
    background: PresentationColor
    """Background or fill color used with the accent treatment."""

    text: PresentationColor
    """Text color intended to be rendered on top of the accent background."""

    @classmethod
    def from_dict(cls, obj: Any) -> "PresentationAccent":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        accent = PresentationColor.from_dict(obj.get("accent"))
        background = PresentationColor.from_dict(obj.get("background"))
        text = PresentationColor.from_dict(obj.get("text"))
        return PresentationAccent(accent, background, text)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["accent"] = to_class(PresentationColor, self.accent)
        result["background"] = to_class(PresentationColor, self.background)
        result["text"] = to_class(PresentationColor, self.text)
        return result


@dataclass
class PresentationColorTheme(DataModelHelper):
    """Presentation color theme defining the background, text, semantic accent colors, and chart
    palette. All colors use a reusable RGB color type with three integer channels from 0 to
    255 and a human-readable color name.
    """

    accent_amber: PresentationAccent
    """Semantic treatment for caution, emerging risks, trends, and attention-worthy information."""

    accent_blue: PresentationAccent
    """Semantic treatment for informational content, neutral emphasis, and reference data."""

    accent_green: PresentationAccent
    """Semantic treatment for positive outcomes, recommendations, completed work, and healthy
    states.
    """
    accent_grey: PresentationAccent
    """Neutral treatment for secondary information, structural elements, borders, dividers,
    disabled states, metadata, and other low-emphasis content.
    """
    accent_purple: PresentationAccent
    """Semantic treatment for specialized, exploratory, analytical, or distinctive content that
    benefits from visual differentiation.
    """
    accent_red: PresentationAccent
    """Semantic treatment for failures, risks, incidents, warnings, and urgent information."""

    accent_teal: PresentationAccent
    """Semantic treatment for secondary emphasis, technical content, systems, data flows, and
    supporting information.
    """
    accent_yellow: PresentationAccent
    """Semantic treatment for attention, highlights, pending states, notable changes, and
    information requiring visual emphasis.
    """
    background: PresentationColor
    """Primary presentation background color."""

    chart_colors: list[PresentationColor]
    """Ordered palette of colors used for categorical charts and visual data series."""

    muted_text: PresentationColor
    """Secondary text color for supporting descriptions, metadata, labels, and lower-emphasis
    content.
    """
    text: PresentationColor
    """Primary presentation text color used for titles, headings, and high-emphasis content."""

    @classmethod
    def from_dict(cls, obj: Any) -> "PresentationColorTheme":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        accent_amber = PresentationAccent.from_dict(obj.get("accentAmber"))
        accent_blue = PresentationAccent.from_dict(obj.get("accentBlue"))
        accent_green = PresentationAccent.from_dict(obj.get("accentGreen"))
        accent_grey = PresentationAccent.from_dict(obj.get("accentGrey"))
        accent_purple = PresentationAccent.from_dict(obj.get("accentPurple"))
        accent_red = PresentationAccent.from_dict(obj.get("accentRed"))
        accent_teal = PresentationAccent.from_dict(obj.get("accentTeal"))
        accent_yellow = PresentationAccent.from_dict(obj.get("accentYellow"))
        background = PresentationColor.from_dict(obj.get("background"))
        chart_colors = from_list(PresentationColor.from_dict, obj.get("chartColors"))
        muted_text = PresentationColor.from_dict(obj.get("mutedText"))
        text = PresentationColor.from_dict(obj.get("text"))
        return PresentationColorTheme(
            accent_amber,
            accent_blue,
            accent_green,
            accent_grey,
            accent_purple,
            accent_red,
            accent_teal,
            accent_yellow,
            background,
            chart_colors,
            muted_text,
            text,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["accentAmber"] = to_class(PresentationAccent, self.accent_amber)
        result["accentBlue"] = to_class(PresentationAccent, self.accent_blue)
        result["accentGreen"] = to_class(PresentationAccent, self.accent_green)
        result["accentGrey"] = to_class(PresentationAccent, self.accent_grey)
        result["accentPurple"] = to_class(PresentationAccent, self.accent_purple)
        result["accentRed"] = to_class(PresentationAccent, self.accent_red)
        result["accentTeal"] = to_class(PresentationAccent, self.accent_teal)
        result["accentYellow"] = to_class(PresentationAccent, self.accent_yellow)
        result["background"] = to_class(PresentationColor, self.background)
        result["chartColors"] = from_list(
            lambda x: to_class(PresentationColor, x), self.chart_colors
        )
        result["mutedText"] = to_class(PresentationColor, self.muted_text)
        result["text"] = to_class(PresentationColor, self.text)
        return result


class ThemeColorRef(Enum):
    """Default semantic color resolved from PresentationColorTheme.

    Address of a color in PresentationColorTheme. Scalars are named directly; accents are
    addressed as <accent>.<channel>.

    Semantic color name resolved from PresentationColorTheme.

    Optional semantic series color resolved from PresentationColorTheme.

    Semantic color resolved from PresentationColorTheme.
    """

    ACCENT_AMBER_ACCENT = "accentAmber.accent"
    ACCENT_AMBER_BACKGROUND = "accentAmber.background"
    ACCENT_AMBER_TEXT = "accentAmber.text"
    ACCENT_BLUE_ACCENT = "accentBlue.accent"
    ACCENT_BLUE_BACKGROUND = "accentBlue.background"
    ACCENT_BLUE_TEXT = "accentBlue.text"
    ACCENT_GREEN_ACCENT = "accentGreen.accent"
    ACCENT_GREEN_BACKGROUND = "accentGreen.background"
    ACCENT_GREEN_TEXT = "accentGreen.text"
    ACCENT_GREY_ACCENT = "accentGrey.accent"
    ACCENT_GREY_BACKGROUND = "accentGrey.background"
    ACCENT_GREY_TEXT = "accentGrey.text"
    ACCENT_PURPLE_ACCENT = "accentPurple.accent"
    ACCENT_PURPLE_BACKGROUND = "accentPurple.background"
    ACCENT_PURPLE_TEXT = "accentPurple.text"
    ACCENT_RED_ACCENT = "accentRed.accent"
    ACCENT_RED_BACKGROUND = "accentRed.background"
    ACCENT_RED_TEXT = "accentRed.text"
    ACCENT_TEAL_ACCENT = "accentTeal.accent"
    ACCENT_TEAL_BACKGROUND = "accentTeal.background"
    ACCENT_TEAL_TEXT = "accentTeal.text"
    ACCENT_YELLOW_ACCENT = "accentYellow.accent"
    ACCENT_YELLOW_BACKGROUND = "accentYellow.background"
    ACCENT_YELLOW_TEXT = "accentYellow.text"
    BACKGROUND = "background"
    MUTED_TEXT = "mutedText"
    TEXT = "text"


@dataclass
class RegionDefaults(DataModelHelper):
    """Default geometry and styling for body regions.

    Default geometry, font size, and color for a region type.

    Default geometry and styling for title regions.
    """

    color: ThemeColorRef | None = None
    """Default semantic color resolved from PresentationColorTheme."""

    font_size: float | None = None
    """Default font size in points."""

    height: float | None = None
    """Default region height in pixels."""

    width: float | None = None
    """Default region width in pixels."""

    x: float | None = None
    """Default horizontal offset in pixels from the canvas origin."""

    y: float | None = None
    """Default vertical offset in pixels from the canvas origin."""

    @classmethod
    def from_dict(cls, obj: Any) -> "RegionDefaults":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        color = from_union([ThemeColorRef, from_none], obj.get("color"))
        font_size = from_union([from_float, from_none], obj.get("fontSize"))
        height = from_union([from_float, from_none], obj.get("height"))
        width = from_union([from_float, from_none], obj.get("width"))
        x = from_union([from_float, from_none], obj.get("x"))
        y = from_union([from_float, from_none], obj.get("y"))
        return RegionDefaults(color, font_size, height, width, x, y)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.color is not None:
            result["color"] = from_union(
                [lambda x: to_enum(ThemeColorRef, x), from_none], self.color
            )
        if self.font_size is not None:
            result["fontSize"] = from_union([to_float, from_none], self.font_size)
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
class Notes(DataModelHelper):
    """Speaker notes rendering defaults."""

    enabled: bool | None = None
    """Whether speaker notes are rendered."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Notes":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        enabled = from_union([from_bool, from_none], obj.get("enabled"))
        return Notes(enabled)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.enabled is not None:
            result["enabled"] = from_union([from_bool, from_none], self.enabled)
        return result


@dataclass
class LayoutDefaults(DataModelHelper):
    """Canvas geometry and per-region-type defaults shared by every layout.

    Canvas geometry and per-region-type defaults. The single owner of canvas dimensions and
    outer margin.
    """

    body: RegionDefaults | None = None
    """Default geometry and styling for body regions."""

    canvas_height: int | None = None
    """Canvas height in pixels. Layout region coordinates are absolute against this."""

    canvas_width: int | None = None
    """Canvas width in pixels. Layout region coordinates are absolute against this."""

    notes: Notes | None = None
    """Speaker notes rendering defaults."""

    outer_margin: int | None = None
    """Default outer margin in pixels."""

    title: RegionDefaults | None = None
    """Default geometry and styling for title regions."""

    @classmethod
    def from_dict(cls, obj: Any) -> "LayoutDefaults":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        body = from_union([RegionDefaults.from_dict, from_none], obj.get("body"))
        canvas_height = from_union([from_int, from_none], obj.get("canvasHeight"))
        canvas_width = from_union([from_int, from_none], obj.get("canvasWidth"))
        notes = from_union([Notes.from_dict, from_none], obj.get("notes"))
        outer_margin = from_union([from_int, from_none], obj.get("outerMargin"))
        title = from_union([RegionDefaults.from_dict, from_none], obj.get("title"))
        return LayoutDefaults(body, canvas_height, canvas_width, notes, outer_margin, title)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.body is not None:
            result["body"] = from_union(
                [lambda x: to_class(RegionDefaults, x), from_none], self.body
            )
        if self.canvas_height is not None:
            result["canvasHeight"] = from_union([from_int, from_none], self.canvas_height)
        if self.canvas_width is not None:
            result["canvasWidth"] = from_union([from_int, from_none], self.canvas_width)
        if self.notes is not None:
            result["notes"] = from_union([lambda x: to_class(Notes, x), from_none], self.notes)
        if self.outer_margin is not None:
            result["outerMargin"] = from_union([from_int, from_none], self.outer_margin)
        if self.title is not None:
            result["title"] = from_union(
                [lambda x: to_class(RegionDefaults, x), from_none], self.title
            )
        return result


class Align(Enum):
    """Horizontal text alignment."""

    CENTER = "center"
    LEFT = "left"
    RIGHT = "right"


class Overflow(Enum):
    """Behavior when content exceeds the region box. 'wrap' flows text within the box; 'clip'
    truncates at the boundary.
    """

    CLIP = "clip"
    WRAP = "wrap"


class RegionType(Enum):
    """Region kind, informing default styling."""

    BODY = "body"
    CHART = "chart"
    COLUMN = "column"
    FOOTER = "footer"
    IMAGE = "image"
    METRIC = "metric"
    NOTES = "notes"
    SUBTITLE = "subtitle"
    TABLE = "table"
    TITLE = "title"


class VerticalAlign(Enum):
    """Vertical text alignment."""

    BOTTOM = "bottom"
    MIDDLE = "middle"
    TOP = "top"


@dataclass
class Region(DataModelHelper):
    """A single addressable content area within a slide layout."""

    id: str
    """Region identifier referenced by a slide's content blocks."""

    align: Align | None = None
    """Horizontal text alignment."""

    color: ThemeColorRef | None = None
    """Semantic color name resolved from PresentationColorTheme."""

    font_size: float | None = None
    """Font size in points."""

    height: float | None = None
    """Region height in pixels."""

    overflow: Overflow | None = None
    """Behavior when content exceeds the region box. 'wrap' flows text within the box; 'clip'
    truncates at the boundary.
    """
    padding: float | None = None
    """Inner padding in pixels."""

    type: RegionType | None = None
    """Region kind, informing default styling."""

    vertical_align: VerticalAlign | None = None
    """Vertical text alignment."""

    width: float | None = None
    """Region width in pixels."""

    x: float | None = None
    """Horizontal offset in pixels from the canvas origin."""

    y: float | None = None
    """Vertical offset in pixels from the canvas origin."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Region":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_str(obj.get("id"))
        align = from_union([Align, from_none], obj.get("align"))
        color = from_union([ThemeColorRef, from_none], obj.get("color"))
        font_size = from_union([from_float, from_none], obj.get("fontSize"))
        height = from_union([from_float, from_none], obj.get("height"))
        overflow = from_union([Overflow, from_none], obj.get("overflow"))
        padding = from_union([from_float, from_none], obj.get("padding"))
        type = from_union([RegionType, from_none], obj.get("type"))
        vertical_align = from_union([VerticalAlign, from_none], obj.get("verticalAlign"))
        width = from_union([from_float, from_none], obj.get("width"))
        x = from_union([from_float, from_none], obj.get("x"))
        y = from_union([from_float, from_none], obj.get("y"))
        return Region(
            id,
            align,
            color,
            font_size,
            height,
            overflow,
            padding,
            type,
            vertical_align,
            width,
            x,
            y,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_str(self.id)
        if self.align is not None:
            result["align"] = from_union([lambda x: to_enum(Align, x), from_none], self.align)
        if self.color is not None:
            result["color"] = from_union(
                [lambda x: to_enum(ThemeColorRef, x), from_none], self.color
            )
        if self.font_size is not None:
            result["fontSize"] = from_union([to_float, from_none], self.font_size)
        if self.height is not None:
            result["height"] = from_union([to_float, from_none], self.height)
        if self.overflow is not None:
            result["overflow"] = from_union(
                [lambda x: to_enum(Overflow, x), from_none], self.overflow
            )
        if self.padding is not None:
            result["padding"] = from_union([to_float, from_none], self.padding)
        if self.type is not None:
            result["type"] = from_union([lambda x: to_enum(RegionType, x), from_none], self.type)
        if self.vertical_align is not None:
            result["verticalAlign"] = from_union(
                [lambda x: to_enum(VerticalAlign, x), from_none], self.vertical_align
            )
        if self.width is not None:
            result["width"] = from_union([to_float, from_none], self.width)
        if self.x is not None:
            result["x"] = from_union([to_float, from_none], self.x)
        if self.y is not None:
            result["y"] = from_union([to_float, from_none], self.y)
        return result


@dataclass
class SlideLayout(DataModelHelper):
    """A named, reusable arrangement of regions on the canvas."""

    id: str
    """Stable identifier referenced by slides."""

    name: str
    """Human-readable layout name."""

    regions: list[Region]
    """The regions making up this layout."""

    description: str | None = None
    """Human-readable layout description."""

    notes: str | None = None
    """Authoring guidance for agents or presentation generators."""

    @classmethod
    def from_dict(cls, obj: Any) -> "SlideLayout":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_str(obj.get("id"))
        name = from_str(obj.get("name"))
        regions = from_list(Region.from_dict, obj.get("regions"))
        description = from_union([from_str, from_none], obj.get("description"))
        notes = from_union([from_str, from_none], obj.get("notes"))
        return SlideLayout(id, name, regions, description, notes)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["id"] = from_str(self.id)
        result["name"] = from_str(self.name)
        result["regions"] = from_list(lambda x: to_class(Region, x), self.regions)
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.notes is not None:
            result["notes"] = from_union([from_str, from_none], self.notes)
        return result


@dataclass
class PresentationSlideLayouts(DataModelHelper):
    """Reusable slide layout definitions describing title, body, columns, metrics, and
    supporting regions.
    """

    defaults: LayoutDefaults
    """Canvas geometry and per-region-type defaults shared by every layout."""

    layouts: list[SlideLayout]
    """The reusable slide layout library."""

    @classmethod
    def from_dict(cls, obj: Any) -> "PresentationSlideLayouts":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        defaults = LayoutDefaults.from_dict(obj.get("defaults"))
        layouts = from_list(SlideLayout.from_dict, obj.get("layouts"))
        return PresentationSlideLayouts(defaults, layouts)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["defaults"] = to_class(LayoutDefaults, self.defaults)
        result["layouts"] = from_list(lambda x: to_class(SlideLayout, x), self.layouts)
        return result


@dataclass
class Defaults(DataModelHelper):
    """Rendering defaults inherited by slides and layouts unless overridden."""

    body_font_size: float | None = None
    """Default body font size in points."""

    font_family: str | None = None
    """Default font family."""

    small_font_size: float | None = None
    """Default small/footer font size in points."""

    title_font_size: float | None = None
    """Default title font size in points."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Defaults":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        body_font_size = from_union([from_float, from_none], obj.get("bodyFontSize"))
        font_family = from_union([from_str, from_none], obj.get("fontFamily"))
        small_font_size = from_union([from_float, from_none], obj.get("smallFontSize"))
        title_font_size = from_union([from_float, from_none], obj.get("titleFontSize"))
        return Defaults(body_font_size, font_family, small_font_size, title_font_size)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.body_font_size is not None:
            result["bodyFontSize"] = from_union([to_float, from_none], self.body_font_size)
        if self.font_family is not None:
            result["fontFamily"] = from_union([from_str, from_none], self.font_family)
        if self.small_font_size is not None:
            result["smallFontSize"] = from_union([to_float, from_none], self.small_font_size)
        if self.title_font_size is not None:
            result["titleFontSize"] = from_union([to_float, from_none], self.title_font_size)
        return result


class Format(Enum):
    """Output file format."""

    PPTX = "pptx"


@dataclass
class File(DataModelHelper):
    """Output file location and format."""

    name: str
    """Output filename including extension."""

    format: Format | None = None
    """Output file format."""

    path: str | None = None
    """Output directory. Defaults to the current working directory."""

    @classmethod
    def from_dict(cls, obj: Any) -> "File":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        name = from_str(obj.get("name"))
        format = from_union([Format, from_none], obj.get("format"))
        path = from_union([from_str, from_none], obj.get("path"))
        return File(name, format, path)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        if self.format is not None:
            result["format"] = from_union([lambda x: to_enum(Format, x), from_none], self.format)
        if self.path is not None:
            result["path"] = from_union([from_str, from_none], self.path)
        return result


@dataclass
class LayoutVersion(DataModelHelper):
    """Identity of the slide layout standard (PresentationSlideLayouts) this deck was authored
    against, recorded so a separate migration tool can later decide whether the deck needs
    updating to a newer layout standard. This library only records and round-trips this
    identity -- it does not resolve, store, or discover layout definitions.
    """

    id: str | None = None
    """Identifier of the layout standard, e.g. a layout-set name or slug."""

    version: str | None = None
    """Version of the layout standard."""

    @classmethod
    def from_dict(cls, obj: Any) -> "LayoutVersion":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_str, from_none], obj.get("id"))
        version = from_union([from_str, from_none], obj.get("version"))
        return LayoutVersion(id, version)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.id is not None:
            result["id"] = from_union([from_str, from_none], self.id)
        if self.version is not None:
            result["version"] = from_union([from_str, from_none], self.version)
        return result


@dataclass
class ThemeVersion(DataModelHelper):
    """Identity of the corporate color theme (PresentationColorTheme) this deck was authored
    against, recorded so a separate migration tool can later decide whether the deck needs
    updating to a newer corporate theme. This library only records and round-trips this
    identity -- it does not resolve, store, or discover theme definitions.
    """

    id: str | None = None
    """Identifier of the corporate theme, e.g. a theme name or slug."""

    version: str | None = None
    """Version of the corporate theme."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ThemeVersion":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        id = from_union([from_str, from_none], obj.get("id"))
        version = from_union([from_str, from_none], obj.get("version"))
        return ThemeVersion(id, version)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.id is not None:
            result["id"] = from_union([from_str, from_none], self.id)
        if self.version is not None:
            result["version"] = from_union([from_str, from_none], self.version)
        return result


@dataclass
class PresentationMetadata(DataModelHelper):
    """Deck-level metadata and rendering defaults for a presentation."""

    author: str
    """Primary presentation author."""

    company: str
    """Organization or company associated with the presentation."""

    date: str
    """Presentation date. Prefer ISO-8601 format when known."""

    file: File
    """Output file location and format."""

    title: str
    """Presentation title."""

    defaults: Defaults | None = None
    """Rendering defaults inherited by slides and layouts unless overridden."""

    description: str | None = None
    """Short description of the presentation purpose."""

    layout_version: LayoutVersion | None = None
    """Identity of the slide layout standard (PresentationSlideLayouts) this deck was authored
    against, recorded so a separate migration tool can later decide whether the deck needs
    updating to a newer layout standard. This library only records and round-trips this
    identity -- it does not resolve, store, or discover layout definitions.
    """
    subtitle: str | None = None
    """Optional presentation subtitle."""

    tags: list[str] | None = None
    """Free-form tags describing the presentation."""

    theme_version: ThemeVersion | None = None
    """Identity of the corporate color theme (PresentationColorTheme) this deck was authored
    against, recorded so a separate migration tool can later decide whether the deck needs
    updating to a newer corporate theme. This library only records and round-trips this
    identity -- it does not resolve, store, or discover theme definitions.
    """
    version: str | None = None
    """Optional presentation/content version."""

    @classmethod
    def from_dict(cls, obj: Any) -> "PresentationMetadata":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        author = from_str(obj.get("author"))
        company = from_str(obj.get("company"))
        date = from_str(obj.get("date"))
        file = File.from_dict(obj.get("file"))
        title = from_str(obj.get("title"))
        defaults = from_union([Defaults.from_dict, from_none], obj.get("defaults"))
        description = from_union([from_str, from_none], obj.get("description"))
        layout_version = from_union([LayoutVersion.from_dict, from_none], obj.get("layoutVersion"))
        subtitle = from_union([from_str, from_none], obj.get("subtitle"))
        tags = from_union([lambda x: from_list(from_str, x), from_none], obj.get("tags"))
        theme_version = from_union([ThemeVersion.from_dict, from_none], obj.get("themeVersion"))
        version = from_union([from_str, from_none], obj.get("version"))
        return PresentationMetadata(
            author,
            company,
            date,
            file,
            title,
            defaults,
            description,
            layout_version,
            subtitle,
            tags,
            theme_version,
            version,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["author"] = from_str(self.author)
        result["company"] = from_str(self.company)
        result["date"] = from_str(self.date)
        result["file"] = to_class(File, self.file)
        result["title"] = from_str(self.title)
        if self.defaults is not None:
            result["defaults"] = from_union(
                [lambda x: to_class(Defaults, x), from_none], self.defaults
            )
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.layout_version is not None:
            result["layoutVersion"] = from_union(
                [lambda x: to_class(LayoutVersion, x), from_none], self.layout_version
            )
        if self.subtitle is not None:
            result["subtitle"] = from_union([from_str, from_none], self.subtitle)
        if self.tags is not None:
            result["tags"] = from_union([lambda x: from_list(from_str, x), from_none], self.tags)
        if self.theme_version is not None:
            result["themeVersion"] = from_union(
                [lambda x: to_class(ThemeVersion, x), from_none], self.theme_version
            )
        if self.version is not None:
            result["version"] = from_union([from_str, from_none], self.version)
        return result


class ChartKind(Enum):
    """Chart kind for a 'chart' block. Placeholder set; an arm is added only once it is
    renderable downstream.
    """

    BAR = "bar"
    LINE = "line"


@dataclass
class TextRun(DataModelHelper):
    """A run of body text with uniform inline emphasis."""

    text: str
    """The run's literal text."""

    bold: bool | None = None
    """Whether the run renders bold."""

    italic: bool | None = None
    """Whether the run renders italic."""

    @classmethod
    def from_dict(cls, obj: Any) -> "TextRun":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        text = from_str(obj.get("text"))
        bold = from_union([from_bool, from_none], obj.get("bold"))
        italic = from_union([from_bool, from_none], obj.get("italic"))
        return TextRun(text, bold, italic)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["text"] = from_str(self.text)
        if self.bold is not None:
            result["bold"] = from_union([from_bool, from_none], self.bold)
        if self.italic is not None:
            result["italic"] = from_union([from_bool, from_none], self.italic)
        return result


@dataclass
class ChartSeries(DataModelHelper):
    """A named series of numeric values aligned to the chart's categories."""

    name: str
    """Series label for the legend."""

    values: list[float]
    """Numeric values, one per category."""

    color: ThemeColorRef | None = None
    """Optional semantic series color resolved from PresentationColorTheme."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ChartSeries":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        name = from_str(obj.get("name"))
        values = from_list(from_float, obj.get("values"))
        color = from_union([ThemeColorRef, from_none], obj.get("color"))
        return ChartSeries(name, values, color)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        result["values"] = from_list(to_float, self.values)
        if self.color is not None:
            result["color"] = from_union(
                [lambda x: to_enum(ThemeColorRef, x), from_none], self.color
            )
        return result


@dataclass
class Style(DataModelHelper):
    """Optional style overrides for this content block."""

    align: Align | None = None
    """Horizontal text alignment."""

    bold: bool | None = None
    """Whether the content renders bold."""

    color: ThemeColorRef | None = None
    """Semantic color resolved from PresentationColorTheme."""

    font_size: float | None = None
    """Font size override in points."""

    @classmethod
    def from_dict(cls, obj: Any) -> "Style":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        align = from_union([Align, from_none], obj.get("align"))
        bold = from_union([from_bool, from_none], obj.get("bold"))
        color = from_union([ThemeColorRef, from_none], obj.get("color"))
        font_size = from_union([from_float, from_none], obj.get("fontSize"))
        return Style(align, bold, color, font_size)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.align is not None:
            result["align"] = from_union([lambda x: to_enum(Align, x), from_none], self.align)
        if self.bold is not None:
            result["bold"] = from_union([from_bool, from_none], self.bold)
        if self.color is not None:
            result["color"] = from_union(
                [lambda x: to_enum(ThemeColorRef, x), from_none], self.color
            )
        if self.font_size is not None:
            result["fontSize"] = from_union([to_float, from_none], self.font_size)
        return result


class ContentType(Enum):
    """Content block kind. Each arm has a payload capable of expressing it and a renderer
    capable of drawing it, except 'mermaid': a schema-only nucleation point that stores
    diagram source with no renderer yet (see 'mermaidSource').
    """

    BULLETS = "bullets"
    CHART = "chart"
    IMAGE = "image"
    MERMAID = "mermaid"
    METRIC = "metric"
    TABLE = "table"
    TEXT = "text"


@dataclass
class ContentBlock(DataModelHelper):
    """A single piece of slide content placed into a named layout region."""

    region: str
    """Layout region that receives this content. Must not be a reserved region id ('title',
    'subtitle'), which are filled by the slide's own title and subtitle.
    """
    type: ContentType
    """Content block kind. Each arm has a payload capable of expressing it and a renderer
    capable of drawing it, except 'mermaid': a schema-only nucleation point that stores
    diagram source with no renderer yet (see 'mermaidSource').
    """
    bullet_levels: list[int] | None = None
    """Optional indent level per entry in 'items', 0 (outermost) to 4. Shorter than 'items'
    leaves the remaining bullets at level 0.
    """
    categories: list[str] | None = None
    """Shared x-axis category labels for a 'chart' block."""

    chart_kind: ChartKind | None = None
    """Chart kind for a 'chart' block. Placeholder set; an arm is added only once it is
    renderable downstream.
    """
    delta: str | None = None
    """Optional change indicator for a 'metric' block, e.g. '+3.1pp QoQ'. Empty when the metric
    shows no comparison.
    """
    headers: list[str] | None = None
    """Optional column headers for a 'table' block. Empty for a headerless table."""

    items: list[str] | None = None
    """Bullet items for a 'bullets' block."""

    label: str | None = None
    """Caption naming what a 'metric' block measures."""

    mermaid_source: str | None = None
    """Raw Mermaid diagram source text for a 'mermaid' block. This repository stores the source
    only; it does not parse, lay out, or render Mermaid diagrams. Rendering, if ever added,
    is a downstream (clerical-tools) concern.
    """
    rows: list[list[str]] | None = None
    """Row-major cells for a 'table' block. Every cell is a pre-formatted string; ragged rows
    are an authoring error the consumer reports.
    """
    runs: list[TextRun] | None = None
    """Inline emphasis runs for a 'text' block that needs mixed formatting. When present the
    renderer uses these instead of the flat 'text' string.
    """
    series: list[ChartSeries] | None = None
    """One or more named data series for a 'chart' block."""

    source: str | None = None
    """Filesystem path to the image file for an 'image' block."""

    style: Style | None = None
    """Optional style overrides for this content block."""

    text: str | None = None
    """Body text for a 'text' block."""

    value: str | None = None
    """Pre-formatted headline value for a 'metric' block, e.g. '$4.2M' or '+12%'. A string so
    number formatting and locale stay a renderer concern.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "ContentBlock":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        region = from_str(obj.get("region"))
        type = ContentType(obj.get("type"))
        bullet_levels = from_union(
            [lambda x: from_list(from_int, x), from_none], obj.get("bulletLevels")
        )
        categories = from_union(
            [lambda x: from_list(from_str, x), from_none], obj.get("categories")
        )
        chart_kind = from_union([ChartKind, from_none], obj.get("chartKind"))
        delta = from_union([from_str, from_none], obj.get("delta"))
        headers = from_union([lambda x: from_list(from_str, x), from_none], obj.get("headers"))
        items = from_union([lambda x: from_list(from_str, x), from_none], obj.get("items"))
        label = from_union([from_str, from_none], obj.get("label"))
        mermaid_source = from_union([from_str, from_none], obj.get("mermaidSource"))
        rows = from_union(
            [lambda x: from_list(lambda x: from_list(from_str, x), x), from_none], obj.get("rows")
        )
        runs = from_union([lambda x: from_list(TextRun.from_dict, x), from_none], obj.get("runs"))
        series = from_union(
            [lambda x: from_list(ChartSeries.from_dict, x), from_none], obj.get("series")
        )
        source = from_union([from_str, from_none], obj.get("source"))
        style = from_union([Style.from_dict, from_none], obj.get("style"))
        text = from_union([from_str, from_none], obj.get("text"))
        value = from_union([from_str, from_none], obj.get("value"))
        return ContentBlock(
            region,
            type,
            bullet_levels,
            categories,
            chart_kind,
            delta,
            headers,
            items,
            label,
            mermaid_source,
            rows,
            runs,
            series,
            source,
            style,
            text,
            value,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["region"] = from_str(self.region)
        result["type"] = to_enum(ContentType, self.type)
        if self.bullet_levels is not None:
            result["bulletLevels"] = from_union(
                [lambda x: from_list(from_int, x), from_none], self.bullet_levels
            )
        if self.categories is not None:
            result["categories"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.categories
            )
        if self.chart_kind is not None:
            result["chartKind"] = from_union(
                [lambda x: to_enum(ChartKind, x), from_none], self.chart_kind
            )
        if self.delta is not None:
            result["delta"] = from_union([from_str, from_none], self.delta)
        if self.headers is not None:
            result["headers"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.headers
            )
        if self.items is not None:
            result["items"] = from_union([lambda x: from_list(from_str, x), from_none], self.items)
        if self.label is not None:
            result["label"] = from_union([from_str, from_none], self.label)
        if self.mermaid_source is not None:
            result["mermaidSource"] = from_union([from_str, from_none], self.mermaid_source)
        if self.rows is not None:
            result["rows"] = from_union(
                [lambda x: from_list(lambda x: from_list(from_str, x), x), from_none], self.rows
            )
        if self.runs is not None:
            result["runs"] = from_union(
                [lambda x: from_list(lambda x: to_class(TextRun, x), x), from_none], self.runs
            )
        if self.series is not None:
            result["series"] = from_union(
                [lambda x: from_list(lambda x: to_class(ChartSeries, x), x), from_none], self.series
            )
        if self.source is not None:
            result["source"] = from_union([from_str, from_none], self.source)
        if self.style is not None:
            result["style"] = from_union([lambda x: to_class(Style, x), from_none], self.style)
        if self.text is not None:
            result["text"] = from_union([from_str, from_none], self.text)
        if self.value is not None:
            result["value"] = from_union([from_str, from_none], self.value)
        return result


@dataclass
class Slide(DataModelHelper):
    """A single slide referencing a reusable layout and carrying its content blocks."""

    layout: str
    """ID of a reusable slide layout."""

    number: int
    """1-based slide position within the deck."""

    content: list[ContentBlock] | None = None
    """Content blocks placed into the slide's layout regions."""

    hidden: bool | None = None
    """When true, the slide is excluded from the rendered deck."""

    id: str | None = None
    """Optional stable identifier for the slide."""

    notes: str | None = None
    """Speaker notes or agent instructions specific to this slide."""

    subtitle: str | None = None
    """Optional slide subtitle. When present it binds to the reserved region id 'subtitle' on
    the slide's layout; a missing region is an authoring error.
    """
    title: str | None = None
    """Slide title. Optional so a divider or full-bleed slide can omit one. When present it
    binds to the reserved region id 'title' on the slide's layout; a missing region is an
    authoring error.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "Slide":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        layout = from_str(obj.get("layout"))
        number = from_int(obj.get("number"))
        content = from_union(
            [lambda x: from_list(ContentBlock.from_dict, x), from_none], obj.get("content")
        )
        hidden = from_union([from_bool, from_none], obj.get("hidden"))
        id = from_union([from_str, from_none], obj.get("id"))
        notes = from_union([from_str, from_none], obj.get("notes"))
        subtitle = from_union([from_str, from_none], obj.get("subtitle"))
        title = from_union([from_str, from_none], obj.get("title"))
        return Slide(layout, number, content, hidden, id, notes, subtitle, title)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["layout"] = from_str(self.layout)
        result["number"] = from_int(self.number)
        if self.content is not None:
            result["content"] = from_union(
                [lambda x: from_list(lambda x: to_class(ContentBlock, x), x), from_none],
                self.content,
            )
        if self.hidden is not None:
            result["hidden"] = from_union([from_bool, from_none], self.hidden)
        if self.id is not None:
            result["id"] = from_union([from_str, from_none], self.id)
        if self.notes is not None:
            result["notes"] = from_union([from_str, from_none], self.notes)
        if self.subtitle is not None:
            result["subtitle"] = from_union([from_str, from_none], self.subtitle)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        return result


@dataclass
class PresentationDeck(DataModelHelper):
    """Presentation content consisting of ordered slides referencing reusable slide layouts."""

    metadata: PresentationMetadata
    slides: list[Slide]
    """Ordered slides making up the deck."""

    @classmethod
    def from_dict(cls, obj: Any) -> "PresentationDeck":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        metadata = PresentationMetadata.from_dict(obj.get("metadata"))
        slides = from_list(Slide.from_dict, obj.get("slides"))
        return PresentationDeck(metadata, slides)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["metadata"] = to_class(PresentationMetadata, self.metadata)
        result["slides"] = from_list(lambda x: to_class(Slide, x), self.slides)
        return result


def presentation_color_theme_from_dict(s: Any) -> PresentationColorTheme:
    return PresentationColorTheme.from_dict(s)


def presentation_color_theme_to_dict(x: PresentationColorTheme) -> Any:
    return to_class(PresentationColorTheme, x)


def presentation_metadata_from_dict(s: Any) -> PresentationMetadata:
    return PresentationMetadata.from_dict(s)


def presentation_metadata_to_dict(x: PresentationMetadata) -> Any:
    return to_class(PresentationMetadata, x)


def presentation_slide_layouts_from_dict(s: Any) -> PresentationSlideLayouts:
    return PresentationSlideLayouts.from_dict(s)


def presentation_slide_layouts_to_dict(x: PresentationSlideLayouts) -> Any:
    return to_class(PresentationSlideLayouts, x)


def presentation_deck_from_dict(s: Any) -> PresentationDeck:
    return PresentationDeck.from_dict(s)


def presentation_deck_to_dict(x: PresentationDeck) -> Any:
    return to_class(PresentationDeck, x)
