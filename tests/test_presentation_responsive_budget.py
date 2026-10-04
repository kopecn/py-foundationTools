"""Tests for the responsive fit budget on region (chunk 01).

Contract: .claude/specs/presentationSchema.md R15. A region MAY declare
``overflow: shrink`` plus ``minFontSize``, ``maxLines``, and ``scaleLadder`` to
bound deterministic shrinking. All fields are additive and optional -- no
field is required and none carries a schema default.
"""

from foundationTypes.presentationTypes.Presentations import Overflow, Region


def test_region_accepts_shrink_and_budget() -> None:
    region = Region(
        id="body",
        overflow=Overflow.SHRINK,
        min_font_size=10.0,
        max_lines=4,
        scale_ladder=[24.0, 20.0, 16.0, 12.0],
    )

    round_tripped = Region.from_dict(region.to_dict())

    assert round_tripped == region
    assert round_tripped.overflow == Overflow.SHRINK
    assert round_tripped.min_font_size == 10.0
    assert round_tripped.max_lines == 4
    assert round_tripped.scale_ladder == [24.0, 20.0, 16.0, 12.0]


def test_existing_region_still_valid() -> None:
    region = Region(id="body", overflow=Overflow.WRAP)

    round_tripped = Region.from_dict(region.to_dict())

    assert round_tripped == region
    assert round_tripped.min_font_size is None
    assert round_tripped.max_lines is None
    assert round_tripped.scale_ladder is None
