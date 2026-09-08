"""
Theme resolution: semantic color name -> RGB (R4).

Pure, stdlib-only, no I/O. A deck never carries a literal color -- it names a
``themeColorRef`` address (``background``, ``accentBlue.accent``, ...) and this
module resolves that address against an already-parsed ``PresentationColorTheme``.

An unresolvable reference is an expected authoring error, not an exceptional
condition, so resolution reports failure through a result object rather than
raising (the repository's error convention, see ``CLITransactResult``). The
``themeColorRef`` schema enum already constrains valid input at validation time;
the checks here are defence in depth, not the primary gate.
"""

import re
from dataclasses import dataclass, fields

from foundationTypes.presentationTypes.Presentations import (
    PresentationAccent,
    PresentationColor,
    PresentationColorTheme,
)

__all__ = [
    "ColorResult",
    "ContrastPairing",
    "ThemeReport",
    "contrast_ratio",
    "resolve_color",
    "validate_theme",
]

_SCALAR_ATTRS = {
    "background": "background",
    "text": "text",
    "mutedText": "muted_text",
}
_ACCENT_CHANNELS = ("accent", "background", "text")
_CAMEL_BOUNDARY = re.compile(r"(?<!^)(?=[A-Z])")


@dataclass(frozen=True)
class ColorResult:
    """Result of resolving a ``themeColorRef`` address against a theme."""

    color: PresentationColor | None
    error: str | None

    @property
    def ok(self) -> bool:
        return self.error is None


def _accent_attr_name(accent_name: str) -> str:
    """``accentBlue`` -> ``accent_blue`` (matches the generated field names)."""
    return _CAMEL_BOUNDARY.sub("_", accent_name).lower()


def resolve_color(theme: PresentationColorTheme, ref: str) -> ColorResult:
    """
    Resolve a ``themeColorRef`` address to a concrete color.

    Two address forms: a bare scalar (``background``, ``text``, ``mutedText``)
    reads a top-level theme property; a dotted form (``accentBlue.accent``) reads
    a channel of an accent. Anything else is a failure result.
    """
    if "." not in ref:
        attr = _SCALAR_ATTRS.get(ref)
        if attr is None:
            return ColorResult(
                color=None,
                error=(
                    f"unknown color reference '{ref}'; expected one of "
                    f"{', '.join(sorted(_SCALAR_ATTRS))} or '<accent>.<channel>'"
                ),
            )
        return ColorResult(color=getattr(theme, attr), error=None)

    accent_name, _, channel = ref.partition(".")
    if channel not in _ACCENT_CHANNELS:
        return ColorResult(
            color=None,
            error=(
                f"unknown color channel '{channel}' in '{ref}'; "
                f"expected one of {', '.join(_ACCENT_CHANNELS)}"
            ),
        )

    accent_attr = _accent_attr_name(accent_name)
    accent: PresentationAccent | None = getattr(theme, accent_attr, None)
    if not isinstance(accent, PresentationAccent):
        return ColorResult(color=None, error=f"unknown accent '{accent_name}' in '{ref}'")

    return ColorResult(color=getattr(accent, channel), error=None)


# --- Contrast checking (R4 / WCAG 2.x relative luminance) ------------------
#
# Opacity is intentionally ignored: PresentationColor.opacity exists in the
# schema, but python-pptx exposes no public transparency API, so a contrast
# number computed against it would describe an appearance the renderer cannot
# produce.

_AA_NORMAL_TEXT_THRESHOLD = 4.5
_AA_LARGE_TEXT_THRESHOLD = 3.0

_ContrastStatus = str  # "ok" | "low" | "fail"


def _channel(c: int) -> float:
    s = c / 255.0
    return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4


def _luminance(color: PresentationColor) -> float:
    return 0.2126 * _channel(color.r) + 0.7152 * _channel(color.g) + 0.0722 * _channel(color.b)


def contrast_ratio(fg: PresentationColor, bg: PresentationColor) -> float:
    """WCAG 2.x relative-luminance contrast ratio. Symmetric; ranges 1.0-21.0."""
    a, b = _luminance(fg), _luminance(bg)
    lighter, darker = max(a, b), min(a, b)
    return (lighter + 0.05) / (darker + 0.05)


def _classify(ratio: float) -> _ContrastStatus:
    # Presentation text is large and viewed at distance; report against the
    # normal-text AA threshold (4.5) but classify rather than fail outright.
    if ratio >= _AA_NORMAL_TEXT_THRESHOLD:
        return "ok"
    if ratio >= _AA_LARGE_TEXT_THRESHOLD:
        return "low"
    return "fail"


def _snake_to_camel(name: str) -> str:
    """``accent_blue`` -> ``accentBlue`` (matches the theme's own property names)."""
    head, *rest = name.split("_")
    return head + "".join(word.capitalize() for word in rest)


@dataclass(frozen=True)
class ContrastPairing:
    """One text-on-background pairing the theme asserts, and its contrast verdict."""

    name: str
    ratio: float
    status: _ContrastStatus


@dataclass(frozen=True)
class ThemeReport:
    """Every text-on-background pairing a theme declares, each classified."""

    pairings: list[ContrastPairing]


def validate_theme(theme: PresentationColorTheme) -> ThemeReport:
    """
    Report contrast for exactly the pairings the theme declares: ``text`` on
    ``background``, ``mutedText`` on ``background``, and each accent's ``text``
    on that same accent's ``background``. Never raises and never blocks a
    render -- an illegible theme is a decision the author is allowed to make;
    this reports it rather than preventing it.

    Accents are discovered generically from the theme's own dataclass fields
    (rather than a hardcoded name list), so adding an accent to the theme is
    picked up here automatically, per the R4 invariant.
    """
    pairings: list[ContrastPairing] = []

    def add(name: str, fg: PresentationColor, bg: PresentationColor) -> None:
        ratio = contrast_ratio(fg, bg)
        pairings.append(ContrastPairing(name=name, ratio=ratio, status=_classify(ratio)))

    add("text", theme.text, theme.background)
    add("mutedText", theme.muted_text, theme.background)

    for field in fields(theme):
        value = getattr(theme, field.name)
        if isinstance(value, PresentationAccent):
            add(f"{_snake_to_camel(field.name)}.text", value.text, value.background)

    return ThemeReport(pairings=pairings)
