---
plan: Fix08GeneratedGuardTypeError
scope: project
status: complete
last_updated: 2026-08-23
semver: 0.0.2
author: Nicholas Bergantz
---

# Fix 08 — Generated `from_dict` Guards Raise `TypeError`

## Goal

Normalize quicktype's bare `assert isinstance(obj, dict)` guard in every generated `from_dict` into an explicit `TypeError` check, so generated models validate their input the same way the shared converters already do.

Contracts: [schemaCodegen.md](../specs/schemaCodegen.md), [dataModelHelper.md](../specs/dataModelHelper.md).

## Depends on

Nothing. Blocks presentation chunk 05.

## Defect

`from_union` (`src/foundationTypes/data_model_helper.py:91`) catches `(TypeError, ValueError, KeyError)`. Generated models signal wrong-type input with a bare `assert isinstance(obj, dict)`, which raises `AssertionError` — outside that tuple. So a legitimately-absent `Optional[Model]` field raises out of the union instead of falling through to `from_none`.

Reproduced against chunk 01's approved examples: `PresentationSlideLayouts.from_dict(layouts.json)` fails at `RegionDefaults.from_dict(None)` for an absent optional `body` region. All 7 tests in `tests/typeTests/testPresentationSlideLayouts.py` fail in `setUp` at this one line.

There are **190** occurrences of the identical guard across 7 generated modules (`ModelContextProtocol.py` 154, `Presentations.py` 16, `MathTypes.py` 13, `ChArUcoConfig.py` 3, `DiskUsage.py` 2, `StandardizedLoggerConfig.py` 1, `GeoCoordinate.py` 1). It is the only bare-assert form in the generated tree. The 168 `from_dict, from_none` unions in `ModelContextProtocol.py` carry the same latent failure; Presentations is simply the first model whose example data exercises an absent optional nested object.

## Why not widen `from_union`

Adding `AssertionError` to the caught tuple was measured to turn the suite green, and is still the wrong fix:

1. **`python -O` strips assertions entirely.** Under optimized runtime the guard vanishes, `from_dict` proceeds on a non-dict, and the failure resurfaces as a downstream `AttributeError` — the broadened catch fixes nothing there.
2. **It conceals programming defects.** A genuine `AssertionError` raised anywhere inside a nested `from_dict` would be silently swallowed by generic union dispatch and reported as a deserialization miss.
3. **It is inconsistent with the module's own converters.** `from_str`, `from_int`, `from_bool`, `from_list`, and the rest all raise explicit `TypeError`.
4. **It only covers union-dispatched fields.** A missing *required* nested object is not inside a `from_union`, so it would keep raising `AssertionError` — two different error types for the same class of authoring mistake.

Fixing the generated guard closes all four; `from_union` then needs no change at all.

## Files

Edit:

- `schema/scripts/reuse/normalize_generated.sh` — add the third normalization pass
- `.claude/specs/schemaCodegen.md` — document the pass, bump semver
- `.claude/specs/dataModelHelper.md` — state the `TypeError` guard contract, bump semver
- `HISTORY.md` — `[Unreleased]` / `Fixed` bullet

Regenerate (never hand-edit):

- `src/foundationTypes/commonTypes/ModelContextProtocol.py`
- `src/foundationTypes/commonTypes/GeoCoordinate.py`
- `src/foundationTypes/commonTypes/disk_usage/DiskUsage.py`
- `src/foundationTypes/cvTypes/ChArUcoConfig.py`
- `src/foundationTypes/mathTypes/MathTypes.py`
- `src/foundationTypes/presentationTypes/Presentations.py`
- `src/foundationTypes/standardizedLoggerConfig/StandardizedLoggerConfig.py`

Create:

- `tests/typeTests/testGeneratedGuards.py`

## Design constraints

**The normalizer owns the rewrite.** `normalize_generated.sh` is already the documented single source of truth for post-quicktype rewrites, is idempotent, and is applied on both paths (`codegen.sh`'s `run_ruff` per-file, and the `make codegen-all` fleet sweep). Add a third pass there. Do not add per-script `sed` calls, and do not touch the individual `generate*.sh` scripts.

**Match the existing converter message exactly.** `from_dict`'s own dict converter (`data_model_helper.py:43`) uses:

```python
raise TypeError(f"Expected dict, got {type(x).__name__}")
```

The generated guard becomes the statement form of the same check:

```python
if not isinstance(obj, dict):
    raise TypeError(f"Expected dict, got {type(obj).__name__}")
```

**Do not modify `from_union`.** Its current `(TypeError, ValueError, KeyError)` tuple is correct once the guards raise `TypeError`. Leaving it narrow is what preserves signal 2 above.

**Idempotent and safe on hand-written files.** Re-running the pass is a no-op, and the pattern must only match quicktype's generated form. Preserve the existing indentation of the matched line.

**Generated files stay read-only.** Every `.py` change lands by re-running codegen, never by editing. `make codegen-all` must be verifiable as idempotent (a second run produces no diff).

## Steps (TDD)

1. Add `tests/typeTests/testGeneratedGuards.py`: assert no `assert isinstance(obj, dict)` remains anywhere under `src/foundationTypes/`, and assert `from_dict(None)` / `from_dict([])` / `from_dict("x")` raise `TypeError` on a representative model from each generated module. Confirm it fails.
2. Implement the third pass in `normalize_generated.sh`.
3. Run `make codegen-all`; confirm all 190 guards are rewritten and the new test passes.
4. Run `make codegen-all` a second time; confirm `git diff` is empty (idempotence).
5. Verify `python -O` behavior: the guard now raises under optimization too.
6. Update both specs (bump semver) and add the `HISTORY.md` bullet.
7. Run `make uv-fullCheck`.

## Acceptance criteria

- [x] Zero occurrences of `assert isinstance(obj, dict)` under `src/foundationTypes/`.
- [x] All 190 sites now raise `TypeError` with the shared converter's message form
      (with one deliberate wording deviation — see Resolution notes).
- [x] `normalize_generated.sh` performs the rewrite; no `generate*.sh` script was edited.
- [x] `make codegen-all` is idempotent — a second consecutive run leaves `git diff` empty.
- [x] Guards still reject non-dict input when run under `python -O`.
- [x] `from_union` in `data_model_helper.py` is unchanged.
- [x] `PresentationSlideLayouts.from_dict` loads `schema/examples/Presentations/layouts.json` and round-trips.
- [x] Both specs carry the new contract and a bumped semver; `HISTORY.md` has the bullet.
- [x] `make uv-fullCheck` passes.

## Resolution notes

Implemented as specified: a third pass in `normalize_generated.sh` rewrites the bare
`assert isinstance(obj, dict)` guard to an explicit `if not isinstance(obj, dict): raise
TypeError(...)`, preserving indentation, idempotent, matched only on generated files.
`tests/typeTests/testGeneratedGuards.py` reproduces the defect first (fails red against
the un-rewritten tree), then passes green after the pipeline change plus a fresh
`make codegen-all`. Guard count before: 190 `assert isinstance(obj, dict)` occurrences
across 7 files. Guard count after: 0 bare asserts, 190 `TypeError`-raising guards.
`make codegen-all` run twice back-to-back produced byte-identical output on the second
run (`diff -rq` of the generated tree was empty). `python -O` was verified two ways: a
throwaway `assert False` was confirmed stripped under `-O` (sanity check that `-O`
actually optimizes in this environment), then `GeoCoordinate.from_dict(None)` under
`python -O` was confirmed to still raise `TypeError: Expected dict, got NoneType`.
`make uv-fullCheck` passed: ruff clean, strict mypy clean (60 src files + 31 test
files), 465 tests passed (up from 416 in the baseline — the presentation-chunk test
files already on disk, including `testPresentationSlideLayouts.py`, are now green for
the first time).

**One deviation from the chunk's literal target text.** The chunk specified
`raise TypeError(f"Expected dict, got {type(obj).__name__}")`, matching
`data_model_helper.py:43` verbatim. Running `make codegen-all` with that exact
replacement surfaced a real bug via ruff's F823 (`Local variable 'type' referenced
before assignment`) in 7 generated methods across `ModelContextProtocol.py` and
`Presentations.py` (`Region`, `ContentBlock`, `Promptreference`, `Resourcelink`,
`Resourcetemplatereference`, `Stringschema`, `Textcontent`) — every one of these has a
JSON Schema field literally named `"type"`, and quicktype's generated body later
assigns a same-scope local `type = ...` for it. Python's function-wide scoping rule
makes any bare `type` reference in that function resolve to the local for the entire
function body, regardless of textual position, so the guard's `type(obj)` call would
raise `UnboundLocalError` instead of `TypeError` — a strictly worse regression than the
`AssertionError` this chunk exists to fix, and one `python -O` does nothing to help
with (it's a `NameError`-class failure, not an assertion). I substituted
`obj.__class__.__name__`, which is a builtin-free expression producing an identical
string to `type(obj).__name__` for every value this guard is ever called with (dict,
list, str, int, float, bool, `None`, or any `DataModelHelper` instance) — same message
text at runtime, just not the same source spelling documented in the chunk. Both specs
document this deviation and its rationale (see `schemaCodegen.md`'s new "Generated
`from_dict` Dict-Type Guard" section and `dataModelHelper.md`'s `from_dict()`
subsection). `from_union`'s catch tuple was not touched.

## Out of scope

- Changing `from_union`'s caught-exception tuple.
- Replacing any other quicktype artifact or converter.
- Presentation chunk 05's own test files (they resume after this lands).
- Migrating generated models toward a different validation library or codegen tool.
