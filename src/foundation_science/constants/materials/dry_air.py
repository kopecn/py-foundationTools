"""Dry air — thermodynamic properties.

Substance-major grouping: every property of dry air belongs here regardless of which
domain it comes from, so a future transport property (viscosity, thermal
conductivity) joins this class rather than fragmenting the substance across a
``transport`` module.

All three properties below carry ``std_uncertainty=None``. That is the honest
reading of their provenance — "approximate", "representative", "varies with
temperature" all assert that an error exists without bounding it. Marking them
``0.0`` would claim a precision none of them has.
"""

from typing import Final

from foundation_science.constants.constant import Constant, Distribution


class DryAir:
    """Properties of dry air at or near ISA sea-level conditions."""

    R: Final = Constant(
        287.058,
        unit="J/(kg·K)",
        std_uncertainty=None,
        distribution=Distribution.UNKNOWN,
        source="R_UNIVERSAL / M_air with M_air ≈ 28.965 kg/kmol; "
        "Çengel & Boles, Thermodynamics: An Engineering Approach",
    )
    """Specific gas constant for dry air. Derived from an assumed molar mass, which
    itself varies with composition — notably humidity and CO₂ fraction — so the
    value inherits an unquantified composition error."""

    CP: Final = Constant(
        1004.7,
        unit="J/(kg·K)",
        std_uncertainty=None,
        distribution=Distribution.UNKNOWN,
        source="Çengel & Boles — representative value near 288 K",
    )
    """Specific heat at constant pressure near ISA sea-level conditions (~288 K).
    Varies with temperature; not valid across a wide range."""

    GAMMA: Final = Constant(
        1.4,
        unit="1",
        std_uncertainty=None,
        distribution=Distribution.UNKNOWN,
        source="Standard diatomic-gas approximation",
    )
    """Ratio of specific heats (cp/cv) near ambient temperature. A modelling
    approximation rather than a measurement: its error is model error, and it grows
    as temperature moves away from ambient."""
