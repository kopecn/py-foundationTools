"""Tests for the stdlib-only Presentations resolution layer (chunk 03).

Contract: .claude/specs/presentationSchema.md, Resolution Layer section.
"""

from foundation_tools.presentation.layout_resolver import (
    RESERVED_REGION_IDS,
    resolve_layout,
    resolve_region,
    resolve_slide_text,
)
from foundation_tools.presentation.theme_resolver import resolve_color
from foundation_tools.presentation.units import emu_to_px, px_to_emu
from foundationTypes.presentationTypes.Presentations import (
    ContentBlock,
    ContentType,
    LayoutDefaults,
    PresentationAccent,
    PresentationColor,
    PresentationColorTheme,
    PresentationSlideLayouts,
    Region,
    Slide,
    SlideLayout,
)


def _color(name: str, r: int, g: int, b: int) -> PresentationColor:
    return PresentationColor(name=name, r=r, g=g, b=b)


def _accent(name: str) -> PresentationAccent:
    return PresentationAccent(
        accent=_color(f"{name} accent", 1, 2, 3),
        background=_color(f"{name} background", 4, 5, 6),
        text=_color(f"{name} text", 7, 8, 9),
    )


def _theme() -> PresentationColorTheme:
    return PresentationColorTheme(
        accent_amber=_accent("amber"),
        accent_blue=_accent("blue"),
        accent_green=_accent("green"),
        accent_grey=_accent("grey"),
        accent_purple=_accent("purple"),
        accent_red=_accent("red"),
        accent_teal=_accent("teal"),
        accent_yellow=_accent("yellow"),
        background=_color("bg", 255, 255, 255),
        chart_colors=[_color("chart0", 0, 0, 0)],
        muted_text=_color("muted", 100, 100, 100),
        text=_color("text", 10, 20, 30),
    )


def _layouts() -> PresentationSlideLayouts:
    title_layout = SlideLayout(
        id="title",
        name="Title",
        regions=[Region(id="title"), Region(id="subtitle")],
    )
    one_column = SlideLayout(
        id="one-column",
        name="One Column",
        regions=[Region(id="title"), Region(id="body")],
    )
    return PresentationSlideLayouts(defaults=LayoutDefaults(), layouts=[title_layout, one_column])


class TestUnits:
    def test_px_to_emu_width(self) -> None:
        assert px_to_emu(1920) == 12192000

    def test_px_to_emu_height(self) -> None:
        assert px_to_emu(1080) == 6858000

    def test_roundtrip_integers(self) -> None:
        for n in range(0, 1921):
            assert emu_to_px(px_to_emu(n)) == n


class TestResolveColor:
    def test_scalar_form(self) -> None:
        theme = _theme()
        result = resolve_color(theme, "text")
        assert result.ok
        assert result.color == theme.text

    def test_dotted_accent_form(self) -> None:
        theme = _theme()
        result = resolve_color(theme, "accentBlue.accent")
        assert result.ok
        assert result.color == theme.accent_blue.accent

    def test_dotted_accent_background_and_text_channels(self) -> None:
        theme = _theme()
        bg = resolve_color(theme, "accentGreen.background")
        text = resolve_color(theme, "accentGreen.text")
        assert bg.ok and bg.color == theme.accent_green.background
        assert text.ok and text.color == theme.accent_green.text

    def test_unknown_accent_fails(self) -> None:
        theme = _theme()
        result = resolve_color(theme, "accentMagenta.accent")
        assert not result.ok
        assert result.color is None
        assert result.error is not None
        assert "accentMagenta" in result.error

    def test_unknown_scalar_fails(self) -> None:
        theme = _theme()
        result = resolve_color(theme, "notAColor")
        assert not result.ok
        assert result.error is not None

    def test_malformed_channel_fails(self) -> None:
        theme = _theme()
        result = resolve_color(theme, "accentBlue.nope")
        assert not result.ok
        assert result.error is not None


class TestResolveLayout:
    def test_hit(self) -> None:
        layouts = _layouts()
        result = resolve_layout(layouts, "one-column")
        assert result.ok
        assert result.layout is not None
        assert result.layout.id == "one-column"

    def test_miss_lists_available_ids(self) -> None:
        layouts = _layouts()
        result = resolve_layout(layouts, "two-col")
        assert not result.ok
        assert result.layout is None
        assert result.error is not None
        assert "two-col" in result.error
        assert "title" in result.error
        assert "one-column" in result.error


class TestResolveRegion:
    def test_hit(self) -> None:
        layouts = _layouts()
        layout = resolve_layout(layouts, "title").layout
        assert layout is not None
        result = resolve_region(layout, "subtitle")
        assert result.ok
        assert result.region is not None
        assert result.region.id == "subtitle"

    def test_miss_names_region_and_layout(self) -> None:
        layouts = _layouts()
        layout = resolve_layout(layouts, "title").layout
        assert layout is not None
        result = resolve_region(layout, "footer")
        assert not result.ok
        assert result.region is None
        assert result.error is not None
        assert "footer" in result.error
        assert "title" in result.error


class TestResolveSlideText:
    """R11: Slide.title / Slide.subtitle bind to reserved region ids."""

    def _slide(
        self,
        *,
        layout: str = "title",
        title: str | None = None,
        subtitle: str | None = None,
        content: list[ContentBlock] | None = None,
    ) -> Slide:
        return Slide(
            layout=layout, number=1, title=title, subtitle=subtitle, content=content
        )

    def _layout(self, layout_id: str) -> SlideLayout:
        layout = resolve_layout(_layouts(), layout_id).layout
        assert layout is not None
        return layout

    def test_binds_title_and_subtitle_to_reserved_regions(self) -> None:
        result = resolve_slide_text(
            self._layout("title"), self._slide(title="Deck", subtitle="Q3")
        )
        assert result.ok
        assert [(b.field, b.region.id, b.text) for b in result.bindings] == [
            ("title", "title", "Deck"),
            ("subtitle", "subtitle", "Q3"),
        ]

    def test_reserved_ids_are_ordinary_regions(self) -> None:
        layout = self._layout("title")
        result = resolve_slide_text(layout, self._slide(title="Deck"))
        assert result.bindings[0].region is resolve_region(layout, "title").region

    def test_absent_fields_bind_nothing(self) -> None:
        result = resolve_slide_text(self._layout("title"), self._slide())
        assert result.ok
        assert result.bindings == ()

    def test_empty_subtitle_counts_as_absent(self) -> None:
        result = resolve_slide_text(
            self._layout("one-column"), self._slide(layout="one-column", subtitle="")
        )
        assert result.ok
        assert result.bindings == ()

    def test_missing_reserved_region_is_an_error_not_a_silent_drop(self) -> None:
        result = resolve_slide_text(
            self._layout("one-column"), self._slide(layout="one-column", subtitle="Q3")
        )
        assert not result.ok
        assert result.bindings == ()
        assert len(result.errors) == 1
        assert "subtitle" in result.errors[0]
        assert "one-column" in result.errors[0]

    def test_unused_reserved_region_is_not_an_error(self) -> None:
        result = resolve_slide_text(self._layout("title"), self._slide(title="Deck"))
        assert result.ok
        assert [b.field for b in result.bindings] == ["title"]

    def test_content_block_targeting_reserved_region_is_an_error(self) -> None:
        slide = self._slide(
            title="Deck",
            content=[ContentBlock(region="title", type=ContentType.TEXT, text="also a title")],
        )
        result = resolve_slide_text(self._layout("title"), slide)
        assert not result.ok
        assert len(result.errors) == 1
        assert "reserved region 'title'" in result.errors[0]

    def test_content_block_targeting_ordinary_region_is_fine(self) -> None:
        slide = self._slide(
            layout="one-column",
            title="Deck",
            content=[ContentBlock(region="body", type=ContentType.TEXT, text="body")],
        )
        result = resolve_slide_text(self._layout("one-column"), slide)
        assert result.ok

    def test_reserved_ids_are_defined_once(self) -> None:
        assert RESERVED_REGION_IDS == {"title": "title", "subtitle": "subtitle"}
