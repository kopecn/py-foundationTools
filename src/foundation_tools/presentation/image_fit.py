"""
Aspect-preserving media fit geometry for the Presentations domain (plan 12;
extended by chunk 04 / R18 for `cover`, `fitWidth`, `fitHeight`).

Placing media into a layout region requires scaling its intrinsic pixel size
against the region's bounding box. `fit_into_box` reads "scale it to bounding
box" as *contain*: the media is scaled (up or down) so it fits entirely inside
the box while preserving its aspect ratio, then centered within the box. A
plain stretch to the box's width/height would distort any media whose aspect
ratio does not match the box exactly, which is the surprising outcome `contain`
avoids.

`cover_into_box`, `fit_width_into_box`, and `fit_height_into_box` are sibling
total functions for R18's other fit modes: `cover` fills the box exactly,
preserving aspect ratio by cropping the overflow (deterministic crop fractions
in [0, 1)); `fitWidth`/`fitHeight` each match exactly one box dimension,
preserving aspect ratio and allowing the other dimension to overflow or
underflow the box, centered about it.

Pure stdlib arithmetic, no I/O: the caller supplies the media's intrinsic
pixel dimensions (which only an image-reading library downstream can obtain)
and each function returns geometry in the same units as the box.
"""

__all__ = [
    "fit_into_box",
    "cover_into_box",
    "fit_width_into_box",
    "fit_height_into_box",
]


def fit_into_box(
    intrinsic_width: float,
    intrinsic_height: float,
    box_x: float,
    box_y: float,
    box_width: float,
    box_height: float,
) -> tuple[float, float, float, float]:
    """Scale (intrinsic_width, intrinsic_height) to fit inside the box preserving
    aspect ratio, centered. Returns (x, y, width, height) in the same pixel units."""
    intrinsic_aspect = intrinsic_width / intrinsic_height
    box_aspect = box_width / box_height

    if intrinsic_aspect > box_aspect:
        # Wider than the box (relative to height): width is the limiting
        # dimension, height shrinks to preserve aspect ratio.
        width = box_width
        height = box_width / intrinsic_aspect
    else:
        # Taller than (or equal to) the box: height is the limiting
        # dimension, width shrinks to preserve aspect ratio.
        height = box_height
        width = box_height * intrinsic_aspect

    x = box_x + (box_width - width) / 2
    y = box_y + (box_height - height) / 2

    return (x, y, width, height)


def cover_into_box(
    intrinsic_width: float,
    intrinsic_height: float,
    box_x: float,
    box_y: float,
    box_width: float,
    box_height: float,
) -> tuple[float, float, float, float, float, float, float, float]:
    """Scale (intrinsic_width, intrinsic_height) to fully cover the box (no
    letterboxing), centered, cropping whatever overflows. Returns
    (x, y, width, height, crop_left, crop_right, crop_top, crop_bottom): the
    placement rect always equals the box exactly, and the four crop fractions
    (each in [0, 1)) name the fraction of the scaled media cropped from that
    edge to fit the box."""
    scale = max(box_width / intrinsic_width, box_height / intrinsic_height)
    scaled_width = intrinsic_width * scale
    scaled_height = intrinsic_height * scale

    crop_x = (scaled_width - box_width) / scaled_width / 2
    crop_y = (scaled_height - box_height) / scaled_height / 2

    return (box_x, box_y, box_width, box_height, crop_x, crop_x, crop_y, crop_y)


def fit_width_into_box(
    intrinsic_width: float,
    intrinsic_height: float,
    box_x: float,
    box_y: float,
    box_width: float,
    box_height: float,
) -> tuple[float, float, float, float]:
    """Scale (intrinsic_width, intrinsic_height) so width matches the box
    exactly, preserving aspect ratio; the resulting height MAY overflow or
    underflow the box and is centered vertically about it. Returns
    (x, y, width, height) in the same pixel units as the box."""
    scale = box_width / intrinsic_width
    width = box_width
    height = intrinsic_height * scale

    x = box_x
    y = box_y + (box_height - height) / 2

    return (x, y, width, height)


def fit_height_into_box(
    intrinsic_width: float,
    intrinsic_height: float,
    box_x: float,
    box_y: float,
    box_width: float,
    box_height: float,
) -> tuple[float, float, float, float]:
    """Scale (intrinsic_width, intrinsic_height) so height matches the box
    exactly, preserving aspect ratio; the resulting width MAY overflow or
    underflow the box and is centered horizontally about it. Returns
    (x, y, width, height) in the same pixel units as the box."""
    scale = box_height / intrinsic_height
    height = box_height
    width = intrinsic_width * scale

    x = box_x + (box_width - width) / 2
    y = box_y

    return (x, y, width, height)
