---
spec: PhysicalConstants
scope: project
status: implemented
applies_to: src/foundation_science/constants/
last_updated: 2026-08-15
semver: 0.1.0
author: Nicholas Bergantz
---

# Physical Constants Specification

Defines the contract for `foundation_science.constants`: how a physical constant is
declared, how its uncertainty is recorded, and how constants are grouped.

## Purpose

A physical constant is a float first and a metrological object second. It must
survive arithmetic at native speed and satisfy every signature that accepts a
`float`; it must also carry enough metadata that a downstream uncertainty budget can
read its standard uncertainty without a human re-deriving it from prose.

`Constant` (`src/foundation_science/constants/constant.py`) subclasses `float` to
satisfy both requirements at once.

## The `Constant` contract

`Constant` SHALL subclass `float`, use `__slots__`, and expose exactly four fields:
`unit`, `std_uncertainty`, `distribution`, `source`.

All four SHALL be required keyword arguments with no defaults. This makes "I did not
think about the uncertainty" unrepresentable at the definition site.

Arithmetic on a `Constant` returns a plain `float` and discards the metadata. This
is required behavior, not a limitation: automatic propagation would have to assume
the inputs are independent, and a combined uncertainty that is silently too small is
worse than no combined uncertainty at all. Combining is the explicit job of the
propagation layer.

`Constant` SHALL implement `__reduce__` rather than `__getnewargs__`; the required
keyword-only arguments make the inherited float reconstruction path unusable for
`pickle` and `copy`.

## The three-state uncertainty rule

`std_uncertainty` is typed `float | None`, and `None` SHALL NOT be treated as
equivalent to `0.0`:

| State | `std_uncertainty` | Meaning |
|---|---|---|
| Exact by definition | `0.0` | A defined convention or an SI-exact value. No error. |
| Measured, Type B | `> 0.0` | From CODATA, a calibration certificate, or a spec band. |
| Unknown | `None` | The error is real but has not been quantified. |

Conflating the last two is the failure this type exists to prevent. A representative
engineering value recorded as `0.0` claims a precision it does not have and shrinks
every budget that consumes it.

`Constant.__new__` SHALL raise `ValueError` on an incoherent pairing, so a violation
fails at import rather than at use:

- `EXACT` requires `std_uncertainty == 0.0`
- `UNKNOWN` requires `std_uncertainty is None`
- `NORMAL` / `RECTANGULAR` / `TRIANGULAR` require a positive `float`

Constants in this package are always Type B by construction. Type A (statistical,
from repeat measurements) enters at the metrology layer, never here.

### Consequence for consumers

Any layer that combines uncertainties SHALL refuse to produce a combined value when
a contributing leaf is `None`. Substituting zero for unknown is prohibited.

## Entry-time normalization to k=1

Stored uncertainty SHALL always be standard uncertainty at k=1. Conversion happens
at the definition site, where the distribution is known, never at the point of use,
where it is not:

- `Constant.from_half_width(value, half_width=a, ...)` — `u = a/√3` (rectangular) or
  `u = a/√6` (triangular)
- `Constant.from_expanded(value, expanded=U, k=2.0, ...)` — `u = U/k`

Recording `distribution` alongside the value is what lets a budget report state its
own assumptions.

## Grouping

Constants SHALL be grouped substance-major, not domain-major. Every property of a
substance belongs to that substance's namespace class regardless of the domain it
comes from, so a transport property joins `DryAir` rather than fragmenting the
substance across a `transport` module.

Three kinds of module:

- `universal.py` — constants with no substance and no reference state. Flat
  module-level names; there is one universal namespace and nothing to disambiguate.
- `standards/` — defined reference states and conventions (`ISA`). Exact within the
  standard's own frame.
- `materials/` — substances (`DryAir`, `JetA1`), one class per substance.

A name suffix is permitted only when it carries information. `ISA.T_SL` keeps `_SL`
because the standard defines conditions at many altitudes; `DryAir.R` drops `_AIR`
because the class already supplies it.

`__init__.py` files SHALL stay empty. Consumers import the module or class path
directly, which is the call-site qualification this design exists to produce.

## Registry

`registry.iter_constants()` discovers constants by introspection. A hand-maintained
index is prohibited — it is a second source of truth that drifts the moment someone
adds a value.

The registry backs the CI audit in `tests/test_constants.py`, which SHALL include a
non-zero-count assertion so a broken walk cannot silently pass every other check.

## Package boundaries

`foundation_science` SHALL import nothing from the other top-level packages, and
SHALL declare no external runtime dependency. This is enforced statically by
`tests/test_package_layering.py`.

This package holds **scalar constants only**. Two adjacent kinds of data are
explicitly out of scope and SHALL NOT be added here:

- **Tables** — keyed collections with a uniform schema (periodic table, steam
  tables, material property databases). These need lookup functions and a data
  model.
- **Parameter sets** — mutually consistent named bundles (molecular-dynamics force
  fields, equation-of-state coefficients). A force field is only valid as a
  versioned set; mixing terms across sources is a physics error, so these need
  provenance as data rather than as a docstring.

## Deferred: the metrology layer

`foundation_science.metrology` is not implemented. When it is, it SHALL depend on
`constants` and never the reverse, so the constants package cannot grow a math
engine. The intended design is forward-mode dual numbers carrying `∂f/∂xᵢ` keyed by
named source, which preserves the sensitivity coefficients a GUM budget table
reports — not just the combined number.
