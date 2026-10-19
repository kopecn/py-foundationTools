---
human_ask: >
  a series of FA's was generated from the first use of the build presentation tool.
  please review:
  /Users/nbergantz/__Workspaces__/pythonWorkspaces/py-clerical-tools/.claude/fa_reports
  and create a series action plan on closing these gaps.
goal: >
  Add the responsive fit budget to the region schema — overflow `shrink`, minFontSize,
  maxLines, scaleLadder — additive and codegen-clean.
last_updated: 2026-09-15
semver: 0.0.1
author: Nicholas Bergantz
status: completed
---

# F1 — Responsive fit budget

Serves [Summary goal](./00-overview.md#summary-goal) · [Original ask](./00-original-ask.md).
Implements [presentationSchema.md](../../specs/presentationSchema.md) **R15**. Evidence:
`py-clerical-tools/.claude/fa_reports/FA-01-deterministic-text-bounds.md`. Unblocks
clerical chunk 10.

## Deliverable

`region` (in `PresentationSlideLayouts-schema.json`) gains: the `overflow` enum value
`shrink` (deferred in R8, now activated), and optional `minFontSize` (number, pt),
`maxLines` (integer ≥ 1), `scaleLadder` (array of descending numbers, pt). Regenerated
types + round-trip tests. No defaults.

## Files

- `schema/schemas/Presentations/PresentationSlideLayouts-schema.json` — add the `overflow`
  enum member and the three optional properties, each with a `description` (they become
  docstrings, per R1).
- `src/foundationTypes/presentationTypes/Presentations.py` — regenerated via
  `make codegen-all` (do not hand-edit).
- `tests/test_presentation_responsive_budget.py` — new.

## Design constraints (decided here)

- Additive/optional; not in any `required` list; no `default`.
- `overflow` currently has `wrap`/`clip`; add `shrink` as a third enum member.
- `scaleLadder` items are numbers; the schema does not enforce descending order (a
  consumer/lint concern) but the `description` states the intent.
- Cross-file `$ref` by bare filename only if reused; these live inline on `region`.

## TDD steps

1. Failing tests:
   - `test_region_accepts_shrink_and_budget` — a region with `overflow: shrink`,
     `minFontSize`, `maxLines`, `scaleLadder` validates and round-trips
     (`to_dict`→`from_dict` lossless).
   - `test_existing_region_still_valid` — a region without the new fields still validates
     and round-trips (regression).
2. Edit schema; `make codegen-all`; implement/adjust resolution if the resolver surfaces
   region fields.
3. `make uv-fullCheck` green.

## Acceptance criteria

- [x] `overflow: shrink` + budget fields validate and round-trip losslessly.
- [x] Existing decks/layouts still validate (no field required, no default).
- [x] `make codegen-all` regenerates cleanly; generated file not hand-edited.
- [x] `make uv-fullCheck` green.

## Out of scope

- Any shrink *computation* — that is the downstream renderer (clerical chunk 10).
- Bullet/rhythm/metric fields (chunks 02, 03).

## Ask ↔ result

**Objective (`human_ask`/`goal`):** the `human_ask` recorded on this chunk and the
series overview is planning-only — review the `py-clerical-tools` FA reports and
produce an action plan closing the gaps. This chunk's own `goal` narrows that to one
concrete deliverable: add the responsive fit budget (`overflow: shrink`,
`minFontSize`, `maxLines`, `scaleLadder`) to `region` in
`PresentationSlideLayouts-schema.json`, additively, per R15.

**Live authorization:** the live command `/execute-plan
.claude/plans/presentation-fa-closure` explicitly authorized implementing chunk 01
now — a live execution request, not a conflict with the recorded planning-only
`human_ask` (per the chunk's own instructions, execution authorization can be given
separately from the original planning ask).

**Delivered:** added the `shrink` enum member to `region.overflow` and three new
optional `region` properties (`minFontSize: number`, `maxLines: integer, minimum 1`,
`scaleLadder: array<number>`), each with a `description`, in
`schema/schemas/Presentations/PresentationSlideLayouts-schema.json`. No field was
added to any `required` list; no `default` was added. Regenerated
`src/foundationTypes/presentationTypes/Presentations.py` via `make codegen-all`
(not hand-edited) — the diff is limited to the `Overflow` enum gaining `SHRINK` and
`Region` gaining `max_lines`/`min_font_size`/`scale_ladder` as `Optional` fields with
`from_dict`/`to_dict` support. Added
`tests/test_presentation_responsive_budget.py` with the two TDD-specified tests
(`test_region_accepts_shrink_and_budget`, `test_existing_region_still_valid`);
confirmed both failed before the schema edit and pass after. No nested object type
was introduced, so `CLASSES_FOR_BASE_PARENT` in
`schema/scripts/generatePresentations.sh` required no change.

**Gap:** none identified against the chunk as written. Shrink computation itself
remains explicitly out of scope (downstream renderer, clerical chunk 10), as stated
above.
