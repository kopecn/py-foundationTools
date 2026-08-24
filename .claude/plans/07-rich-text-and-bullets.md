---
plan: ActionPlan07RichTextAndBullets
scope: project
status: outline
last_updated: 2026-08-23
semver: 0.0.1
author: Nicholas Bergantz
---

# 07 — Rich Text and Bullet Levels (tier 2)

> **Outline.** Expand at gate 1.

## Goal

Let a sentence carry emphasis and a bullet list carry structure — the minimum for a deck that argues rather than lists.

## Sketch

- A `run` type: `text` plus optional `bold`, `italic`, `underline`, `color` (`themeColorRef`), `fontSize`, `hyperlink`.
- `contentBlock.runs[]` as an alternative to `contentBlock.text`. Both present is an authoring error the consumer reports; the schema cannot express the exclusion without a union.
- `bullets` items gain an optional `level` (0-based, cap at 4 — deeper nesting is unreadable on a slide).
- `overflow: "shrink"` becomes expressible now that runs carry explicit sizes.

## Open at gate

Whether `shrink` is worth implementing at all. It needs font metrics to be honest, and the alternative — reporting overflow at `validate` time and letting the author fix it — may be both simpler and better.

## Out of scope

Paragraph spacing, indent control, tab stops, per-run fonts.
