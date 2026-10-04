"""Tests for layout capacity and semantic roles (chunk 06).

Contract: .claude/specs/presentationSchema.md R20. A ``region`` MAY declare
``allowedContentTypes``, occupancy (``required`` | ``recommended`` | ``optional``),
``maxLines``, ``maxCharacters``, ``maxItems``, ``maxCharactersPerItem``, and a semantic
``role``. A ``layout`` MAY declare a ``purpose`` tag set and a ``density`` class.
``preferredAspectRatio`` is the single field shared with R18 (chunk 04) -- this chunk
reuses that one declaration on ``region`` rather than redeclaring it. All fields are
additive and optional -- no field is required and none carries a schema default.
"""

import json
from pathlib import Path

from foundationTypes.presentationTypes.Presentations import (
    ContentType,
    Density,
    Occupancy,
    PresentationSlideLayouts,
    Purpose,
    Region,
    Role,
    SlideLayout,
)

SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schema" / "schemas" / "Presentations"


def test_region_capacity_roundtrip() -> None:
    region = Region(
        id="body",
        allowed_content_types=[ContentType.TEXT, ContentType.BULLETS],
        occupancy=Occupancy.REQUIRED,
        max_lines=4,
        max_characters=400,
        max_items=5,
        max_characters_per_item=80,
    )

    round_tripped = Region.from_dict(region.to_dict())

    assert round_tripped == region
    assert round_tripped.allowed_content_types == [ContentType.TEXT, ContentType.BULLETS]
    assert round_tripped.occupancy == Occupancy.REQUIRED
    assert round_tripped.max_lines == 4
    assert round_tripped.max_characters == 400
    assert round_tripped.max_items == 5
    assert round_tripped.max_characters_per_item == 80


def test_occupancy_and_role_enums() -> None:
    region = Region(id="presenter", occupancy=Occupancy.RECOMMENDED, role=Role.PRESENTER_NAME)

    round_tripped = Region.from_dict(region.to_dict())

    assert round_tripped == region
    assert round_tripped.occupancy == Occupancy.RECOMMENDED
    assert round_tripped.role == Role.PRESENTER_NAME

    for occupancy in (Occupancy.REQUIRED, Occupancy.RECOMMENDED, Occupancy.OPTIONAL):
        assert Region.from_dict(Region(id="x", occupancy=occupancy).to_dict()).occupancy == (
            occupancy
        )

    for role in (Role.PRESENTER_NAME, Role.DECK_TITLE, Role.METRIC_VALUE, Role.EVIDENCE):
        assert Region.from_dict(Region(id="x", role=role).to_dict()).role == role


def test_layout_purpose_density_roundtrip() -> None:
    layout = SlideLayout(
        id="impact-metrics",
        name="Impact metrics",
        regions=[Region(id="body")],
        purpose=[Purpose.METRIC, Purpose.EVIDENCE],
        density=Density.DENSE,
    )

    round_tripped = SlideLayout.from_dict(layout.to_dict())

    assert round_tripped == layout
    assert round_tripped.purpose == [Purpose.METRIC, Purpose.EVIDENCE]
    assert round_tripped.density == Density.DENSE


def test_preferred_aspect_ref_shared() -> None:
    # R20 shares the single preferredAspectRatio declared on 'region' (chunk 04)
    # rather than redeclaring a copy -- assert exactly one definition site exists.
    schema_text = (SCHEMA_DIR / "PresentationSlideLayouts-schema.json").read_text(
        encoding="utf-8"
    )
    assert schema_text.count('"preferredAspectRatio":') == 1

    region_schema = json.loads(schema_text)["definitions"]["region"]["properties"]
    assert "preferredAspectRatio" in region_schema
    assert "$ref" not in region_schema["preferredAspectRatio"]


def test_existing_layout_still_valid() -> None:
    layout = SlideLayout(id="title-content", name="Title + content", regions=[Region(id="body")])

    round_tripped = SlideLayout.from_dict(layout.to_dict())

    assert round_tripped == layout
    assert round_tripped.purpose is None
    assert round_tripped.density is None

    region = Region(id="body")
    round_tripped_region = Region.from_dict(region.to_dict())
    assert round_tripped_region == region
    assert round_tripped_region.allowed_content_types is None
    assert round_tripped_region.occupancy is None
    assert round_tripped_region.max_characters is None
    assert round_tripped_region.max_items is None
    assert round_tripped_region.max_characters_per_item is None
    assert round_tripped_region.role is None

    # A schema-valid slide layouts document without any R20 fields still parses.
    doc = {
        "defaults": {},
        "layouts": [layout.to_dict()],
    }
    parsed = PresentationSlideLayouts.from_dict(doc)
    assert parsed.layouts[0].id == "title-content"
