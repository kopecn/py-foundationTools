"""
Layout resolution: layout id -> layout, region id -> region (R3), slide title and
subtitle -> their reserved regions (R11).

Pure, stdlib-only, no I/O. An unknown layout or region id is an expected
authoring error (a typo in a deck), not an exceptional condition, so resolution
reports failure through a result object rather than raising -- the repository's
error convention, see ``CLITransactResult``. A failure message names both the bad
id and what was available, since that message is the whole user experience of a
typo.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final

from foundationTypes.presentationTypes.Presentations import (
    PresentationSlideLayouts,
    Region,
    Slide,
    SlideLayout,
)

__all__ = [
    "RESERVED_REGION_IDS",
    "LayoutResult",
    "RegionResult",
    "SlideTextBinding",
    "SlideTextResult",
    "resolve_layout",
    "resolve_region",
    "resolve_slide_text",
]


@dataclass(frozen=True)
class LayoutResult:
    """Result of resolving a layout id against a layout library."""

    layout: SlideLayout | None
    error: str | None

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass(frozen=True)
class RegionResult:
    """Result of resolving a region id against a single layout."""

    region: Region | None
    error: str | None

    @property
    def ok(self) -> bool:
        return self.error is None


def resolve_layout(layouts: PresentationSlideLayouts, layout_id: str) -> LayoutResult:
    """Find the layout with the given id in the library, or a failure naming it."""
    for layout in layouts.layouts:
        if layout.id == layout_id:
            return LayoutResult(layout=layout, error=None)
    available = ", ".join(layout.id for layout in layouts.layouts)
    return LayoutResult(
        layout=None,
        error=f"unknown layout '{layout_id}'; available: {available}",
    )


def resolve_region(layout: SlideLayout, region_id: str) -> RegionResult:
    """Find the region with the given id in the layout, or a failure naming it."""
    for region in layout.regions:
        if region.id == region_id:
            return RegionResult(region=region, error=None)
    available = ", ".join(region.id for region in layout.regions)
    return RegionResult(
        region=None,
        error=f"unknown region '{region_id}' in layout '{layout.id}'; available: {available}",
    )


RESERVED_REGION_IDS: Final[Mapping[str, str]] = MappingProxyType(
    {
        "title": "title",
        "subtitle": "subtitle",
    }
)
"""Slide text field -> reserved region id it binds to (R11).

The single definition of the binding; no consumer SHALL re-derive these ids.
"""


@dataclass(frozen=True)
class SlideTextBinding:
    """One resolved slide text field placed into its reserved region."""

    field: str
    """The ``Slide`` field the text came from: ``title`` or ``subtitle``."""

    region: Region
    """The reserved region the text renders into."""

    text: str
    """The text to render."""


@dataclass(frozen=True)
class SlideTextResult:
    """Result of binding a slide's title and subtitle to its layout (R11)."""

    bindings: tuple[SlideTextBinding, ...]
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def resolve_slide_text(layout: SlideLayout, slide: Slide) -> SlideTextResult:
    """Bind ``slide.title`` / ``slide.subtitle`` to the reserved regions of R11.

    Reserved regions are ordinary regions -- they carry the same geometry, color,
    font, and overflow as any other and resolve through the same cascade. Only
    which text fills them is special.

    Reports, never raises, per the module's error convention:

    - a slide field with text but no matching region is an authoring error, so
      the text is never silently dropped;
    - a reserved region with no slide text simply yields no binding, since an
      empty region is a layout affordance;
    - a content block targeting a reserved region id is an authoring error --
      one region, one source of text.

    A field that is ``None`` or empty counts as absent: it carries no text that
    could be dropped, and the schema's ``subtitle`` default is the empty string.
    """
    bindings: list[SlideTextBinding] = []
    errors: list[str] = []
    fields: tuple[tuple[str, str | None], ...] = (
        ("title", slide.title),
        ("subtitle", slide.subtitle),
    )

    for field, text in fields:
        if not text:
            continue
        region_id = RESERVED_REGION_IDS[field]
        result = resolve_region(layout, region_id)
        if result.region is None:
            available = ", ".join(region.id for region in layout.regions)
            errors.append(
                f"slide {slide.number} sets '{field}' but layout '{layout.id}' has no "
                f"reserved region '{region_id}'; available: {available}"
            )
            continue
        bindings.append(SlideTextBinding(field=field, region=result.region, text=text))

    reserved = set(RESERVED_REGION_IDS.values())
    for block in slide.content or []:
        if block.region in reserved:
            errors.append(
                f"slide {slide.number} has a content block targeting reserved region "
                f"'{block.region}'; use the slide's own '{block.region}' field instead"
            )

    return SlideTextResult(bindings=tuple(bindings), errors=tuple(errors))
