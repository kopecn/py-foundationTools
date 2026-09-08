"""
Aspect-preserving contain-fit geometry for the Presentations domain (plan 12).

Placing an image into a layout region requires scaling the image's intrinsic
pixel size to fit inside the region's bounding box without distorting it.
This module reads "scale it to bounding box" as *contain*: the image is
scaled (up or down) so it fits entirely inside the box while preserving its
aspect ratio, then centered within the box. A plain stretch to the box's
width/height would distort any image whose aspect ratio does not match the
box exactly, which is the surprising outcome this function avoids.

Pure stdlib arithmetic, no I/O: the caller supplies the image's intrinsic
pixel dimensions (which only an image-reading library downstream can obtain)
and this returns the placement rectangle in the same units as the box.
"""

__all__ = ["fit_into_box"]


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
