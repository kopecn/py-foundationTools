import json
from pathlib import Path
from typing import Any

import pytest

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schema" / "schemas" / "Presentations"


def _load(name: str) -> dict[str, Any]:
    with (SCHEMA_DIR / name).open(encoding="utf-8") as f:
        result: dict[str, Any] = json.load(f)
        return result


def test_no_layout_library_key_anywhere() -> None:
    for path in SCHEMA_DIR.glob("*.json"):
        text = path.read_text(encoding="utf-8")
        assert "layoutLibrary" not in text, f"layoutLibrary still present in {path.name}"


def test_deck_has_no_local_metadata_definition() -> None:
    deck = _load("PresentationDeck-schema.json")
    assert "presentationMetadata" not in deck.get("definitions", {})


def test_deck_metadata_is_bare_filename_ref() -> None:
    deck = _load("PresentationDeck-schema.json")
    assert deck["properties"]["metadata"] == {"$ref": "PresentationMetadata-schema.json"}


def test_deck_has_no_layouts_field() -> None:
    deck = _load("PresentationDeck-schema.json")
    assert "layouts" not in deck["properties"]


def test_content_block_type_enum_includes_metric_table_chart() -> None:
    # Tier 2 adds metric + table (chunk 06) and chart (chunk 08) now that each
    # has a flat payload; text and bullets keep their tier-1 leading positions.
    # Tier 3 chunk 11 adds "mermaid" as a schema-only nucleation point (source
    # stored, not rendered here) -- see test_content_block_mermaid_payload_field_present.
    # Chunk 12 adds "image" now that it has a typed payload (the source path),
    # the tier R7 named for admitting image -- see the image source field test.
    deck = _load("PresentationDeck-schema.json")
    content_block = deck["definitions"]["contentBlock"]
    assert content_block["properties"]["type"]["enum"] == [
        "text",
        "bullets",
        "metric",
        "table",
        "chart",
        "mermaid",
        "image",
    ]


def test_content_block_untyped_data_bag_stays_removed() -> None:
    # R7: contentBlock.data (untyped object) SHALL stay gone, and an arm stays
    # out of the enum until a tier gives it a typed payload. image shipped in
    # chunk 12 (typed source payload); quote is still unshipped.
    deck = _load("PresentationDeck-schema.json")
    content_block = deck["definitions"]["contentBlock"]
    assert "data" not in content_block["properties"]
    for unshipped in ("quote",):
        assert unshipped not in content_block["properties"]["type"]["enum"]


def test_content_block_metric_and_table_payload_fields_present() -> None:
    # R9: metric and table are flat sibling fields, not nested payload objects.
    deck = _load("PresentationDeck-schema.json")
    props = deck["definitions"]["contentBlock"]["properties"]
    for field in ("value", "label", "delta", "headers", "rows"):
        assert field in props, f"{field} missing from contentBlock properties"
    assert props["headers"]["items"] == {"type": "string"}
    assert props["rows"]["items"] == {"type": "array", "items": {"type": "string"}}


def test_content_block_rich_text_and_chart_payload_fields_present() -> None:
    # chunk 07: runs (typed emphasis) + bulletLevels (bounded 0-4).
    # chunk 08: chartKind + categories + series, all flat siblings per R9.
    deck = _load("PresentationDeck-schema.json")
    definitions = deck["definitions"]
    props = definitions["contentBlock"]["properties"]
    for field in ("runs", "bulletLevels", "chartKind", "categories", "series"):
        assert field in props, f"{field} missing from contentBlock properties"
    assert props["bulletLevels"]["items"]["minimum"] == 0
    assert props["bulletLevels"]["items"]["maximum"] == 4
    assert props["chartKind"]["enum"] == ["bar", "line"]
    assert props["runs"]["items"] == {"$ref": "#/definitions/textRun"}
    assert props["series"]["items"] == {"$ref": "#/definitions/chartSeries"}
    assert definitions["textRun"]["required"] == ["text"]
    assert definitions["chartSeries"]["required"] == ["name", "values"]


def test_content_block_mermaid_payload_field_present() -> None:
    # chunk 11: smallest typed attachment point for Mermaid source. A single
    # string field mirrors how 'text' serves a 'text' block. No parsing, layout,
    # or rendering is added -- the description must say so plainly.
    deck = _load("PresentationDeck-schema.json")
    props = deck["definitions"]["contentBlock"]["properties"]
    assert "mermaidSource" in props
    assert props["mermaidSource"]["type"] == "string"
    description = props["mermaidSource"]["description"].lower()
    assert "does not" in description
    assert "render" in description


def test_theme_color_ref_enum_matches_theme_accent_count() -> None:
    # PresentationColorTheme-schema.json declares 8 accents (accentGrey, accentRed,
    # accentGreen, accentBlue, accentAmber, accentTeal, accentYellow, accentPurple),
    # not 9 as presentationSchema.md originally asserted -- corrected there in this
    # chunk. 3 scalars + 8 accents x 3 channels = 27.
    theme = _load("PresentationColorTheme-schema.json")
    accents = [name for name in theme["required"] if name.startswith("accent")]
    layouts = _load("PresentationSlideLayouts-schema.json")
    theme_color_ref = layouts["definitions"]["themeColorRef"]
    assert len(theme_color_ref["enum"]) == 3 + len(accents) * 3
    assert len(theme_color_ref["enum"]) == 27


def test_metadata_has_no_canvas_or_margin() -> None:
    metadata = _load("PresentationMetadata-schema.json")
    assert "canvas" not in metadata["properties"]
    assert "margin" not in metadata["properties"].get("defaults", {}).get("properties", {})
    assert "colorTheme" not in metadata["properties"].get("defaults", {}).get("properties", {})


def test_deck_has_no_canvas_key() -> None:
    for name in ("PresentationDeck-schema.json", "PresentationMetadata-schema.json"):
        schema = _load(name)
        assert "canvas" not in schema.get("properties", {})


def test_metadata_theme_and_layout_version_identity_present_and_optional() -> None:
    # chunk 09: identity/version stamp for which corporate theme and layout
    # standard a deck was authored against -- not a resolvable reference (R3
    # removed defaults.colorTheme), just recorded identity for later migration
    # tooling. Both fields SHALL be optional so older decks stay valid.
    metadata = _load("PresentationMetadata-schema.json")
    assert "themeVersion" not in metadata["required"]
    assert "layoutVersion" not in metadata["required"]
    for field in ("themeVersion", "layoutVersion"):
        block = metadata["properties"][field]
        assert block["type"] == "object"
        assert set(block["properties"]) == {"id", "version"}
        assert block["properties"]["id"]["type"] == "string"
        assert block["properties"]["version"]["type"] == "string"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
