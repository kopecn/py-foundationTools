"""Physical constants.

SI units throughout. Exact standards are identified explicitly; engineering
properties that vary with temperature or composition are documented as
representative values. Each constant includes a brief provenance note.
"""

R_AIR = 287.058
"""J/(kg·K) — specific gas constant for dry air, derived from the universal gas
constant and the dry-air molar mass (M_air ≈ 28.965 kg/kmol). Standard
engineering value (e.g. Çengel & Boles, *Thermodynamics: An Engineering
Approach*)."""

CP_AIR = 1004.7
"""J/(kg·K) — approximate specific heat at constant pressure for dry air near
ISA sea-level conditions (~288 K). This property varies slightly with
temperature. Representative engineering handbook value (e.g. Çengel & Boles)."""

GAMMA_AIR = 1.4
"""dimensionless — approximate ratio of specific heats (cp/cv) for dry air
near ambient temperatures. Temperature-dependent; 1.4 is the standard
engineering approximation for diatomic gases."""

T_SL = 288.15
"""K — ISA sea-level standard temperature. Exact value defined by the
International Standard Atmosphere (ICAO Doc 7488 / ISO 2533)."""

P_SL = 101325.0
"""Pa — ISA sea-level standard pressure. Exact value defined by the
International Standard Atmosphere (ICAO Doc 7488 / ISO 2533)."""

RHO_SL = 1.225
"""kg/m³ — ISA sea-level standard air density corresponding to the standard
sea-level pressure and temperature (ICAO Doc 7488 / ISO 2533)."""

G0 = 9.80665
"""m/s² — standard acceleration due to gravity. Exact value defined by
international convention."""

LHV_JET_A1 = 43.0e6
"""J/kg — representative lower heating value (LHV) of Jet A-1 fuel referenced
to standard conditions (~298.15 K). Typical engineering value; actual fuel
properties vary slightly with composition (ASTM D1655 / aerospace fuel
handbooks)."""

R_UNIVERSAL = 8.314462618
"""J/(mol·K) — universal (molar) gas constant. CODATA recommended value."""

FAR_STOICH_JET_A = 0.0680
"""dimensionless — representative stoichiometric fuel-air mass ratio for a
Jet-A hydrocarbon surrogate (approximately CH₁.₉₃) undergoing complete
combustion. Actual stoichiometric ratio varies slightly with fuel
composition."""
