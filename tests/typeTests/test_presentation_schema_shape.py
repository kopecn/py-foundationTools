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


def test_content_block_type_enum_is_text_and_bullets() -> None:
    deck = _load("PresentationDeck-schema.json")
    content_block = deck["definitions"]["contentBlock"]
    assert content_block["properties"]["type"]["enum"] == ["text", "bullets"]


def test_content_block_has_no_removed_fields() -> None:
    deck = _load("PresentationDeck-schema.json")
    content_block = deck["definitions"]["contentBlock"]
    for removed in ("value", "label", "data"):
        assert removed not in content_block["properties"]


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


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
