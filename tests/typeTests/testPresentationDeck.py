import copy
import json
import unittest
from pathlib import Path
from typing import Any

from foundationTypes.presentationTypes.Presentations import PresentationDeck

EXAMPLE_DIR = Path(__file__).resolve().parents[2] / "schema" / "examples" / "Presentations"


def _load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        result: dict[str, Any] = json.load(f)
        return result


def _minimal_deck_dict() -> dict[str, Any]:
    return {
        "metadata": {
            "author": "Author",
            "company": "Company",
            "date": "2026-08-23",
            "file": {"name": "out.pptx"},
            "title": "Title",
        },
        "slides": [
            {"layout": "solo", "number": 1},
        ],
    }


def _full_dict() -> dict[str, Any]:
    """Exercises every optional nested object (Defaults, Style) so the
    camelCase wire-key check has something to assert on beyond the flat
    top-level fields.
    """
    deck = _minimal_deck_dict()
    deck["metadata"]["defaults"] = {
        "bodyFontSize": 18,
        "fontFamily": "Calibri",
        "smallFontSize": 10,
        "titleFontSize": 36,
    }
    deck["slides"][0]["content"] = [
        {
            "region": "body",
            "type": "text",
            "text": "hello",
            "style": {"align": "left", "bold": True, "color": "text", "fontSize": 14},
        }
    ]
    return deck


class TestPresentationDeck(unittest.TestCase):
    """Contract tests for the generated PresentationDeck model."""

    def setUp(self) -> None:
        self.example_dict = _load(EXAMPLE_DIR / "deck.json")
        self.example_deck = PresentationDeck.from_dict(self.example_dict)
        self.minimal_dict = _minimal_deck_dict()
        self.full_dict = _full_dict()

    def test_from_dict_builds_valid_instance_from_example(self) -> None:
        # The example deck omits every optional nested object (metadata.defaults,
        # every content block's style) -- this is the exact shape that used to
        # crash with AssertionError before fix-08 rewrote the generated dict-type
        # guard to raise TypeError, letting from_union's (TypeError, ValueError,
        # KeyError) catch correctly fall through to from_none.
        self.assertIsInstance(self.example_deck, PresentationDeck)
        self.assertEqual(self.example_deck.metadata.title, "Q3 Business Review")
        self.assertEqual(len(self.example_deck.slides), 3)
        self.assertEqual([s.number for s in self.example_deck.slides], [1, 2, 3])

    def test_from_dict_builds_valid_instance_from_minimal(self) -> None:
        deck = PresentationDeck.from_dict(self.minimal_dict)
        self.assertEqual(deck.metadata.author, "Author")
        self.assertEqual(deck.slides[0].layout, "solo")

    def test_to_dict_produces_camel_case_wire_keys(self) -> None:
        deck = PresentationDeck.from_dict(self.full_dict)
        result = deck.to_dict()
        defaults = result["metadata"]["defaults"]
        for key in ("bodyFontSize", "fontFamily", "smallFontSize", "titleFontSize"):
            self.assertIn(key, defaults)
        self.assertNotIn("body_font_size", defaults)
        self.assertNotIn("font_family", defaults)
        style = result["slides"][0]["content"][0]["style"]
        self.assertIn("fontSize", style)
        self.assertNotIn("font_size", style)

    def test_roundtrip_preserves_state(self) -> None:
        cases = {
            "example": self.example_dict,
            "minimal": self.minimal_dict,
            "full": self.full_dict,
        }
        for case_name, source_dict in cases.items():
            with self.subTest(case=case_name):
                deck = PresentationDeck.from_dict(source_dict)
                round_tripped = PresentationDeck.from_dict(deck.to_dict())
                self.assertEqual(deck.to_dict(), round_tripped.to_dict())
                self.assertEqual(deck.metadata.title, round_tripped.metadata.title)
                self.assertEqual(
                    [s.number for s in deck.slides],
                    [s.number for s in round_tripped.slides],
                )

    def test_from_dict_raises_on_missing_required_field(self) -> None:
        broken = copy.deepcopy(self.minimal_dict)
        del broken["metadata"]["author"]
        with self.assertRaises(TypeError):
            PresentationDeck.from_dict(broken)

    def test_from_dict_raises_on_missing_required_nested_object(self) -> None:
        # metadata.file is a required nested object; its absence calls
        # File.from_dict(None) directly and must raise TypeError, not
        # AssertionError (fix-08).
        broken = copy.deepcopy(self.minimal_dict)
        del broken["metadata"]["file"]
        with self.assertRaises(TypeError):
            PresentationDeck.from_dict(broken)

    def test_from_dict_raises_on_wrong_typed_field(self) -> None:
        broken = copy.deepcopy(self.minimal_dict)
        broken["slides"][0]["number"] = "not-an-int"
        with self.assertRaises(TypeError):
            PresentationDeck.from_dict(broken)


if __name__ == "__main__":
    unittest.main()
