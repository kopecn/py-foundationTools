"""Tests for bullet style/indent tokens and region paragraph rhythm (chunk 02).

Contract: .claude/specs/presentationSchema.md R16. A ``bullets`` content block MAY
declare a bullet ``style`` (``disc`` | ``dash`` | ``none``) plus bounded per-level
indent/hanging-indent tokens. A text-bearing region MAY declare paragraph rhythm --
``lineSpacing``, ``spaceBefore``, ``spaceAfter``. All fields are additive and
optional -- no field is required and none carries a schema default.
"""

from foundationTypes.presentationTypes.Presentations import (
    BulletStyle,
    ContentBlock,
    ContentType,
    Region,
)


def test_bullets_style_and_indent_roundtrip() -> None:
    block = ContentBlock(
        region="body",
        type=ContentType.BULLETS,
        items=["First", "Second"],
        bullet_levels=[0, 1],
        bullet_style=BulletStyle.DASH,
        bullet_indent=[0.0, 24.0, 48.0],
        bullet_hanging_indent=[12.0, 12.0, 12.0],
    )

    round_tripped = ContentBlock.from_dict(block.to_dict())

    assert round_tripped == block
    assert round_tripped.bullet_style == BulletStyle.DASH
    assert round_tripped.bullet_indent == [0.0, 24.0, 48.0]
    assert round_tripped.bullet_hanging_indent == [12.0, 12.0, 12.0]


def test_region_rhythm_roundtrip() -> None:
    region = Region(
        id="body",
        line_spacing=1.15,
        space_before=8.0,
        space_after=4.0,
    )

    round_tripped = Region.from_dict(region.to_dict())

    assert round_tripped == region
    assert round_tripped.line_spacing == 1.15
    assert round_tripped.space_before == 8.0
    assert round_tripped.space_after == 4.0


def test_existing_bullets_still_valid() -> None:
    block = ContentBlock(region="body", type=ContentType.BULLETS, items=["Only item"])

    round_tripped = ContentBlock.from_dict(block.to_dict())

    assert round_tripped == block
    assert round_tripped.bullet_style is None
    assert round_tripped.bullet_indent is None
    assert round_tripped.bullet_hanging_indent is None

    region = Region(id="body")
    round_tripped_region = Region.from_dict(region.to_dict())

    assert round_tripped_region == region
    assert round_tripped_region.line_spacing is None
    assert round_tripped_region.space_before is None
    assert round_tripped_region.space_after is None
