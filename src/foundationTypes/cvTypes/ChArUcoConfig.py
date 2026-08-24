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
    from_float,
    from_int,
    from_none,
    from_union,
    to_class,
    to_enum,
    to_float,
)

T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


class ArucoDictionary(Enum):
    """Predefined OpenCV marker dictionary used to generate and detect the board."""

    DICT_4_X4_100 = "DICT_4X4_100"
    DICT_4_X4_1000 = "DICT_4X4_1000"
    DICT_4_X4_250 = "DICT_4X4_250"
    DICT_4_X4_50 = "DICT_4X4_50"
    DICT_5_X5_100 = "DICT_5X5_100"
    DICT_5_X5_1000 = "DICT_5X5_1000"
    DICT_5_X5_250 = "DICT_5X5_250"
    DICT_5_X5_50 = "DICT_5X5_50"
    DICT_6_X6_100 = "DICT_6X6_100"
    DICT_6_X6_1000 = "DICT_6X6_1000"
    DICT_6_X6_250 = "DICT_6X6_250"
    DICT_6_X6_50 = "DICT_6X6_50"
    DICT_7_X7_100 = "DICT_7X7_100"
    DICT_7_X7_1000 = "DICT_7X7_1000"
    DICT_7_X7_250 = "DICT_7X7_250"
    DICT_7_X7_50 = "DICT_7X7_50"
    DICT_APRILTAG_16_H5 = "DICT_APRILTAG_16H5"
    DICT_APRILTAG_25_H9 = "DICT_APRILTAG_25H9"
    DICT_APRILTAG_36_H10 = "DICT_APRILTAG_36H10"
    DICT_APRILTAG_36_H11 = "DICT_APRILTAG_36H11"
    DICT_ARUCO_ORIGINAL = "DICT_ARUCO_ORIGINAL"


@dataclass
class ChArUcoBoard(DataModelHelper):
    """Physical geometry of a ChArUco calibration board: a chessboard pattern with embedded
    ArUco markers used for camera calibration and pose estimation. Deliberately excludes
    rendering concerns so the same board can be reused across render targets.

    Physical geometry of the ChArUco calibration board.
    """

    marker_length: float
    """Physical side length of each ArUco marker. Must be smaller than square_length; not
    enforced by this schema, validate at the application layer.
    """
    square_length: float
    """Physical side length of each chessboard square. All dimensions must use the same unit."""

    squares_x: int
    """Number of chessboard squares across the board."""

    squares_y: int
    """Number of chessboard squares down the board."""

    dictionary: ArucoDictionary | None = None

    @classmethod
    def from_dict(cls, obj: Any) -> "ChArUcoBoard":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        marker_length = from_float(obj.get("marker_length"))
        square_length = from_float(obj.get("square_length"))
        squares_x = from_int(obj.get("squares_x"))
        squares_y = from_int(obj.get("squares_y"))
        dictionary = from_union([ArucoDictionary, from_none], obj.get("dictionary"))
        return ChArUcoBoard(marker_length, square_length, squares_x, squares_y, dictionary)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["marker_length"] = to_float(self.marker_length)
        result["square_length"] = to_float(self.square_length)
        result["squares_x"] = from_int(self.squares_x)
        result["squares_y"] = from_int(self.squares_y)
        if self.dictionary is not None:
            result["dictionary"] = from_union(
                [lambda x: to_enum(ArucoDictionary, x), from_none], self.dictionary
            )
        return result


@dataclass
class ChArUcoRenderOptions(DataModelHelper):
    """Specifies how a ChArUco board should be rendered into an image (PNG, PDF, SVG, etc.)
    suitable for display or printing. Orthogonal to ChArUcoBoard so the same board can be
    rendered at multiple sizes/resolutions.

    Rendering parameters for producing an image of the board.
    """

    image_height: int
    """Height of the generated image in pixels."""

    image_width: int
    """Width of the generated image in pixels."""

    border_bits: int | None = None
    """Width of the black border surrounding each ArUco marker, expressed in marker cells."""

    dpi: int | None = None
    """Target print resolution in dots per inch."""

    margin_size: int | None = None
    """White border around the board, measured in pixels."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ChArUcoRenderOptions":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        image_height = from_int(obj.get("image_height"))
        image_width = from_int(obj.get("image_width"))
        border_bits = from_union([from_int, from_none], obj.get("border_bits"))
        dpi = from_union([from_int, from_none], obj.get("dpi"))
        margin_size = from_union([from_int, from_none], obj.get("margin_size"))
        return ChArUcoRenderOptions(image_height, image_width, border_bits, dpi, margin_size)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["image_height"] = from_int(self.image_height)
        result["image_width"] = from_int(self.image_width)
        if self.border_bits is not None:
            result["border_bits"] = from_union([from_int, from_none], self.border_bits)
        if self.dpi is not None:
            result["dpi"] = from_union([from_int, from_none], self.dpi)
        if self.margin_size is not None:
            result["margin_size"] = from_union([from_int, from_none], self.margin_size)
        return result


@dataclass
class ChArUcoConfig(DataModelHelper):
    """Combined ChArUco codegen document: pairs a board's physical geometry with a set of render
    options. Kept as a thin composition of ChArUcoBoard and ChArUcoRenderOptions so either
    can be reused independently while this schema drives the single generated model consumers
    actually construct.
    """

    board: ChArUcoBoard
    """Physical geometry of the ChArUco calibration board."""

    render: ChArUcoRenderOptions
    """Rendering parameters for producing an image of the board."""

    @classmethod
    def from_dict(cls, obj: Any) -> "ChArUcoConfig":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        board = ChArUcoBoard.from_dict(obj.get("board"))
        render = ChArUcoRenderOptions.from_dict(obj.get("render"))
        return ChArUcoConfig(board, render)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["board"] = to_class(ChArUcoBoard, self.board)
        result["render"] = to_class(ChArUcoRenderOptions, self.render)
        return result


def ch_ar_uco_board_from_dict(s: Any) -> ChArUcoBoard:
    return ChArUcoBoard.from_dict(s)


def ch_ar_uco_board_to_dict(x: ChArUcoBoard) -> Any:
    return to_class(ChArUcoBoard, x)


def ch_ar_uco_render_options_from_dict(s: Any) -> ChArUcoRenderOptions:
    return ChArUcoRenderOptions.from_dict(s)


def ch_ar_uco_render_options_to_dict(x: ChArUcoRenderOptions) -> Any:
    return to_class(ChArUcoRenderOptions, x)


def ch_ar_uco_config_from_dict(s: Any) -> ChArUcoConfig:
    return ChArUcoConfig.from_dict(s)


def ch_ar_uco_config_to_dict(x: ChArUcoConfig) -> Any:
    return to_class(ChArUcoConfig, x)
