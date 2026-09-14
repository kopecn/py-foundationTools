---
plan: Fix06PhysicalConstantFiniteness
scope: project
status: complete
last_updated: 2026-09-04
semver: 1.0.0
author: Nicholas Bergantz
---

# Fix candidate 06 — non-finite uncertainty metadata

Evidence: bounded uncertainty validation checks only `<= 0`, allowing `NaN` and
positive infinity through direct and normalization constructors.

Minimum fix: apply `math.isfinite` to bounded uncertainty inputs and add focused cases
for `NaN` and infinities while preserving exact (`0.0`) and unknown (`None`) states.

Do not validate the central constant value or add propagation, unit algebra, or value
revisions.

## Ask ↔ result

- **Objective:** reject non-finite (`NaN`, `+inf`) bounded `std_uncertainty` while preserving the three valid states.
- **Authorized by:** `/execute-plan please proceed` (user approved all of fix-01–07).
- **Delivered:** `math.isfinite` guard in `_validate` (between the `None` check and the `<= 0.0` check), so it covers the direct constructor and both normalization constructors (`from_half_width`/`from_expanded`), raising `ValueError` (matching convention). Tests assert `NaN`/`+inf` rejected via both paths and that exact `0.0`, unknown `None`, and ordinary positive-finite are preserved. Rejection cases confirmed failing pre-fix.
- **Gate:** `make uv-fullCheck` — ruff/mypy clean, 532 passed.
- **Gap:** none. Central value, propagation, unit algebra untouched.
