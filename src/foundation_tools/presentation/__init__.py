"""
Presentation -- stdlib-only resolution layer for the Presentations domain.

Everything a renderer needs and cannot compute for itself: pixel <-> EMU unit
conversion, semantic color name -> RGB, layout id -> layout, region id ->
region, slide title/subtitle -> reserved region. Pure functions, no I/O, no
dependency on ``python-pptx``. Re-exports the public surface so callers import
from the package rather than the module file:
``from foundation_tools.presentation import resolve_layout``.
"""

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
    "RegionResult",
    "SlideTextBinding",
    "SlideTextResult",
    "ThemeReport",
    "contrast_ratio",
    "emu_to_px",
    "px_to_emu",
    "resolve_color",
    "resolve_layout",
    "resolve_region",
    "resolve_slide_text",
    "validate_theme",
]
