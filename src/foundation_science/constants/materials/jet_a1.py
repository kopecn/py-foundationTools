"""Jet A-1 aviation turbine fuel — combustion properties.

Both properties are composition-dependent and land as ``UNKNOWN``. Jet A-1 is a
specification, not a single substance: ASTM D1655 constrains properties like the net
heat of combustion with a *minimum*, not a symmetric tolerance band, so a ``±a``
half-width cannot be read off the standard directly.

Once a fuel-spec band is confirmed for a given application, convert the affected
constant to ``Constant.from_half_width`` rather than inventing a symmetric band here.
"""

from typing import Final

from foundation_science.constants.constant import Constant, Distribution


class JetA1:
    """Combustion properties of Jet A-1 fuel."""

    LHV: Final = Constant(
        43.0e6,
        unit="J/kg",
        std_uncertainty=None,
        distribution=Distribution.UNKNOWN,
        source="Representative value referenced to ~298.15 K; ASTM D1655 specifies a "
        "minimum net heat of combustion rather than a band",
    )
    """Lower heating value (net heat of combustion). Actual fuel varies with
    composition and batch; the specification constrains this from below only, so no
    symmetric uncertainty band is available from the standard."""

    FAR_STOICH: Final = Constant(
        0.0680,
        unit="1",
        std_uncertainty=None,
        distribution=Distribution.UNKNOWN,
        source="Complete combustion of a CH₁.₉₃ hydrocarbon surrogate",
    )
    """Stoichiometric fuel-air mass ratio. Computed from a surrogate hydrocarbon
    formula, so it carries the surrogate's composition error."""
