"""Universal physical constants.

Constants with no associated substance and no reference state. Flat module-level
names rather than a namespace class: there is exactly one universal namespace, so
there is nothing to disambiguate against.

Note that a defined convention tied to a particular body or reference condition is
*not* universal — standard gravity lives in ``standards.isa``, not here.
"""

from typing import Final

from foundation_science.constants.constant import Constant, Distribution

R_UNIVERSAL: Final = Constant(
    8.31446261815324,
    unit="J/(mol·K)",
    std_uncertainty=0.0,
    distribution=Distribution.EXACT,
    source="SI 2019 redefinition — exact as N_A·k_B, both defined exactly",
)
"""Universal (molar) gas constant. Exact since the 2019 SI redefinition fixed both
the Avogadro constant and the Boltzmann constant; the full-precision value is
stored because a truncated literal would carry a rounding error that
``Distribution.EXACT`` claims does not exist."""
