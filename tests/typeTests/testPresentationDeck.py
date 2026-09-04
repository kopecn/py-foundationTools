import copy
import unittest
from typing import Any

from foundationTypes.presentationTypes.Presentations import (
    ChartKind,
    ContentType,
    PresentationDeck,
    ThemeColorRef,
)


def _example_deck_dict() -> dict[str, Any]:
    """A three-slide deck exercising ``text`` and ``bullets`` blocks, omitting
    every optional nested object (metadata.defaults, every block's style).

    Inlined here so the test is self-contained under tests/ -- it carries no
    dependency on a checked-in example file.
    """
    return {
        "metadata": {
            "file": {"name": "q3-review.pptx"},
            "title": "Q3 Business Review",
            "author": "Nicholas Bergantz",
            "company": "Example Corp",
            "date": "2026-08-23",
        },
        "slides": [
            {
                "number": 1,
                "id": "cover",
                "layout": "title",
                "title": "Q3 Business Review",
                "subtitle": "Engineering Organization",
                "content": [
                    {
                        "region": "footer",
                        "type": "text",
                        "text": "Confidential - Internal Use Only",
                    }
                ],
            },
            {
                "number": 2,
                "id": "highlights",
                "layout": "one-column",
                "title": "Highlights",
                "content": [
                    {
                        "region": "body",
                        "type": "bullets",
                        "items": [
                            "Shipped presentation schema linking",
                            "Closed the tier-1 gate",
                            "Zero new runtime dependencies",
                        ],
                    }
                ],
            },
            {
                "number": 3,
                "id": "roadmap",
                "layout": "two-column",
                "title": "Roadmap",
                "content": [
                    {
                        "region": "left",
                        "type": "text",
                        "text": "Near term: typed content blocks, rich text, and bullet levels.",
                    },
                    {
                        "region": "right",
                        "type": "bullets",
                        "items": [
                            "Deck versioning",
                            "Layout migration",
                            "Mermaid nucleation",
                        ],
                    },
                ],
            },
        ],
    }


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


def _metric_table_deck_dict() -> dict[str, Any]:
    """A two-slide deck exercising the tier-2 ``metric`` and ``table`` blocks,
    including a metric that omits the optional ``delta``.
    """
    return {
        "metadata": {
            "author": "Nicholas Bergantz",
            "company": "Example Corp",
            "date": "2026-08-28",
            "file": {"name": "metrics.pptx"},
            "title": "Metrics",
        },
        "slides": [
            {
                "number": 1,
                "layout": "kpi-row",
                "title": "Quarter at a glance",
                "content": [
                    {
                        "region": "kpi-left",
                        "type": "metric",
                        "value": "$4.2M",
                        "label": "Bookings",
                        "delta": "+12% QoQ",
                    },
                    {
                        "region": "kpi-right",
                        "type": "metric",
                        "value": "63",
                        "label": "NPS",
                    },
                ],
            },
            {
                "number": 2,
                "layout": "one-column",
                "title": "Pipeline by stage",
                "content": [
                    {
                        "region": "body",
                        "type": "table",
                        "headers": ["Stage", "Count", "Value"],
                        "rows": [
                            ["Discovery", "12", "$1.1M"],
                            ["Proposal", "5", "$0.8M"],
                            ["Closing", "3", "$0.6M"],
                        ],
                    }
                ],
            },
        ],
    }


def _rich_text_chart_deck_dict() -> dict[str, Any]:
    """A two-slide deck exercising the tier-2 ``runs`` / ``bulletLevels`` (chunk 07)
    and ``chart`` (chunk 08) placeholder payloads.
    """
    return {
        "metadata": {
            "author": "Nicholas Bergantz",
            "company": "Example Corp",
            "date": "2026-08-28",
            "file": {"name": "narrative.pptx"},
            "title": "Narrative",
        },
        "slides": [
            {
                "number": 1,
                "layout": "one-column",
                "title": "Where we are",
                "content": [
                    {
                        "region": "body",
                        "type": "text",
                        "runs": [
                            {"text": "Revenue is "},
                            {"text": "up 12%", "bold": True},
                            {"text": " and "},
                            {"text": "ahead of plan", "italic": True},
                            {"text": "."},
                        ],
                    },
                    {
                        "region": "aside",
                        "type": "bullets",
                        "items": ["Region EMEA", "  France", "  Germany", "Region APAC"],
                        "bulletLevels": [0, 1, 1, 0],
                    },
                ],
            },
            {
                "number": 2,
                "layout": "one-column",
                "title": "Bookings by quarter",
                "content": [
                    {
                        "region": "body",
                        "type": "chart",
                        "chartKind": "bar",
                        "categories": ["Q1", "Q2", "Q3"],
                        "series": [
                            {
                                "name": "Bookings",
                                "values": [3.1, 3.8, 4.2],
                                "color": "accentBlue.accent",
                            },
                            {"name": "Target", "values": [3.0, 3.5, 4.0]},
                        ],
                    }
                ],
            },
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


def _versioned_deck_dict() -> dict[str, Any]:
    """A minimal deck stamped with the theme/layout version identity (chunk 09)."""
    deck = _minimal_deck_dict()
    deck["metadata"]["themeVersion"] = {"id": "acme-corporate", "version": "2.1"}
    deck["metadata"]["layoutVersion"] = {"id": "acme-standard-16x9", "version": "3"}
    return deck


def _mermaid_deck_dict() -> dict[str, Any]:
    """A minimal deck exercising the tier-3 'mermaid' nucleation point (chunk 11):
    a single content block carrying raw Mermaid source text only. No parsing,
    layout, or rendering is exercised -- there is none to exercise.
    """
    deck = _minimal_deck_dict()
    deck["slides"][0]["content"] = [
        {
            "region": "body",
            "type": "mermaid",
            "mermaidSource": "graph TD\n  A[Start] --> B[End]",
        }
    ]
    return deck


class TestPresentationDeck(unittest.TestCase):
    """Contract tests for the generated PresentationDeck model."""

    def setUp(self) -> None:
        self.example_dict = _example_deck_dict()
        self.example_deck = PresentationDeck.from_dict(self.example_dict)
        self.minimal_dict = _minimal_deck_dict()
        self.full_dict = _full_dict()
        self.metric_table_dict = _metric_table_deck_dict()
        self.rich_text_chart_dict = _rich_text_chart_deck_dict()
        self.versioned_dict = _versioned_deck_dict()
        self.mermaid_dict = _mermaid_deck_dict()

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

    def test_from_dict_builds_metric_and_table_blocks(self) -> None:
        deck = PresentationDeck.from_dict(self.metric_table_dict)
        assert deck.slides[0].content is not None
        metric = deck.slides[0].content[0]
        self.assertEqual(metric.type, ContentType.METRIC)
        self.assertEqual(metric.value, "$4.2M")
        self.assertEqual(metric.label, "Bookings")
        self.assertEqual(metric.delta, "+12% QoQ")
        bare_metric = deck.slides[0].content[1]
        self.assertEqual(bare_metric.value, "63")
        self.assertIsNone(bare_metric.delta)
        assert deck.slides[1].content is not None
        table = deck.slides[1].content[0]
        self.assertEqual(table.type, ContentType.TABLE)
        self.assertEqual(table.headers, ["Stage", "Count", "Value"])
        assert table.rows is not None
        self.assertEqual(len(table.rows), 3)
        self.assertEqual(table.rows[0], ["Discovery", "12", "$1.1M"])

    def test_from_dict_builds_rich_text_bullet_levels_and_chart(self) -> None:
        deck = PresentationDeck.from_dict(self.rich_text_chart_dict)
        assert deck.slides[0].content is not None
        run_block = deck.slides[0].content[0]
        assert run_block.runs is not None
        self.assertEqual(len(run_block.runs), 5)
        self.assertEqual(run_block.runs[1].text, "up 12%")
        self.assertTrue(run_block.runs[1].bold)
        self.assertTrue(run_block.runs[3].italic)
        bullet_block = deck.slides[0].content[1]
        self.assertEqual(bullet_block.bullet_levels, [0, 1, 1, 0])
        assert deck.slides[1].content is not None
        chart = deck.slides[1].content[0]
        self.assertEqual(chart.type, ContentType.CHART)
        self.assertEqual(chart.chart_kind, ChartKind.BAR)
        self.assertEqual(chart.categories, ["Q1", "Q2", "Q3"])
        assert chart.series is not None
        self.assertEqual(chart.series[0].name, "Bookings")
        self.assertEqual(chart.series[0].values, [3.1, 3.8, 4.2])
        self.assertEqual(chart.series[0].color, ThemeColorRef.ACCENT_BLUE_ACCENT)
        self.assertIsNone(chart.series[1].color)

    def test_from_dict_builds_theme_and_layout_version_identity(self) -> None:
        deck = PresentationDeck.from_dict(self.versioned_dict)
        assert deck.metadata.theme_version is not None
        self.assertEqual(deck.metadata.theme_version.id, "acme-corporate")
        self.assertEqual(deck.metadata.theme_version.version, "2.1")
        assert deck.metadata.layout_version is not None
        self.assertEqual(deck.metadata.layout_version.id, "acme-standard-16x9")
        self.assertEqual(deck.metadata.layout_version.version, "3")

    def test_theme_and_layout_version_identity_is_optional(self) -> None:
        # Older decks with no version stamp at all must still parse.
        deck = PresentationDeck.from_dict(self.minimal_dict)
        self.assertIsNone(deck.metadata.theme_version)
        self.assertIsNone(deck.metadata.layout_version)

    def test_from_dict_builds_mermaid_block(self) -> None:
        # chunk 11: the block round-trips its raw source text and nothing else --
        # there is no parsing or rendering to assert on.
        deck = PresentationDeck.from_dict(self.mermaid_dict)
        assert deck.slides[0].content is not None
        block = deck.slides[0].content[0]
        self.assertEqual(block.type, ContentType.MERMAID)
        self.assertEqual(block.mermaid_source, "graph TD\n  A[Start] --> B[End]")

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
            "metric_table": self.metric_table_dict,
            "rich_text_chart": self.rich_text_chart_dict,
            "versioned": self.versioned_dict,
            "mermaid": self.mermaid_dict,
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
