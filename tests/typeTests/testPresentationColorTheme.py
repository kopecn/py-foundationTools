import copy
import json
import unittest
from pathlib import Path
from typing import Any

from foundation_tools.presentation.theme_resolver import resolve_color
from foundationTypes.presentationTypes.Presentations import PresentationColorTheme

EXAMPLE_DIR = Path(__file__).resolve().parents[2] / "schema" / "examples" / "Presentations"
SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schema" / "schemas" / "Presentations"

_ACCENT_NAMES = (
    "accentGrey",
    "accentRed",
    "accentGreen",
    "accentBlue",
    "accentAmber",
    "accentTeal",
    "accentYellow",
    "accentPurple",
)


def _load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        result: dict[str, Any] = json.load(f)
        return result


def _minimal_color(name: str = "c") -> dict[str, Any]:
    return {"name": name, "r": 1, "g": 2, "b": 3}


def _minimal_accent() -> dict[str, Any]:
    return {
        "accent": _minimal_color("accent"),
        "background": _minimal_color("bg"),
        "text": _minimal_color("text"),
    }


def _minimal_theme_dict() -> dict[str, Any]:
    theme: dict[str, Any] = {
        "background": _minimal_color("bg"),
        "text": _minimal_color("text"),
        "mutedText": _minimal_color("muted"),
        "chartColors": [_minimal_color("chart0")],
    }
    for accent in _ACCENT_NAMES:
        theme[accent] = _minimal_accent()
    return theme


class TestPresentationColorTheme(unittest.TestCase):
    """Contract tests for the generated PresentationColorTheme model."""

    def setUp(self) -> None:
        self.example_dict = _load(EXAMPLE_DIR / "theme.json")
        self.example_theme = PresentationColorTheme.from_dict(self.example_dict)
        self.minimal_dict = _minimal_theme_dict()

    def test_from_dict_builds_valid_instance_from_example(self) -> None:
        self.assertIsInstance(self.example_theme, PresentationColorTheme)
        self.assertEqual(self.example_theme.background.name, "White")
        self.assertEqual(self.example_theme.accent_blue.accent.name, "Cobalt")

    def test_from_dict_builds_valid_instance_from_minimal(self) -> None:
        theme = PresentationColorTheme.from_dict(self.minimal_dict)
        self.assertIsInstance(theme, PresentationColorTheme)
        self.assertEqual(theme.background.r, 1)

    def test_to_dict_produces_camel_case_wire_keys(self) -> None:
        result = self.example_theme.to_dict()
        for key in ("background", "text", "mutedText", "chartColors", *_ACCENT_NAMES):
            self.assertIn(key, result)
        # snake_case must never leak onto the wire.
        self.assertNotIn("muted_text", result)
        self.assertNotIn("accent_blue", result)
        self.assertNotIn("chart_colors", result)

    def test_roundtrip_preserves_state(self) -> None:
        cases = {
            "example": self.example_dict,
            "minimal": self.minimal_dict,
        }
        for case_name, source_dict in cases.items():
            with self.subTest(case=case_name):
                theme = PresentationColorTheme.from_dict(source_dict)
                round_tripped = PresentationColorTheme.from_dict(theme.to_dict())
                self.assertEqual(theme.to_dict(), round_tripped.to_dict())
                self.assertEqual(theme.background.r, round_tripped.background.r)
                self.assertEqual(theme.background.g, round_tripped.background.g)
                self.assertEqual(theme.background.b, round_tripped.background.b)
                for accent_name in _ACCENT_NAMES:
                    attr = "accent_" + accent_name[len("accent") :].lower()
                    original_accent = getattr(theme, attr)
                    restored_accent = getattr(round_tripped, attr)
                    self.assertEqual(original_accent.accent.name, restored_accent.accent.name)

    def test_from_dict_raises_on_missing_required_field(self) -> None:
        # A missing *scalar* leaf -- background.r, itself required -- exercises
        # the from_int(None) -> TypeError path.
        broken = copy.deepcopy(self.minimal_dict)
        del broken["background"]["r"]
        with self.assertRaises(TypeError):
            PresentationColorTheme.from_dict(broken)

    def test_from_dict_raises_on_missing_top_level_object_field(self) -> None:
        # background is required, so a missing field calls
        # PresentationColor.from_dict(None) directly (no from_union involved);
        # its dict-type guard now raises TypeError instead of the pre-fix-08
        # AssertionError. See fix-08's Resolution notes.
        broken = copy.deepcopy(self.minimal_dict)
        del broken["background"]
        with self.assertRaises(TypeError):
            PresentationColorTheme.from_dict(broken)

    def test_from_dict_raises_on_wrong_typed_field(self) -> None:
        broken = copy.deepcopy(self.minimal_dict)
        broken["background"]["r"] = "not-an-int"
        with self.assertRaises(TypeError):
            PresentationColorTheme.from_dict(broken)


class TestThemeColorRefEnumCoverage(unittest.TestCase):
    """Every themeColorRef enum value must resolve against the example theme (R4)."""

    def test_every_enum_value_resolves_against_example_theme(self) -> None:
        theme = PresentationColorTheme.from_dict(_load(EXAMPLE_DIR / "theme.json"))
        layouts_schema = _load(SCHEMA_DIR / "PresentationSlideLayouts-schema.json")
        enum_values = layouts_schema["definitions"]["themeColorRef"]["enum"]
        self.assertEqual(len(enum_values), 27)
        for ref in enum_values:
            with self.subTest(ref=ref):
                result = resolve_color(theme, ref)
                self.assertTrue(result.ok, f"{ref!r} failed to resolve: {result.error}")
                self.assertIsNotNone(result.color)


if __name__ == "__main__":
    unittest.main()
