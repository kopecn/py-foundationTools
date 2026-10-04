"""Tests for media fit modes and region aspect/fill fields (chunk 04).

Contract: .claude/specs/presentationSchema.md R18. ``image`` and ``mermaid`` blocks MAY
declare a ``fit`` mode (``contain`` | ``cover`` | ``fitWidth`` | ``fitHeight``), with
``contain`` the schema-declared default for both -- the one intentional new default in
this series, an R12 semver bump. ``cover`` MAY carry focal-point metadata. A visual
region MAY declare ``preferredAspectRatio``/``minAspectRatio``/``maxAspectRatio`` and
``minFillRatio``. Every field besides ``fit`` stays additive, optional, and
default-less.
"""

import json
from pathlib import Path

from foundationTypes.presentationTypes.Presentations import (
    ContentBlock,
    ContentType,
    Fit,
    FocalPoint,
    Region,
)

SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schema" / "schemas" / "Presentations"


def test_fit_field_roundtrip_with_default() -> None:
    # R12/R18: the schema itself declares "contain" as fit's default -- the
    # one intentional new default in this series.
    deck_schema = json.loads(
        (SCHEMA_DIR / "PresentationDeck-schema.json").read_text(encoding="utf-8")
    )
    fit_field = deck_schema["definitions"]["contentBlock"]["properties"]["fit"]
    assert fit_field["enum"] == ["contain", "cover", "fitWidth", "fitHeight"]
    assert fit_field["default"] == "contain"

    block = ContentBlock(
        region="hero",
        type=ContentType.IMAGE,
        source="hero.png",
        fit=Fit.COVER,
        focal_point=FocalPoint(x=0.25, y=0.75),
    )

    round_tripped = ContentBlock.from_dict(block.to_dict())

    assert round_tripped == block
    assert round_tripped.fit == Fit.COVER
    assert round_tripped.focal_point == FocalPoint(x=0.25, y=0.75)


def test_mermaid_block_also_accepts_fit() -> None:
    # R18 declares 'contain' the default for both image and mermaid blocks --
    # fit is one shared field, not type-conditional, so mermaid accepts every
    # arm identically.
    block = ContentBlock(
        region="diagram",
        type=ContentType.MERMAID,
        mermaid_source="graph TD;",
        fit=Fit.FIT_WIDTH,
    )

    round_tripped = ContentBlock.from_dict(block.to_dict())

    assert round_tripped == block
    assert round_tripped.fit == Fit.FIT_WIDTH


def test_region_aspect_and_fill_roundtrip() -> None:
    region = Region(
        id="hero_image",
        preferred_aspect_ratio=1.778,
        min_aspect_ratio=1.5,
        max_aspect_ratio=2.0,
        min_fill_ratio=0.8,
    )

    round_tripped = Region.from_dict(region.to_dict())

    assert round_tripped == region
    assert round_tripped.preferred_aspect_ratio == 1.778
    assert round_tripped.min_aspect_ratio == 1.5
    assert round_tripped.max_aspect_ratio == 2.0
    assert round_tripped.min_fill_ratio == 0.8


def test_existing_image_block_and_region_still_valid() -> None:
    block = ContentBlock(region="hero", type=ContentType.IMAGE, source="hero.png")
    round_tripped = ContentBlock.from_dict(block.to_dict())
    assert round_tripped == block
    assert round_tripped.fit is None
    assert round_tripped.focal_point is None

    region = Region(id="hero_image")
    round_tripped_region = Region.from_dict(region.to_dict())
    assert round_tripped_region == region
    assert round_tripped_region.preferred_aspect_ratio is None
    assert round_tripped_region.min_aspect_ratio is None
    assert round_tripped_region.max_aspect_ratio is None
    assert round_tripped_region.min_fill_ratio is None
