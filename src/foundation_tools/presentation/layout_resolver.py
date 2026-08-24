"""
Layout resolution: layout id -> layout, region id -> region (R3).

Pure, stdlib-only, no I/O. An unknown layout or region id is an expected
authoring error (a typo in a deck), not an exceptional condition, so resolution
reports failure through a result object rather than raising -- the repository's
error convention, see ``CLITransactResult``. A failure message names both the bad
id and what was available, since that message is the whole user experience of a
typo.
"""

from dataclasses import dataclass

from foundationTypes.presentationTypes.Presentations import (
    PresentationSlideLayouts,
    Region,
    SlideLayout,
)

__all__ = ["LayoutResult", "RegionResult", "resolve_layout", "resolve_region"]


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
