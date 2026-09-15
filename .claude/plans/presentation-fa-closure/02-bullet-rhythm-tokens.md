---
human_ask: >
  a series of FA's was generated from the first use of the build presentation tool.
  please review:
  /Users/nbergantz/__Workspaces__/pythonWorkspaces/py-clerical-tools/.claude/fa_reports
  and create a series action plan on closing these gaps.
goal: >
  Add bullet style/indent tokens to the bullets arm and paragraph-rhythm fields to
  text-bearing regions.
last_updated: 2026-09-15
semver: 0.0.1
author: Nicholas Bergantz
status: completed
---

# F2 — Bullet + rhythm tokens

Serves [Summary goal](./00-overview.md#summary-goal) · [Original ask](./00-original-ask.md).
Implements [presentationSchema.md](../../specs/presentationSchema.md) **R16**. Evidence:
`py-clerical-tools/.claude/fa_reports/FA-02-structured-text-and-spacing.md`. Unblocks the
clerical bullet/rhythm token upgrade.

## Deliverable

- `bullets` arm (in `PresentationDeck-schema.json`, `contentBlock`) gains an optional
  bullet `style` enum (`disc` | `dash` | `none`) and bounded per-level indent/hanging
  tokens.
- text-bearing `region` (in `PresentationSlideLayouts-schema.json`) gains optional
  paragraph rhythm: `lineSpacing`, `spaceBefore`, `spaceAfter`.
- Regenerated types + round-trip tests. No defaults (per R16, defaults stay absent so
  output does not silently depend on a template).

## Files

- `schema/schemas/Presentations/PresentationDeck-schema.json` — bullet `style` + indent
  tokens on the bullets fields.
- `schema/schemas/Presentations/PresentationSlideLayouts-schema.json` — rhythm on region.
- `src/foundationTypes/presentationTypes/Presentations.py` — regenerated.
- `tests/test_presentation_bullet_rhythm.py` — new.

## Design constraints (decided here)

- Flat bag, no discriminated union (R9): add optional sibling fields.
- `style` enum members exactly `disc`/`dash`/`none`.
- Indent tokens are bounded numbers with descriptive docstrings; keep names aligned with
  R16 prose.
- All optional, no `required`, no `default`.

## TDD steps

1. Failing tests: `test_bullets_style_and_indent_roundtrip`,
   `test_region_rhythm_roundtrip`, `test_existing_bullets_still_valid` (regression).
2. Edit schemas; `make codegen-all`.
3. `make uv-fullCheck` green.

## Acceptance criteria

- [x] Bullet style/indent + region rhythm validate and round-trip.
- [x] Existing bullets/regions still valid; no defaults added.
- [x] `make codegen-all` clean; generated file untouched (only regenerated).
- [x] `make uv-fullCheck` green.

## Out of scope

- Rendering bullets/rhythm (clerical chunks 02 upgrade, and renderer R5e).
- Metric role styles (chunk 03).

## Ask ↔ result

**Objective (`human_ask`/`goal`):** the `human_ask` recorded on this chunk and the
series overview is planning-only — review the `py-clerical-tools` FA reports and
produce an action plan closing the gaps. This chunk's own `goal` narrows that to one
concrete deliverable: add bullet style/indent tokens to the `bullets` arm and
paragraph-rhythm fields to text-bearing regions, additively, per R16.

**Live authorization:** the live command `/execute-plan
.claude/plans/presentation-fa-closure` explicitly authorized implementing chunk 02
now — a live execution request, not a conflict with the recorded planning-only
`human_ask`.

**Delivered:** in `schema/schemas/Presentations/PresentationDeck-schema.json`,
added three optional sibling fields on `contentBlock` (flat bag, no discriminated
union, per R9): `bulletStyle` (enum `disc`/`dash`/`none`), `bulletIndent` (array of
number ≥ 0, max 5 items — one per bullet level 0–4), and `bulletHangingIndent`
(array of number ≥ 0, max 5 items). In
`schema/schemas/Presentations/PresentationSlideLayouts-schema.json`, added three
optional fields on `region`: `lineSpacing`, `spaceBefore`, `spaceAfter` (all
number ≥ 0). None is in any `required` list; none carries a `default`, per R16's
"keep defaults absent" instruction. Regenerated
`src/foundationTypes/presentationTypes/Presentations.py` via `make codegen-all`
(not hand-edited) — `ContentBlock` gained `bullet_style: Optional[BulletStyle]`,
`bullet_indent`/`bullet_hanging_indent: Optional[List[float]]`, and a new
`BulletStyle` enum; `Region` gained `line_spacing`/`space_before`/`space_after:
Optional[float]`. No new nested object type was introduced, so
`CLASSES_FOR_BASE_PARENT` in `schema/scripts/generatePresentations.sh` required no
change. Added `tests/test_presentation_bullet_rhythm.py` with the three
TDD-specified tests (`test_bullets_style_and_indent_roundtrip`,
`test_region_rhythm_roundtrip`, `test_existing_bullets_still_valid`); confirmed the
import failed before the schema edit (no `BulletStyle`) and all three pass after.
`make codegen-all` regenerated cleanly with `git status` showing drift limited to
the two schemas, the generated file, and the new test. `make uv-fullCheck` is
green: flake8 clean, mypy strict clean (67 + 45 files), 939 tests passed
(including the 3 new ones). No gap.
