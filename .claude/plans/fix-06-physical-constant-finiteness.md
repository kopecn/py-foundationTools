---
plan: Fix06PhysicalConstantFiniteness
scope: project
status: pending
last_updated: 2026-08-23
semver: 0.0.1
author: Nicholas Bergantz
---

# Fix 06 — Physical-Constant Finiteness

## Goal

Enforce the physical-constants contract that bounded standard uncertainties are
positive and finite.

Contract: [physicalConstants.md](../specs/physicalConstants.md).

## Depends on

Fix 05 only in preferred landing order. There is no code dependency.

## Defect

The validation currently checks only `std_uncertainty <= 0.0`. IEEE-754 `NaN` makes
that comparison false, and positive infinity also passes, so both can be stored under
`NORMAL`, `RECTANGULAR`, or `TRIANGULAR` despite `_BOUNDED` documenting a positive,
finite requirement.

The normalization constructors have the same comparison hole for `half_width`,
`expanded`, and `k`.

## Files

Edit:

- `src/foundation_science/constants/constant.py`
- `tests/test_constants.py`
- `HISTORY.md`

Update only if clarification is needed:

- `.claude/specs/physicalConstants.md`

## Design constraints

**Use `math.isfinite`.** Bounded distributions require `std_uncertainty` to be both
strictly positive and finite. Preserve the existing exact (`0.0`) and unknown (`None`)
states unchanged.

**Validate normalization inputs directly.** `from_half_width` rejects non-finite
`half_width`; `from_expanded` rejects non-finite `expanded` and `k`. Error messages
name the input rather than relying only on a later derived uncertainty failure.

**Scope stays on uncertainty metadata.** Do not add a finiteness rule for the numeric
constant value itself without a separate contract decision; this review finding is
specifically about uncertainty invariants.

**Audit uses the same invariant.** Strengthen the package-wide registry test so every
bounded shipped constant is asserted finite as well as positive.

## Steps (TDD)

1. Parameterize direct-construction tests over `NaN`, positive infinity, and negative
   infinity for every bounded distribution.
2. Add `from_half_width` and `from_expanded` cases for non-finite inputs and coverage
   factors.
3. Strengthen `test_every_declared_constant_is_coherent` with `math.isfinite`.
4. Implement finiteness checks with precise `ValueError` messages.
5. Add an `[Unreleased]` `Fixed` bullet.
6. Run `tests/test_constants.py`, then `make uv-fullCheck`.

## Acceptance criteria

- [ ] No bounded distribution accepts `NaN` or either infinity as uncertainty.
- [ ] Normalization constructors reject non-finite widths, expanded uncertainties,
  and coverage factors.
- [ ] Exact and unknown states retain their current behavior.
- [ ] Pickle/copy round trips and float substitutability remain unchanged.
- [ ] Every shipped bounded constant passes a positive-and-finite registry audit.
- [ ] `make uv-fullCheck` passes.

## Out of scope

- Automatic uncertainty propagation.
- Unit algebra or unit conversion.
- Validating the central numeric value as finite.
- Revising the provenance or values of shipped constants.

