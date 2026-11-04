---
plan: ActionPlan07RichTextAndBullets
scope: project
status: completed
last_updated: 2026-08-28
semver: 1.2.0
author: Nicholas Bergantz
---

# 07 — rich text and structured bullets

Add a minimal typed run model for emphasis and a bounded bullet level so narrative
slides can express structure without literal formatting decisions. Final fields and
limits are chosen from actual authored decks when this plan opens.

Paragraph layout, tab stops, font metrics, automatic shrinking, and per-run font
families are out of scope unless usage proves they are required.

## What shipped

Placeholder shapes, additive to the existing `text`/`bullets` arms (no existing
field changed shape):

- `schema/schemas/Presentations/PresentationDeck-schema.json`
  - `textRun` definition: `text` (required string) + optional `bold` / `italic` booleans.
  - `contentBlock.runs`: optional `array` of `textRun` — inline emphasis for a `text`
    block; renderer uses these instead of the flat `text` string when present.
  - `contentBlock.bulletLevels`: optional `array` of integer, `minimum` 0 / `maximum` 4 —
    per-entry indent level parallel to `items`; short array leaves the tail at level 0.
- `schema/scripts/generatePresentations.sh` — `TextRun` added to `CLASSES_FOR_BASE_PARENT`.
- `src/foundationTypes/presentationTypes/Presentations.py` — regenerated. New `TextRun`
  dataclass; `ContentBlock` gains `runs` / `bullet_levels` (wire keys `runs` / `bulletLevels`).
- Tests: `test_presentation_schema_shape.py::test_content_block_rich_text_and_chart_payload_fields_present`;
  `testPresentationDeck.py` `_rich_text_chart_deck_dict` fixture, `from_dict` test, round-trip case.

Gate after: `make uv-fullCheck` clean, 485 tests.

## Acceptance

- [x] Typed run model with emphasis, no literal formatting values.
- [x] Bullet level bounded 0–4 in the schema.
- [x] Round-trips through the generated model (`to_dict` → `from_dict` → `to_dict` equality).
- [x] No new runtime dependency; no rendering added here.
- [x] `make uv-fullCheck` passes.

## Ask ↔ result

`human_ask`: "do 07 and 08 the same way" — random placeholder meeting the basic
necessities. Delivered exactly that; no real authored deck exists to tune against.
