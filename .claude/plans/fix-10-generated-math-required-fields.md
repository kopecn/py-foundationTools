---
plan: Fix10GeneratedMathRequiredFields
scope: project
status: needs-approval
last_updated: 2026-09-04
semver: 1.0.0
author: Nicholas Bergantz
---

# Fix candidate 10 — generated math required-field contracts

Evidence: Math schemas require nested fields such as `position`, `orientation`, `t0`,
and `dt`, and their Tier-2 ABC accessors are non-optional. The generated dataclasses make
those fields optional with `None` defaults. `postprocess_mathtypes.py` acknowledges the
incompatible override and emits `# type: ignore[assignment]`, allowing direct constructors
to create schema-invalid objects that violate their base-class contract.

Minimum fix: change the schema/codegen/postprocessing strategy so required nested fields
remain required and non-optional in generated constructors. Remove the corresponding type
suppression and add contract tests for direct construction, `from_dict`, and regeneration.

Do not hand-edit `MathTypes.py`, weaken the ABC return types, make required schema fields
optional, or retain a `None` compatibility constructor unless separately approved.
