"""
Pixel <-> EMU unit conversion for the Presentations domain (R6).

The canvas is 1920x1080 pixels over a 16:9 slide (13-1/3 x 7-1/2 in), which is
exactly 144 px/in. PowerPoint works in EMU (914400 per inch), so the mapping is
exactly 914400 / 144 = 6350 EMU per pixel -- no rounding. 1920 x 6350 = 12192000
and 1080 x 6350 = 6858000, PowerPoint's widescreen slide dimensions.

This is the single, repository-wide definition of EMU_PER_PX (R6): no other
module SHALL re-derive it.
"""

import math
from typing import Final

__all__ = ["EMU_PER_PX", "emu_to_px", "px_to_emu"]

EMU_PER_PX: Final[int] = 6350  # 914400 EMU/in / 144 px/in - exact, no rounding


def px_to_emu(px: float) -> int:
    """Convert pixels to EMU, rounding half-up for fractional coordinates."""
    return math.floor(px * EMU_PER_PX + 0.5)


def emu_to_px(emu: int) -> float:
    """Convert EMU back to pixels. Lossless for integer pixel values."""
    return emu / EMU_PER_PX
