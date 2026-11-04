---
human_ask: >
  a series of FA's was generated from the first use of the build presentation tool.
  please review:
  /Users/nbergantz/__Workspaces__/pythonWorkspaces/py-clerical-tools/.claude/fa_reports
  and create a series action plan on closing these gaps.
goal: >
  Add per-role metric style fields (value/label/delta styles, gap, permitted flags) to
  the region schema.
last_updated: 2026-09-15
semver: 0.0.1
author: Nicholas Bergantz
status: completed
---

# F3 — Metric role styles

Serves [Summary goal](./00-overview.md#summary-goal) · [Original ask](./00-original-ask.md).
Implements [presentationSchema.md](../../specs/presentationSchema.md) **R17**. Evidence:
`py-clerical-tools/.claude/fa_reports/FA-02-structured-text-and-spacing.md`. Unblocks
clerical chunk 11.

## Deliverable

A metric `region` (in `PresentationSlideLayouts-schema.json`) gains optional style roles
for `value`, `label`, and `delta` (each the existing `style` object shape), an inter-field
gap, and permitted flags for `label`/`delta`. Regenerated types + round-trip tests.

## Files

- `schema/schemas/Presentations/PresentationSlideLayouts-schema.json` — add the role-style
  fields, referencing the existing `style` definition by bare-filename `$ref` (R2), plus
  a numeric gap and boolean permitted flags.
- `schema/scripts/generatePresentations.sh` — if a new wrapper object is introduced,
  add it to `CLASSES_FOR_BASE_PARENT`.
- `src/foundationTypes/presentationTypes/Presentations.py` — regenerated.
- `tests/test_presentation_metric_roles.py` — new.

## Design constraints (decided here)

- Reuse the existing `style` shape via `$ref`; do not re-declare it (R2, "one definition
  per concept").
- All optional; no defaults.
- Permitted flags are booleans; absence means permitted (documented in the description).

## TDD steps

1. Failing tests: `test_metric_role_styles_roundtrip`, `test_metric_gap_and_flags`,
   `test_existing_metric_region_still_valid`.
2. Edit schema; add base-parent entry if needed; `make codegen-all`.
3. `make uv-fullCheck` green.

## Acceptance criteria

- [x] Value/label/delta role styles + gap + flags validate and round-trip.
- [x] `style` reused via `$ref`, not re-declared.
- [x] Existing metric regions still valid; no defaults.
- [x] `make codegen-all` clean; `make uv-fullCheck` green.

## Out of scope

- Rendering distinct metric typography (clerical chunk 11).

## Ask ↔ result

**Objective (`human_ask`/`goal`):** the recorded `human_ask` is planning-only --
review the `py-clerical-tools` FA reports and produce an action plan closing the
gaps. This chunk's own `goal` narrows that to one concrete deliverable: add
per-role metric style fields (value/label/delta styles, gap, permitted flags) to
the region schema, additively, per R17. The two do not disagree about the
objective.

**Live authorization:** the live command `/execute-plan
.claude/plans/presentation-fa-closure` explicitly authorized implementing chunk
03 now -- a live execution request, not a conflict with the recorded
planning-only `human_ask`.

**R17 read literally:** "A `metric` region MAY declare separate style roles for
`value`, `label`, and `delta` (each an existing `style` shape), an inter-field
gap, and whether `label`/`delta` are permitted." Everything delivered maps
directly to this sentence; nothing beyond it was added.

**Delivered:** in `schema/schemas/Presentations/PresentationSlideLayouts-schema.json`,
added six optional fields on `region`: `valueStyle`, `labelStyle`, `deltaStyle`
(each `$ref: "PresentationDeck-schema.json#/definitions/contentBlock/properties/style"`
-- the existing inline `style` object on `contentBlock`, reused by cross-file JSON
pointer per R2's "one definition per concept" precedent, not re-declared),
`metricGap` (number >= 0), `labelPermitted` (boolean), `deltaPermitted` (boolean).
None is in `region`'s `required` list (`["id"]`, unchanged); none carries a
`default`; the two permitted flags' descriptions state "absence means permitted."

**One necessary deviation from the literal file list, made to satisfy the
chunk's own design constraint:** the `style` shape is not a top-level named
`definitions` entry in `PresentationDeck-schema.json` -- it is an object nested
inline under `contentBlock.properties.style`. A first codegen pass confirmed
`$ref`-ing that JSON pointer directly from `SlideLayouts` works structurally
(quicktype resolves cross-file pointers into `properties`, not just
`definitions`), but because four properties (`style`, `valueStyle`,
`labelStyle`, `deltaStyle`) now resolved to the same anonymous schema, quicktype
synthesized a new class name (`DeltaStyle`, chosen alphabetically) instead of
reusing the existing `Style` class already imported by
`src/foundation_tools/presentation/migration.py` and referenced by name in
`tests/test_presentation_migration.py` and
`tests/typeTests/testPresentationDeck.py`. That would have silently renamed a
public generated type and broken those call sites -- a correctness regression,
not a cosmetic one. I added a one-line `"title": "Style"` to the existing
`style` object in `PresentationDeck-schema.json` (no structural or behavioral
change; `contentBlock.style` still round-trips identically) so quicktype's
naming is deterministic and the pre-existing `Style` class name is preserved.
This is the smallest edit that makes "reused via `$ref`, not re-declared"
actually true at the generated-code level, not just in the schema text; I did
not otherwise restructure `PresentationDeck-schema.json`.

**Regeneration:** ran `make codegen-all` (not hand-edited); confirmed
`src/foundationTypes/presentationTypes/Presentations.py` now has exactly one
`Style` class (no duplicate), with `Region.value_style` / `label_style` /
`delta_style` all typed `Optional[Style]`, and `Region` gaining `metric_gap:
Optional[float]`, `label_permitted` / `delta_permitted: Optional[bool]`. No new
wrapper object type was introduced (`Style` already existed and was already in
`CLASSES_FOR_BASE_PARENT`), so `schema/scripts/generatePresentations.sh` needed
no edit.

**Verification:** added `tests/test_presentation_metric_roles.py` with the three
TDD-specified tests. Confirmed all three failed before the schema edit
(`TypeError`/`AttributeError` on the new fields) and pass after. Spot-checked
the raw JSON (`region.properties.valueStyle/labelStyle/deltaStyle`) to confirm
each is a bare `$ref` to `PresentationDeck-schema.json#/definitions/contentBlock/properties/style`
with no duplicated `properties` block, and confirmed `region.required == ["id"]`
(unchanged). `git status` after codegen showed drift limited to the two schema
files, the regenerated `Presentations.py`, and the new test file --
`generatePresentations.sh` untouched. `make uv-fullCheck` is green: flake8
clean, mypy strict clean (67 + 46 files), 942 tests passed, including the 3 new
ones, the 3 existing bullet/rhythm tests (chunk 02, unaffected), and the
pre-existing migration/type-shape tests that depend on the `Style` class name
staying stable. No open question; no gap.
