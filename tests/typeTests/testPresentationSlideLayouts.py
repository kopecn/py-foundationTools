import copy
import json
import unittest
from pathlib import Path
from typing import Any

from foundationTypes.presentationTypes.Presentations import PresentationSlideLayouts

EXAMPLE_DIR = Path(__file__).resolve().parents[2] / "schema" / "examples" / "Presentations"


def _load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        result: dict[str, Any] = json.load(f)
        return result


def _minimal_layouts_dict() -> dict[str, Any]:
    return {
        "defaults": {"canvasWidth": 1920, "canvasHeight": 1080, "outerMargin": 80},
        "layouts": [
            {
                "id": "solo",
                "name": "Solo",
                "regions": [{"id": "body", "type": "body"}],
            }
        ],
    }


class TestPresentationSlideLayouts(unittest.TestCase):
    """Contract tests for the generated PresentationSlideLayouts model."""

    def setUp(self) -> None:
        self.example_dict = _load(EXAMPLE_DIR / "layouts.json")
        self.example_layouts = PresentationSlideLayouts.from_dict(self.example_dict)
        self.minimal_dict = _minimal_layouts_dict()

    def test_from_dict_builds_valid_instance_from_example(self) -> None:
        self.assertIsInstance(self.example_layouts, PresentationSlideLayouts)
        layout_ids = [layout.id for layout in self.example_layouts.layouts]
        self.assertEqual(sorted(layout_ids), ["one-column", "title", "two-column"])

    def test_from_dict_builds_valid_instance_from_minimal(self) -> None:
        layouts = PresentationSlideLayouts.from_dict(self.minimal_dict)
        self.assertEqual(layouts.layouts[0].id, "solo")

    def test_to_dict_produces_camel_case_wire_keys(self) -> None:
        result = self.example_layouts.to_dict()
        self.assertIn("defaults", result)
        self.assertIn("layouts", result)
        self.assertIn("canvasWidth", result["defaults"])
        self.assertIn("canvasHeight", result["defaults"])
        self.assertIn("outerMargin", result["defaults"])
        self.assertNotIn("canvas_width", result["defaults"])
        title_layout = next(layer for layer in result["layouts"] if layer["id"] == "title")
        subtitle_region = next(r for r in title_layout["regions"] if r["id"] == "subtitle")
        # fontSize is camelCase on the wire (region.font_size internally).
        self.assertIn("fontSize", subtitle_region)

    def test_roundtrip_preserves_state(self) -> None:
        cases = {
            "example": self.example_dict,
            "minimal": self.minimal_dict,
        }
        for case_name, source_dict in cases.items():
            with self.subTest(case=case_name):
                layouts = PresentationSlideLayouts.from_dict(source_dict)
                round_tripped = PresentationSlideLayouts.from_dict(layouts.to_dict())
                self.assertEqual(layouts.to_dict(), round_tripped.to_dict())
                self.assertEqual(
                    [layer.id for layer in layouts.layouts],
                    [layer.id for layer in round_tripped.layouts],
                )

    def test_from_dict_raises_on_missing_required_field(self) -> None:
        broken = copy.deepcopy(self.minimal_dict)
        del broken["layouts"][0]["regions"][0]["id"]
        with self.assertRaises(TypeError):
            PresentationSlideLayouts.from_dict(broken)

    def test_from_dict_raises_on_wrong_typed_field(self) -> None:
        broken = copy.deepcopy(self.minimal_dict)
        broken["layouts"][0]["regions"][0]["id"] = 42
        with self.assertRaises(TypeError):
            PresentationSlideLayouts.from_dict(broken)

    def test_from_dict_raises_on_missing_regions(self) -> None:
        broken = copy.deepcopy(self.minimal_dict)
        del broken["layouts"][0]["regions"]
        with self.assertRaises(TypeError):
            PresentationSlideLayouts.from_dict(broken)


if __name__ == "__main__":
    unittest.main()
