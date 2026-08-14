---
plan: ActionPlan22MathTierContractTests
scope: project
status: complete
last_updated: 2026-07-08
semver: 0.1.0
author: Nicholas Bergantz
---

# 22 — Math Tier Contract Tests (corrective)

## Origin

Post-audit of chunk 21 (2026-07-08), findings F1 + F2 — both class **(b)
implemented but untested**:

- **F1.** The 13 `XxxxABC` classes each carry a concrete `to_dict` that is the
  serialization contract Tier-3 implementers inherit — but every generated
  `XxxxType` shadows it with the quicktype-generated `to_dict`, so no test (and
  no repo code) ever executes the ABC versions. The wire shape is therefore
  defined twice (hand-written ABC `to_dict` vs schema→quicktype `to_dict`)
  with nothing pinning them together: a schema change regenerates
  `MathTypes.py` while the ABC copy silently drifts. Audit verified all 13
  pairs agree today by source inspection; this chunk makes that agreement
  executable.
- **F2.** `mathTypeTiers.md` Invariant 4 (ABC first in the generated base
  list) has no test. The post-processor emits it correctly today
  (`postprocess_mathtypes.py:146`), but a regression would only surface as
  subtle MRO behavior, not a failure.

This chunk also closes the user-raised investigation "should `to_dict` /
`from_dict` remain on the ABCs?" — answer: **keep both** (see chunk 21's
audit report / `mathTypeTiers.md` tier rationale); the parity test below is
the mitigation for the one real cost (duplicated wire shape).

## Goal

One new test module that pins the Tier-1 ↔ Tier-2 contract for all 13 math
types: structural inheritance (Invariant 4) and ABC-vs-generated `to_dict`
parity.

## Implementation Steps

- [x] **1. Add `tests/typeTests/test_math_tier_contract.py`** with a
  module-level table of all 13 `(XxxxType, XxxxABC)` pairs (mirror
  `TYPE_TO_LIKE` in `schema/scripts/reuse/postprocess_mathtypes.py`) and
  representative `from_dict` payloads per type (nested waveform payloads need
  `t0`/`dt`; include a `PrecisionTimestampType` case with optionals present
  AND a case with optionals absent).
- [x] **2. Structural test (F2):** for every pair assert
  `issubclass(XxxxType, XxxxABC)`, `issubclass(XxxxType, DataModelHelper)`,
  and `XxxxType.__mro__.index(XxxxABC) < XxxxType.__mro__.index(DataModelHelper)`
  (Invariant 4, ABC first).
- [x] **3. Parity test (F1):** for every pair, build `inst =
  XxxxType.from_dict(payload)` and assert
  `XxxxABC.to_dict(inst) == inst.to_dict()` — calling the ABC's concrete
  implementation explicitly so the shadowed code path actually runs.
- [x] **4. Spec:** add a compliance item to
  `.claude/specs/mathTypeTiers.md` requiring the parity + base-order
  assertions in `tests/typeTests/test_math_tier_contract.py` for every new
  Math type; bump `last_updated`/`semver` (minor).
- [x] **5. Gate:** `make uv-fullCheck` green.

## Out of Scope

- Extending `to_dict`/`from_dict` round-trip suites to all 13 types beyond
  what the parity test implicitly exercises (the two existing
  `tests/typeTests/testUnitSpherical*.py` files stay as-is).
- Any change to the ABCs, `MathTypes.py`, or the post-processor — this chunk
  is tests + one spec compliance line only.

## Acceptance

- [x] New test module runs 13 structural + 13 parity assertions (subTest or
  parametrize per type) and fails if any ABC `to_dict` diverges from the
  generated wire shape or if base order flips.
- [x] `make uv-fullCheck` passes.
- [x] `mathTypeTiers.md` compliance checklist names the new test; frontmatter
  bumped.

## Resolution notes

- `tests/typeTests/test_math_tier_contract.py` added: a `PAIRS` module table
  of all 13 `(XxxxType, XxxxABC, payload)` tuples (mirrors
  `postprocess_mathtypes.py`'s `TYPE_TO_LIKE`), driving two
  `pytest.mark.parametrize` tests — `test_abc_precedes_data_model_helper_in_mro`
  (F2, Invariant 4) and `test_abc_to_dict_matches_generated_to_dict` (F1,
  calls `XxxxABC.to_dict(instance)` unbound so the shadowed ABC code path
  actually executes). A 27th standalone test,
  `test_precision_timestamp_parity_with_optionals_present`, covers
  `PrecisionTimestampType` with `referenceFrame`/`timescale`/`uncertainty`
  populated; the PAIRS-table entry for that type uses the optionals-absent
  payload, so both variants required by step 1 are covered without inflating
  the acceptance-criteria "13 parity assertions" count.
- **Deviation/surprise:** `pytest.mark.parametrize(ids=...)` calls the `ids`
  callback once per scalar parameter value, not once per tuple row — an
  initial `_pair_id(pair)` taking the whole 3-tuple raised
  `TypeError: type 'QuaternionType' is not subscriptable` at collection time.
  Fixed by making `_pair_id` a single-value function that names only `type`
  instances (both `type_cls` and `abc_cls` columns) and returns `None` (pytest
  auto-numbers) for the payload dict column.
- **Verification beyond the plan's steps:** manually mutated
  `QuaternionABC.to_dict` (added `+ 1` to the `z` field) and confirmed
  `test_abc_to_dict_matches_generated_to_dict[QuaternionType-...]` fails with
  a clear diff, then reverted via `git checkout --` (chunk 21's staged rename
  of that file was left untouched — verified via `git status --short` showing
  only the new test file as untracked afterward).
- No spec-forced implementation changes were needed beyond the planned
  compliance-item addition (Step 4); `mathTypeTiers.md` bumped to `0.2.0`
  (minor, per Convention 5) and its `applies_to` list extended to include the
  new test module.
- Gate: `make uv-fullCheck` — ruff clean, mypy strict clean (38 src files + 21
  test files), pytest 339/339 passed (312 pre-existing + 27 new).
