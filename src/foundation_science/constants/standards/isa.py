"""International Standard Atmosphere reference conditions (ICAO Doc 7488 / ISO 2533).

These are defined conventions, not measurements: the standard fixes them by fiat,
so they are exact within its own frame of reference. That is a different claim from
"measured with negligible error" — using ISA sea level as a stand-in for actual
atmospheric conditions carries a modelling error this package does not describe.

The ``_SL`` suffix is retained deliberately. Unlike the ``_AIR`` suffixes it
replaced, it is not hand-rolled namespacing: the standard defines conditions at many
altitudes, so "sea level" is genuine information about which one this is.
"""

from typing import Final

from foundation_science.constants.constant import Constant, Distribution


class ISA:
    """Sea-level reference conditions of the International Standard Atmosphere."""

    T_SL: Final = Constant(
        288.15,
        unit="K",
        std_uncertainty=0.0,
        distribution=Distribution.EXACT,
        source="ICAO Doc 7488 / ISO 2533 — defined",
    )
    """Sea-level standard temperature. Exact by definition of the standard."""

    P_SL: Final = Constant(
        101325.0,
        unit="Pa",
        std_uncertainty=0.0,
        distribution=Distribution.EXACT,
        source="ICAO Doc 7488 / ISO 2533 — defined",
    )
    """Sea-level standard pressure. Exact by definition of the standard."""

    RHO_SL: Final = Constant(
        1.225,
        unit="kg/m³",
        std_uncertainty=0.0,
        distribution=Distribution.EXACT,
        source="ICAO Doc 7488 / ISO 2533 — stated by the standard",
    )
    """Sea-level standard air density, consistent with the standard's sea-level
    pressure and temperature. Stated directly by ISO 2533 rather than left to be
    derived, so it is exact in the same sense they are."""

    G0: Final = Constant(
        9.80665,
        unit="m/s²",
        std_uncertainty=0.0,
        distribution=Distribution.EXACT,
        source="Standard acceleration of gravity — defined by international convention",
    )
    """Standard acceleration due to gravity. A defined convention rather than a
    universal constant, which is why it belongs to this reference state and not to
    ``universal``; local gravitational acceleration differs from it measurably."""
