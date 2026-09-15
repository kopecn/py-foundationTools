"""Tests for metric region role styles (chunk 03).

Contract: .claude/specs/presentationSchema.md R17. A ``metric`` region MAY declare
separate style roles for ``value``, ``label``, and ``delta`` (each reusing the
existing ``style`` shape via ``$ref``, per R2 -- not re-declared), an inter-field
gap, and whether ``label``/``delta`` are permitted. All fields are additive and
optional -- no field is required and none carries a schema default; absence of a
permitted flag means permitted.
"""

from foundationTypes.presentationTypes.Presentations import Region, Style


def test_metric_role_styles_roundtrip() -> None:
    region = Region(
        id="headline_metric",
        value_style=Style(bold=True, font_size=48.0),
        label_style=Style(font_size=14.0),
        delta_style=Style(font_size=12.0, bold=False),
    )

    round_tripped = Region.from_dict(region.to_dict())

    assert round_tripped == region
    assert round_tripped.value_style == Style(bold=True, font_size=48.0)
    assert round_tripped.label_style == Style(font_size=14.0)
    assert round_tripped.delta_style == Style(font_size=12.0, bold=False)


def test_metric_gap_and_flags() -> None:
    region = Region(
        id="headline_metric",
        metric_gap=8.0,
        label_permitted=False,
        delta_permitted=False,
    )

    round_tripped = Region.from_dict(region.to_dict())

    assert round_tripped == region
    assert round_tripped.metric_gap == 8.0
    assert round_tripped.label_permitted is False
    assert round_tripped.delta_permitted is False


def test_existing_metric_region_still_valid() -> None:
    region = Region(id="headline_metric")

    round_tripped = Region.from_dict(region.to_dict())

    assert round_tripped == region
    assert round_tripped.value_style is None
    assert round_tripped.label_style is None
    assert round_tripped.delta_style is None
    assert round_tripped.metric_gap is None
    assert round_tripped.label_permitted is None
    assert round_tripped.delta_permitted is None
