"""Tests for WCAG contrast checking on a PresentationColorTheme (chunk 04).

Contract: .claude/specs/presentationSchema.md, Resolution Layer section.
"""

from foundation_tools.presentation.theme_resolver import contrast_ratio, validate_theme
from foundationTypes.presentationTypes.Presentations import (
    PresentationAccent,
    PresentationColor,
    PresentationColorTheme,
)

BLACK = PresentationColor(name="Black", r=0, g=0, b=0)
WHITE = PresentationColor(name="White", r=255, g=255, b=255)
MID_GREY = PresentationColor(name="Mid Grey", r=128, g=128, b=128)


def _accent(accent: PresentationColor, background: PresentationColor) -> PresentationAccent:
    return PresentationAccent(accent=accent, background=background, text=WHITE)


def _theme(
    text: PresentationColor = BLACK,
    background: PresentationColor = WHITE,
    muted_text: PresentationColor = MID_GREY,
) -> PresentationColorTheme:
    grey_accent = _accent(MID_GREY, WHITE)
    return PresentationColorTheme(
        accent_amber=grey_accent,
        accent_blue=grey_accent,
        accent_green=grey_accent,
        accent_grey=grey_accent,
        accent_purple=grey_accent,
        accent_red=grey_accent,
        accent_teal=grey_accent,
        accent_yellow=grey_accent,
        background=background,
        chart_colors=[BLACK],
        muted_text=muted_text,
        text=text,
    )


class TestContrastRatio:
    def test_black_on_white_is_21(self) -> None:
        assert abs(contrast_ratio(BLACK, WHITE) - 21.0) < 1e-9

    def test_symmetric(self) -> None:
        assert contrast_ratio(BLACK, WHITE) == contrast_ratio(WHITE, BLACK)

    def test_identical_colors_give_1(self) -> None:
        assert abs(contrast_ratio(MID_GREY, MID_GREY) - 1.0) < 1e-9
        assert abs(contrast_ratio(BLACK, BLACK) - 1.0) < 1e-9
        assert abs(contrast_ratio(WHITE, WHITE) - 1.0) < 1e-9


def test_known_mid_grey_pairing_value() -> None:
    """Hand-computed WCAG relative luminance for #808080 vs white."""

    def channel(c: int) -> float:
        s = c / 255.0
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4

    luminance = 0.2126 * channel(128) + 0.7152 * channel(128) + 0.0722 * channel(128)
    expected = (1.0 + 0.05) / (luminance + 0.05)
    assert abs(contrast_ratio(MID_GREY, WHITE) - expected) < 1e-9


class TestValidateTheme:
    def test_checks_exactly_2_plus_accents_pairings(self) -> None:
        theme = _theme()
        report = validate_theme(theme)
        accent_count = 8
        assert len(report.pairings) == 2 + accent_count

    def test_never_raises_and_reports_fail_for_illegible_theme(self) -> None:
        near_white = PresentationColor(name="Near White", r=250, g=250, b=250)
        theme = _theme(text=near_white, background=WHITE, muted_text=near_white)
        report = validate_theme(theme)
        text_pairing = next(p for p in report.pairings if p.name == "text")
        assert text_pairing.status == "fail"

    def test_ok_pairing_classified_ok(self) -> None:
        theme = _theme()
        report = validate_theme(theme)
        text_pairing = next(p for p in report.pairings if p.name == "text")
        assert text_pairing.status == "ok"

    def test_never_raises_even_when_every_pairing_fails(self) -> None:
        same = PresentationColor(name="Same", r=100, g=100, b=100)
        theme = _theme(text=same, background=same, muted_text=same)
        report = validate_theme(theme)
        assert all(p.status == "fail" for p in report.pairings)
