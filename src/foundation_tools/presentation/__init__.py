"""
Presentation -- stdlib-only resolution layer for the Presentations domain.

Everything a renderer needs and cannot compute for itself: pixel <-> EMU unit
conversion, semantic color name -> RGB, layout id -> layout, region id ->
region. Pure functions, no I/O, no dependency on ``python-pptx``. Re-exports
the public surface so callers import from the package rather than the module
file: ``from foundation_tools.presentation import resolve_layout``.
"""

from foundation_tools.presentation.layout_resolver import (
    LayoutResult,
    RegionResult,
    resolve_layout,
    resolve_region,
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
    "ColorResult",
    "ContrastPairing",
    "LayoutResult",
    "RegionResult",
    "ThemeReport",
    "contrast_ratio",
    "emu_to_px",
    "px_to_emu",
    "resolve_color",
    "resolve_layout",
    "resolve_region",
    "validate_theme",
]
