"""Unit tests for the cover/fitWidth/fitHeight geometry added to
foundation_tools.presentation.image_fit (chunk 04, R18).

fit_into_box (plan 12) already covers `contain`. This adds pure, total sibling
functions for the remaining R18 fit modes: cover_into_box (fills the box
exactly, cropping the overflow -- crop fractions in [0, 1)), fit_width_into_box,
and fit_height_into_box (each matches exactly one box dimension, allowing
overflow or underflow on the other, centered about the box). No I/O, no
distortion for contain (unchanged), deterministic crop for cover.
"""

import foundation_tools.presentation
from foundation_tools.presentation import (
    cover_into_box,
    fit_height_into_box,
    fit_into_box,
    fit_width_into_box,
)


def test_package_exports_all_media_fit_helpers_once() -> None:
    for helper_name in (
        "cover_into_box",
        "fit_height_into_box",
        "fit_into_box",
        "fit_width_into_box",
    ):
        assert foundation_tools.presentation.__all__.count(helper_name) == 1


def test_contain_unchanged() -> None:
    # R18 adds sibling fit modes; contain's existing behavior (plan 12) must
    # not change. Re-assert a previously-covered case verbatim.
    x, y, width, height = fit_into_box(
        intrinsic_width=2000,
        intrinsic_height=500,
        box_x=0,
        box_y=0,
        box_width=1000,
        box_height=1000,
    )
    assert (x, y, width, height) == (0, 375, 1000, 250)


def test_cover_geometry_deterministic() -> None:
    # Wider-than-box image: cover fills the box exactly and crops left/right.
    result = cover_into_box(
        intrinsic_width=2000,
        intrinsic_height=500,
        box_x=0,
        box_y=0,
        box_width=1000,
        box_height=1000,
    )
    x, y, width, height, crop_l, crop_r, crop_t, crop_b = result

    # Placement rect always equals the box exactly -- cover never letterboxes.
    assert (x, y, width, height) == (0, 0, 1000, 1000)
    # Height is the limiting dimension (image is much wider than tall): no
    # vertical crop, and the horizontal crop is centered (equal both sides)
    # and bounded to [0, 1).
    assert crop_t == 0
    assert crop_b == 0
    assert crop_l == crop_r == 0.375
    assert 0 <= crop_l < 1

    # Deterministic: identical inputs produce identical outputs.
    assert cover_into_box(2000, 500, 0, 0, 1000, 1000) == result


def test_cover_geometry_crops_vertically_for_tall_image() -> None:
    # Taller-than-box image: cover crops top/bottom instead, with a non-zero
    # box origin translating the placement rect too.
    x, y, width, height, crop_l, crop_r, crop_t, crop_b = cover_into_box(
        intrinsic_width=500,
        intrinsic_height=2000,
        box_x=10,
        box_y=20,
        box_width=1000,
        box_height=1000,
    )
    assert (x, y, width, height) == (10, 20, 1000, 1000)
    assert crop_l == 0
    assert crop_r == 0
    assert crop_t == crop_b == 0.375
    assert 0 <= crop_t < 1


def test_cover_geometry_exact_fit_has_no_crop() -> None:
    # Intrinsic aspect ratio already matches the box: no cropping needed.
    x, y, width, height, crop_l, crop_r, crop_t, crop_b = cover_into_box(
        intrinsic_width=800,
        intrinsic_height=600,
        box_x=0,
        box_y=0,
        box_width=800,
        box_height=600,
    )
    assert (x, y, width, height) == (0, 0, 800, 600)
    assert (crop_l, crop_r, crop_t, crop_b) == (0, 0, 0, 0)


def test_fitwidth_fitheight_geometry() -> None:
    # fitWidth: scale so width matches the box exactly; height may overflow
    # or underflow the box, and is centered vertically about the box.
    x, y, width, height = fit_width_into_box(
        intrinsic_width=2000,
        intrinsic_height=500,
        box_x=0,
        box_y=0,
        box_width=1000,
        box_height=100,
    )
    assert width == 1000
    assert height == 250  # overflows the 100px-tall box on purpose
    assert x == 0
    assert y == -75  # centered: (100 - 250) / 2

    # fitHeight: scale so height matches the box exactly; width may overflow
    # or underflow the box, and is centered horizontally about the box.
    x, y, width, height = fit_height_into_box(
        intrinsic_width=500,
        intrinsic_height=2000,
        box_x=0,
        box_y=0,
        box_width=100,
        box_height=1000,
    )
    assert height == 1000
    assert width == 250
    assert y == 0
    assert x == -75


def test_fitwidth_fitheight_respect_box_offset() -> None:
    x, y, width, height = fit_width_into_box(
        intrinsic_width=1000,
        intrinsic_height=1000,
        box_x=50,
        box_y=50,
        box_width=200,
        box_height=200,
    )
    assert (x, y, width, height) == (50, 50, 200, 200)

    x, y, width, height = fit_height_into_box(
        intrinsic_width=1000,
        intrinsic_height=1000,
        box_x=50,
        box_y=50,
        box_width=200,
        box_height=200,
    )
    assert (x, y, width, height) == (50, 50, 200, 200)
