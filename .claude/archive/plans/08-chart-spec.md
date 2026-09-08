---
plan: ActionPlan08ChartSpec
scope: project
status: completed
last_updated: 2026-08-28
semver: 1.2.0
author: Nicholas Bergantz
---

# 08 — minimal chart specification

Define a small typed chart payload sufficient for common narrative-deck data and
semantic theme colors. Select the first supported chart kinds from real use at the
level-1 revision gate and require downstream renderability before adding an arm.

Advanced axes, labels, dual scales, trend lines, and a general visualization grammar
are out of scope.

## What shipped

Placeholder `chart` arm, flat siblings per spec R9:

- `schema/schemas/Presentations/PresentationDeck-schema.json`
  - `contentBlock.type` enum gains `chart` → `["text","bullets","metric","table","chart"]`.
  - `chartSeries` definition: `name` (required), `values` (required `array` of number),
    optional `color` (`themeColorRef` into `PresentationColorTheme`).
  - `contentBlock.chartKind`: enum `["bar", "line"]` — placeholder set.
  - `contentBlock.series`: optional `array` of `chartSeries`.
  - `contentBlock.categories`: optional `array` of string (shared x-axis labels).
- `schema/scripts/generatePresentations.sh` — `ChartSeries` added to `CLASSES_FOR_BASE_PARENT`.
- `src/foundationTypes/presentationTypes/Presentations.py` — regenerated. New `ChartKind`
  enum and `ChartSeries` dataclass; `ContentBlock` gains `chart_kind` / `series` /
  `categories` (wire keys `chartKind` / `series` / `categories`).
- Tests: shared with chunk 07 —
  `test_presentation_schema_shape.py::test_content_block_rich_text_and_chart_payload_fields_present`
  and `test_content_block_type_enum_includes_metric_table_chart`;
  `testPresentationDeck.py` `_rich_text_chart_deck_dict` covers a `bar` chart with two
  series (one themed, one uncolored), `from_dict` assertions, round-trip case.

Gate after: `make uv-fullCheck` clean, 485 tests.

## Acceptance

- [x] Small typed chart payload: kind + named numeric series + optional categories.
- [x] Series color is a semantic `PresentationColorTheme` ref, not a literal color.
- [x] `chartKind` limited to a placeholder set (`bar`, `line`); widen only on renderability.
- [x] Round-trips through the generated model (`to_dict` → `from_dict` → `to_dict` equality).
- [x] No new runtime dependency; no chart rendering added here.
- [x] `make uv-fullCheck` passes.

## Ask ↔ result

`human_ask`: "do 07 and 08 the same way" — random placeholder meeting the basic
necessities. Delivered exactly that. "Downstream renderability before adding an arm"
(chunk text) is a py-clerical-tools concern; not gated here per the chunk's own
"schema/codegen/test result only" scope.
