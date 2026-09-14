---
plan: ActionPlan19DocsConventionSweep
scope: project
status: complete
last_updated: 2026-07-06
semver: 0.2.0
author: Nicholas Bergantz
---

# 19 — Docs & Convention Drift Sweep (corrective)

## Goal

Close the documentation and convention drift the audit found across
`.claude/CLAUDE.md`, the specs, the action-plan records, and `pyproject.toml`.
Docs must tell the truth about the current Makefile, paths, and file names.

## Origin

Chunk 12 audit findings + cross-cutting convention check (corrective follow-up to
plans 00–13).

## Depends on

14–18 (runs last so it records the final state).

## Files

- `.claude/CLAUDE.md`
- `.claude/specs/schemaCodegen.md`, `dataModelHelper.md`, `mathTypeTiers.md`
- `.claude/action-plan/00-overview.md`, `10-sockettransact.md`
- `pyproject.toml`

## Drift to fix

1. **`.claude/CLAUDE.md` Commands section** documents `make fullCheck` /
   `lintCheck` / `formatCheck` / `typecheck` — none exist (verified: `make
   fullCheck` fails). Rewrite to the real targets: `uv-fullCheck` (CI gate),
   `uv-lint`, `uv-typecheck`, `uv-test`, `test`, plus whatever `make help`
   actually lists for install/format at execution time (re-verify against the
   Makefile, not this plan).
2. **Single-test examples** point at `tests/testfoundation_math.py` (doesn't
   exist) → `tests/testfoundationMath.py`.
3. **`StandardizedLoggerConfig` casing**: actual directory is
   `src/foundationTypes/standardizedLoggerConfig/`. Fix `.claude/CLAUDE.md` (two
   occurrences) and `schemaCodegen.md` `applies_to:` — resolves on macOS but
   breaks on case-sensitive filesystems.
4. **`00-overview.md` convention #2** still cites `make fullCheck` → `make
   uv-fullCheck`.
5. **Frontmatter convention** on 3 legacy specs: add `last_updated` (date of
   edit), `semver: 0.0.1`, `author: Nicholas Bergantz` to `dataModelHelper.md`,
   `mathTypeTiers.md`, `schemaCodegen.md`. Content otherwise untouched (except
   the schemaCodegen casing fix above).
6. **`pyproject.toml` keywords** still contain `foundation_cli_helpers` →
   replace with the current name.
7. **`10-sockettransact.md` resolution notes** say "all 11 Compliance
   Requirements"; the spec lists 12 → correct the count.

## Design constraints

- Docs-only chunk plus the one `pyproject.toml` keyword line; zero source/test
  changes.
- Every edited managed markdown gets its frontmatter bumped (convention #7).
- Historical/naming-history notes explicitly exempted from the grep sweeps (e.g.
  the `foundationCLIHelpers` note in `cliTransact.md`).

## Steps

1. Apply fixes 1–7.
2. Grep sweeps (acceptance below).
3. `make uv-fullCheck` (proves the documented gate is the real one and nothing
   broke).

## Acceptance criteria

- [x] `grep -rn "make fullCheck\|make lintCheck\|make formatCheck\|make typecheck"`
      over `.claude/` and `README.md` returns only exempted historical notes.
- [x] `grep -rn "testfoundation_math"` over `.claude/` and `README.md` is empty.
- [x] `grep -rn "StandardizedLoggerConfig/"` over `.claude/` is empty (path
      references; prose class-name mentions of the generated model are fine).
- [x] `grep -n "foundation_cli_helpers" pyproject.toml` is empty.
- [x] All specs under `.claude/specs/` carry `last_updated`/`semver`/`author`.
- [x] Every `applies_to:` path in every spec exists on a case-sensitive check.
- [x] `make uv-fullCheck` passes.

## Resolution notes

- Rewrote `.claude/CLAUDE.md` Commands section against the real Makefile:
  `uv-fullCheck` (= `uv-lint` + `uv-typecheck` + `uv-test`), `uv-lint`, `uv-format`,
  `uv-typecheck` (mypy only — `ty` is a dev dep but intentionally not wired into
  the gate per the Makefile's own comment), `uv-test`, `test`, `testInEnv`,
  `installDev`/`e` (previously misdocumented as `devInstall`).
- Fixed `tests/testfoundation_math.py` → `tests/testfoundationMath.py` (2
  occurrences in `.claude/CLAUDE.md`).
- Fixed `StandardizedLoggerConfig/` → `standardizedLoggerConfig/` casing in
  `.claude/CLAUDE.md` (2 occurrences) and `schemaCodegen.md`'s `applies_to:`.
- `00-overview.md` convention #2: `make fullCheck` → `make uv-fullCheck`
  (dropped the stale `+ ty` from the parenthetical — `ty` isn't wired in).
- Added `last_updated: 2026-07-06` / `semver: 0.0.1` / `author: Nicholas
  Bergantz` frontmatter to `dataModelHelper.md`, `mathTypeTiers.md`,
  `schemaCodegen.md`.
- `pyproject.toml` keyword `foundation_cli_helpers` → `pyFoundationTools`.
- `10-sockettransact.md`: "all 11 Compliance Requirements" → "all 12" (verified
  by counting the numbered list in `socketTransact.md`'s Compliance
  Requirements section — items 1–12); bumped its frontmatter
  (`last_updated: 2026-07-06`, `semver: 0.1.0` → `0.1.1`).
- `00-overview.md` frontmatter bumped `semver: 0.3.0` → `0.3.1` (edited today,
  already dated).
- Additional minimal fix beyond the chunk's literal file list, needed to
  satisfy the acceptance grep over `README.md`: two `make fullCheck` /
  `make typecheck` lines in README's "Testing & Quality Assurance" section
  → `make uv-fullCheck` / `make uv-typecheck`. Left everything else in that
  README section untouched (`make lint` still says pylint, `make format` still
  says black, `make dist`/`make tag`/`make releaseTest`/`cleanBuild`/`cleanTest`
  are also stale but out of scope — no full README overhaul per chunk 12's
  tracked issue).
- Left the `01`–`13` action-plan chunks' own `make fullCheck` mentions
  untouched — they are historical records of what a completed chunk actually
  ran, several already annotated "(`make fullCheck` no longer exists)"; not in
  this chunk's `Files` list and outside its scope.
- `make uv-fullCheck`: ruff clean, mypy clean (37 + 19 files), 307 tests
  passed.

## Out of scope

- Full README overhaul (stale camelCase `saveToFile`/`loadFromFile` examples are
  the separately-tracked known issue from chunk 12).
- Renaming legacy `testfoundation*.py` files.
- `LengthPrefixedCodec` default `max_frame_size` — recorded as intentional in
  chunk 08; no change.
