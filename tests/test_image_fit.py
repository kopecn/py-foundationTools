"""
Unit tests for foundation_tools.presentation.image_fit.fit_into_box (plan 12).

fit_into_box scales an intrinsic (width, height) to fit inside a box while
preserving aspect ratio (contain), centered. These tests cover the four cases
called out in the plan: wider-than-box, taller-than-box, exact-fit, and
already-smaller, asserting both aspect-ratio preservation and centering.
"""

from foundation_tools.presentation.image_fit import fit_into_box


def test_wider_than_box_is_letterboxed_and_centered() -> None:
    # Intrinsic image is much wider (relative to its height) than the box.
    x, y, width, height = fit_into_box(
        intrinsic_width=2000,
        intrinsic_height=500,
        box_x=0,
        box_y=0,
        box_width=1000,
        box_height=1000,
    )

    # Width-limited: fills the box's width, height shrinks to preserve aspect.
    assert width == 1000
    assert height == 250
    # Aspect ratio preserved.
    assert width / height == 2000 / 500
    # Centered: fills the full box width, so x sits at the box origin; the
    # shrunk height is vertically centered in the box.
    assert x == 0
    assert y == 375


def test_taller_than_box_is_pillarboxed_and_centered() -> None:
    # Intrinsic image is much taller (relative to its width) than the box.
    x, y, width, height = fit_into_box(
        intrinsic_width=500,
        intrinsic_height=2000,
        box_x=0,
        box_y=0,
        box_width=1000,
        box_height=1000,
    )

    # Height-limited: fills the box's height, width shrinks to preserve aspect.
    assert height == 1000
    assert width == 250
    assert width / height == 500 / 2000
    # Centered: fills the full box height, so y sits at the box origin; the
    # shrunk width is horizontally centered in the box.
    assert y == 0
    assert x == 375


def test_exact_fit_matches_box_exactly() -> None:
    x, y, width, height = fit_into_box(
        intrinsic_width=800,
        intrinsic_height=600,
        box_x=10,
        box_y=20,
        box_width=800,
        box_height=600,
    )

    assert (x, y, width, height) == (10, 20, 800, 600)


def test_already_smaller_than_box_still_scales_up_to_contain() -> None:
    # "Scale it to bounding box" is read as contain: fit fully inside the box,
    # so a smaller intrinsic image is scaled up (not left at native size).
    x, y, width, height = fit_into_box(
        intrinsic_width=100,
        intrinsic_height=100,
        box_x=0,
        box_y=0,
        box_width=1000,
        box_height=500,
    )

    # Height-limited (box is wider than tall, image is square): height fills
    # the box, width shrinks to match since aspect is 1:1.
    assert height == 500
    assert width == 500
    assert width / height == 100 / 100
    assert y == 0
    assert x == 250


def test_result_respects_box_offset() -> None:
    # A non-zero box origin translates the centered placement, not just the size.
    x, y, width, height = fit_into_box(
        intrinsic_width=200,
        intrinsic_height=100,
        box_x=50,
        box_y=50,
        box_width=200,
        box_height=200,
    )

    assert width == 200
    assert height == 100
    assert x == 50
    assert y == 100
