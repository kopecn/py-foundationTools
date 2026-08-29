---
plan: Fix06PhysicalConstantFiniteness
scope: project
status: needs-approval
last_updated: 2026-08-28
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
