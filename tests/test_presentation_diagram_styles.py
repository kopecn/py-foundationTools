"""Tests for semantic diagram styles on the 'mermaid' block (chunk 05).

Contract: .claude/specs/presentationSchema.md R19. A typed diagram-style object
expresses diagram colors as semantic theme references -- the same enumerated color
addresses PresentationSlideLayouts-schema.json#/definitions/themeColorRef declares
for R4 -- never CSS/hex literals, plus a bounded map from a custom node-class name to
those semantic roles, plus a ``themeBinding`` flag (``themed`` implied by absence |
``fixed`` explicit opt-out). All fields are additive, optional, and default-less
(``themeBinding`` absence means "themed", documented rather than declared, to avoid a
second R12 semver bump).
"""

import json
import re
from pathlib import Path

from foundationTypes.presentationTypes.Presentations import (
    ContentBlock,
    ContentType,
    DiagramClassRole,
    DiagramStyle,
    ThemeBinding,
    ThemeColorRef,
)

SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schema" / "schemas" / "Presentations"


def test_diagram_style_semantic_refs_roundtrip() -> None:
    style = DiagramStyle(
        background=ThemeColorRef.BACKGROUND,
        primary_fill=ThemeColorRef.ACCENT_BLUE_BACKGROUND,
        secondary_fill=ThemeColorRef.ACCENT_TEAL_BACKGROUND,
        tertiary_fill=ThemeColorRef.ACCENT_GREY_BACKGROUND,
        border=ThemeColorRef.ACCENT_GREY_ACCENT,
        text=ThemeColorRef.TEXT,
        line=ThemeColorRef.MUTED_TEXT,
        error=ThemeColorRef.ACCENT_RED_ACCENT,
        success=ThemeColorRef.ACCENT_GREEN_ACCENT,
    )
    block = ContentBlock(
        region="diagram",
        type=ContentType.MERMAID,
        mermaid_source="graph TD;",
        diagram_style=style,
    )

    round_tripped = ContentBlock.from_dict(block.to_dict())

    assert round_tripped == block
    assert round_tripped.diagram_style == style
    assert round_tripped.diagram_style is not None
    assert round_tripped.diagram_style.background == ThemeColorRef.BACKGROUND
    assert round_tripped.diagram_style.error == ThemeColorRef.ACCENT_RED_ACCENT
    assert round_tripped.diagram_style.success == ThemeColorRef.ACCENT_GREEN_ACCENT


def test_class_role_map_roundtrip() -> None:
    style = DiagramStyle(
        class_roles={
            "risk": DiagramClassRole(
                fill=ThemeColorRef.ACCENT_RED_BACKGROUND,
                border=ThemeColorRef.ACCENT_RED_ACCENT,
                text=ThemeColorRef.ACCENT_RED_TEXT,
            ),
            "healthy": DiagramClassRole(
                fill=ThemeColorRef.ACCENT_GREEN_BACKGROUND,
                border=ThemeColorRef.ACCENT_GREEN_ACCENT,
                text=ThemeColorRef.ACCENT_GREEN_TEXT,
            ),
        }
    )
    block = ContentBlock(
        region="diagram",
        type=ContentType.MERMAID,
        mermaid_source="graph TD; A-->B;",
        diagram_style=style,
    )

    round_tripped = ContentBlock.from_dict(block.to_dict())

    assert round_tripped == block
    assert round_tripped.diagram_style is not None
    class_roles = round_tripped.diagram_style.class_roles
    assert class_roles is not None
    assert class_roles["risk"].fill == ThemeColorRef.ACCENT_RED_BACKGROUND
    assert class_roles["risk"].border == ThemeColorRef.ACCENT_RED_ACCENT
    assert class_roles["risk"].text == ThemeColorRef.ACCENT_RED_TEXT
    assert class_roles["healthy"].fill == ThemeColorRef.ACCENT_GREEN_BACKGROUND


def test_theme_binding_fixed_roundtrip() -> None:
    style = DiagramStyle(theme_binding=ThemeBinding.FIXED)
    block = ContentBlock(
        region="diagram",
        type=ContentType.MERMAID,
        mermaid_source="graph TD;",
        diagram_style=style,
    )

    round_tripped = ContentBlock.from_dict(block.to_dict())

    assert round_tripped == block
    assert round_tripped.diagram_style is not None
    assert round_tripped.diagram_style.theme_binding == ThemeBinding.FIXED

    # Absence means "themed" -- documented in the schema description, not a
    # declared JSON Schema default (would be a second R12 semver bump).
    themed_by_absence = DiagramStyle()
    round_tripped_absent = DiagramStyle.from_dict(themed_by_absence.to_dict())
    assert round_tripped_absent.theme_binding is None


def test_diagram_refs_use_color_enumeration() -> None:
    # R19's one normative SHALL: diagram-style color values are semantic theme
    # references ($ref'ing R4's themeColorRef enum), never hex/CSS strings.
    deck_schema = json.loads(
        (SCHEMA_DIR / "PresentationDeck-schema.json").read_text(encoding="utf-8")
    )
    diagram_style = deck_schema["definitions"]["diagramStyle"]
    color_role_fields = [
        "background",
        "primaryFill",
        "secondaryFill",
        "tertiaryFill",
        "border",
        "text",
        "line",
        "error",
        "success",
    ]
    theme_ref_pointer = "PresentationSlideLayouts-schema.json#/definitions/themeColorRef"
    for field in color_role_fields:
        prop = diagram_style["properties"][field]
        assert prop["$ref"] == theme_ref_pointer, field
        assert "enum" not in prop
        assert "pattern" not in prop

    diagram_class_role = deck_schema["definitions"]["diagramClassRole"]
    for field in ["fill", "border", "text"]:
        prop = diagram_class_role["properties"][field]
        assert prop["$ref"] == theme_ref_pointer, field

    # No hex/CSS literal ever appears as a diagram-style color default or example.
    # (The only "#" in either definition is the JSON-pointer fragment inside the
    # legitimate themeColorRef $ref, asserted above -- not a hex color.)
    hex_color_pattern = re.compile(r"#[0-9a-fA-F]{3,8}\b")
    assert hex_color_pattern.search(json.dumps(diagram_style)) is None
    assert hex_color_pattern.search(json.dumps(diagram_class_role)) is None


def test_existing_mermaid_block_still_valid() -> None:
    block = ContentBlock(region="diagram", type=ContentType.MERMAID, mermaid_source="graph TD;")

    round_tripped = ContentBlock.from_dict(block.to_dict())

    assert round_tripped == block
    assert round_tripped.diagram_style is None
