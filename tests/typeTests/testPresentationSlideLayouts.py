import copy
import unittest
from typing import Any

from foundationTypes.presentationTypes.Presentations import PresentationSlideLayouts


def _example_layouts_dict() -> dict[str, Any]:
    """The tier-1 three-layout library (title / one-column / two-column).

    Inlined here so the test is self-contained under tests/ -- it carries no
    dependency on a checked-in example file.
    """
    return {
        "defaults": {"canvasWidth": 1920, "canvasHeight": 1080, "outerMargin": 80},
        "layouts": [
            {
                "id": "title",
                "name": "Title",
                "description": "Simple title slide.",
                "regions": [
                    {
                        "id": "title",
                        "type": "title",
                        "x": 150,
                        "y": 230,
                        "width": 1620,
                        "height": 110,
                        "fontSize": 48,
                        "color": "text",
                    },
                    {
                        "id": "subtitle",
                        "type": "subtitle",
                        "x": 150,
                        "y": 360,
                        "width": 1620,
                        "height": 60,
                        "fontSize": 24,
                        "color": "mutedText",
                    },
                    {
                        "id": "footer",
                        "type": "footer",
                        "x": 150,
                        "y": 900,
                        "width": 1620,
                        "height": 50,
                        "fontSize": 16,
                        "color": "mutedText",
                    },
                ],
            },
            {
                "id": "one-column",
                "name": "One Column",
                "description": "Standard title plus full-width body.",
                "regions": [
                    {
                        "id": "title",
                        "type": "title",
                        "x": 80,
                        "y": 70,
                        "width": 1760,
                        "height": 70,
                        "fontSize": 40,
                        "color": "text",
                    },
                    {
                        "id": "body",
                        "type": "body",
                        "x": 100,
                        "y": 180,
                        "width": 1720,
                        "height": 780,
                        "color": "text",
                    },
                ],
            },
            {
                "id": "two-column",
                "name": "Two Column",
                "description": "Title plus two equal content columns.",
                "regions": [
                    {
                        "id": "title",
                        "type": "title",
                        "x": 80,
                        "y": 70,
                        "width": 1760,
                        "height": 70,
                        "fontSize": 40,
                        "color": "text",
                    },
                    {
                        "id": "left",
                        "type": "column",
                        "x": 100,
                        "y": 180,
                        "width": 820,
                        "height": 780,
                        "color": "text",
                    },
                    {
                        "id": "right",
                        "type": "column",
                        "x": 1000,
                        "y": 180,
                        "width": 820,
                        "height": 780,
                        "color": "text",
                    },
                ],
            },
        ],
    }


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
        self.example_dict = _example_layouts_dict()
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
