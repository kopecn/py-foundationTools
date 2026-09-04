"""
Presentation -- stdlib-only resolution layer for the Presentations domain.

Everything a renderer needs and cannot compute for itself: pixel <-> EMU unit
conversion, semantic color name -> RGB, layout id -> layout, region id ->
region, slide title/subtitle -> reserved region, and an explicit-mapping
migration of a deck's layout/region/color references to a newer corporate
standard. Pure functions, no I/O, no dependency on ``python-pptx``. Re-exports
the public surface so callers import from the package rather than the module
file: ``from foundation_tools.presentation import resolve_layout``.
"""

from foundation_tools.presentation.image_fit import fit_into_box
from foundation_tools.presentation.layout_resolver import (
    RESERVED_REGION_IDS,
    LayoutResult,
    RegionResult,
    SlideTextBinding,
    SlideTextResult,
    resolve_layout,
    resolve_region,
    resolve_slide_text,
)
from foundation_tools.presentation.migration import (
    MigrationMapping,
    MigrationResult,
    UnplacedContent,
    migrate_deck,
)
from foundation_tools.presentation.theme_resolver import (
    ColorResult,
    ContrastPairing,
    ThemeReport,
    contrast_ratio,
    resolve_color,
    validate_theme,
)
from foundation_tools.presentation.units import EMU_PER_PX, emu_to_px, px_to_emu

__all__ = [
    "EMU_PER_PX",
    "RESERVED_REGION_IDS",
    "ColorResult",
    "ContrastPairing",
    "LayoutResult",
    "MigrationMapping",
    "MigrationResult",
    "RegionResult",
    "SlideTextBinding",
    "SlideTextResult",
    "ThemeReport",
    "UnplacedContent",
    "contrast_ratio",
    "emu_to_px",
    "fit_into_box",
    "migrate_deck",
    "px_to_emu",
    "resolve_color",
    "resolve_layout",
    "resolve_region",
    "resolve_slide_text",
    "validate_theme",
]
