---
plan: ActionPlan06TypedContentBlocks
scope: project
status: completed
last_updated: 2026-08-28
semver: 1.2.0
author: Nicholas Bergantz
---

# 06 — typed narrative content blocks

Add the smallest strict payloads needed for metric and table content, then regenerate
the presentation models and prove round-trip behavior. Choose field shapes from real
deck examples at the level-1 revision gate; do not predesign a general table system.

The gate is a schema/codegen/test result only. Rendering, merged cells, conditional
formatting, and layout libraries are out of scope in this repository.

## What shipped

Placeholder field shapes, chosen from an inlined representative deck
(`_metric_table_deck_dict` in `testPresentationDeck.py`): a KPI row of `metric`
blocks and a pipeline `table`. Good enough to unblock 07–08; revisit if a real
deck example contradicts them.

- `schema/schemas/Presentations/PresentationDeck-schema.json` — `contentBlock.type`
  enum extended to `["text", "bullets", "metric", "table"]`; flat sibling fields
  added per spec R9 (no nested payload objects, no new dataclasses):
  - `metric`: `value` (pre-formatted string), `label` (string), `delta` (optional string)
  - `table`: `rows` (row-major `array` of `array` of string), `headers` (optional `array` of string)
- `src/foundationTypes/presentationTypes/Presentations.py` — regenerated via
  `generatePresentations.sh`. `ContentType` gains `METRIC`/`TABLE`; `ContentBlock`
  gains `delta`/`headers`/`label`/`rows`/`value` as `... | None`. No change to
  `CLASSES_FOR_BASE_PARENT` (all payloads are primitives / `list[list[str]]`).
- `.claude/specs/presentationSchema.md` R7 — synced to record the tier-2 enum and
  the two flat payloads. R7 already anticipated this ("Adding an enum value later
  is a non-breaking schema change"). semver 0.2.0 → 0.3.0.
- Tests:
  - `tests/typeTests/test_presentation_schema_shape.py` — enum assertion updated;
    `data` bag + `chart`/`image`/`quote` still guarded absent; new assertion for
    the five flat payload fields and their `items` shapes.
  - `tests/typeTests/testPresentationDeck.py` — `_metric_table_deck_dict` fixture,
    `test_from_dict_builds_metric_and_table_blocks`, and `metric_table` added to
    the round-trip case set.

Gate after: `make uv-fullCheck` clean, 483 tests.

## Acceptance

- [x] `metric` and `table` arms present in the schema enum with flat payloads (R9).
- [x] Generated model round-trips a deck containing both arms (`to_dict` → `from_dict`
      → `to_dict` equality).
- [x] No new runtime dependency; no PowerPoint rendering added here.
- [x] `make uv-fullCheck` passes.

## Ask ↔ result

`human_ask`: open Level 2 — "throw some spaghetti on the wall", a random placeholder
meeting the basic necessities.

Delivered exactly that: smallest flat `metric` + `table` payloads (strings; formatting
is a renderer concern), regenerated model, round-trip proof, spec R7 sync, gate green.
No real deck example exists (deleted by `c78008a`, not to be restored) — the inlined
stand-in is the accepted placeholder.
