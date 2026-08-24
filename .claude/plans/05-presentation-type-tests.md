---
plan: ActionPlan05PresentationTypeTests
scope: project
status: complete
last_updated: 2026-08-23
semver: 0.0.3
author: Nicholas Bergantz
---

# 05 — Presentation Type Tests

## Goal

Close tier 1 with the contract tests the generated models owe: round-trip fidelity, `from_dict` type validation, and correct wire keys.

Contract: [dataModelHelper.md](../specs/dataModelHelper.md) Compliance Requirements; [presentationSchema.md](../specs/presentationSchema.md) Compliance Requirements.

## Depends on

Chunks 03 and 04.

## Files

Create:
- `tests/typeTests/testPresentationDeck.py`
- `tests/typeTests/testPresentationColorTheme.py`
- `tests/typeTests/testPresentationSlideLayouts.py`

## Design constraints

**Follow the house idiom for generated models**, which is `unittest.TestCase`, not bare pytest functions — see `tests/typeTests/testUnitSphericalArc.py`. Per file: `setUp` building named fixtures, then one test per contract clause.

The four clauses each model owes:

1. `from_dict` builds a valid instance from a plain dict.
2. `to_dict` produces the camelCase wire keys the schema declares (the generated fields are snake_case; `mutedText` must not become `muted_text` on the wire).
3. Round-trip preserves state — iterate edge cases under `with self.subTest(...)`.
4. `from_dict` raises `TypeError` on a missing required field and on a wrong-typed field.

**Load the real example instances** from `schema/examples/Presentations/` rather than hand-building dicts everywhere. That makes these tests a check on the examples too, so a broken example cannot ship. Keep one hand-built minimal fixture per model for the error cases.

**Enum coverage.** Assert that every one of the 30 `themeColorRef` values resolves through `resolve_color` against the example theme. This is the check that keeps the enum and the theme's property names in step — the invariant named in R4, and the thing most likely to silently drift when an accent is added.

## Steps (TDD)

1. Write the three test files. Run — expect failures wherever the generated models or examples disagree with the schema.
2. Fix whatever they catch, in the schema or the example, never in the generated `.py`.
3. Re-run — passes.
4. `make uv-fullCheck`.

## Acceptance criteria

- [x] Each of the three models has all four contract clauses tested (`testPresentationColorTheme.py`, `testPresentationSlideLayouts.py`, `testPresentationDeck.py` — all passing).
- [x] Every `themeColorRef` enum value resolves against the example theme (`testPresentationColorTheme.py`, 27 values).
- [x] Tests load and validate `schema/examples/Presentations/*.json` — `theme.json`, `layouts.json`, and `deck.json` all load and round-trip cleanly now that fix-08 landed.
- [x] Round-trip tests use `subTest` so a single failure names the offending case, verified passing for all three models.
- [x] `make uv-fullCheck` passes; mypy strict is clean over `tests/` (472 tests passed).

## Out of scope

- Rendering, `.pptx`, or anything importing `python-pptx` — that is the clerical repository's gate-1 work.
- Performance or large-deck benchmarks.
- Property-based testing (no `hypothesis` dependency).

## Resolution notes

**Unblocked by fix-08.** This chunk was previously blocked on `from_union` in
`src/foundationTypes/data_model_helper.py` not catching the `AssertionError` raised
by quicktype's bare `assert isinstance(obj, dict)` guard when an `Optional[Model]`
field is legitimately absent (see git history for the original Blocker text). fix-08
(`.claude/plans/fix-08-generated-guard-typeerror.md`) resolved this at the root: the
codegen normalizer now rewrites every generated dict-type guard to raise `TypeError`
instead of asserting, which `from_union`'s existing `(TypeError, ValueError, KeyError)`
catch already handles correctly -- `from_union` itself was intentionally left
unchanged, per fix-08's "Why not widen `from_union`" analysis. With that landed,
`PresentationSlideLayouts.from_dict(layouts.json)`, `PresentationDeck.from_dict(deck.json)`,
and `PresentationMetadata.from_dict(...)` all load their real, schema-valid examples
(which omit optional nested objects, the intended sparse-authoring pattern) without
error.

**Work completed:**

- `testPresentationColorTheme.py` (pre-existing, tightened): all four contract clauses
  plus the 27-value `themeColorRef` enum-coverage check. Its two `from_dict` error-path
  tests that previously tolerated `(TypeError, AssertionError)` now assert `TypeError`
  explicitly, since the guard fix makes that the only exception type raised.
- `testPresentationSlideLayouts.py` (pre-existing, tightened): now passes end-to-end
  against the real `layouts.json` example; its one `(TypeError, AssertionError)`
  tolerance was likewise tightened to `TypeError`.
- `testPresentationDeck.py` (new): all four contract clauses against `deck.json` and a
  hand-built minimal fixture, plus a `full` fixture that exercises the two optional
  nested objects (`PresentationMetadata.defaults`, `ContentBlock.style`) for the
  camelCase wire-key check. Its example-based test carries an explicit comment noting
  this is the exact shape that used to crash pre-fix-08.
- Repo-wide grep for `AssertionError` in `tests/` confirmed no other test tolerates or
  expects `AssertionError` from a `from_dict` call; the only remaining occurrences are
  unrelated mock-guard sentinels (`test_ssh_transact.py`, `test_rsync_transact.py`,
  `test_socket_byte_transport.py`) and explanatory comments.
- No schema, example, or generated `.py` was modified -- only test files.
- `make uv-fullCheck` passes: ruff clean, strict mypy clean (60 src + 32 test files),
  472 tests passed (up from 465 after fix-08, +7 for the new `testPresentationDeck.py`).
