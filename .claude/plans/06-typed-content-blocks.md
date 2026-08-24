---
plan: ActionPlan06TypedContentBlocks
scope: project
status: outline
last_updated: 2026-08-23
semver: 0.0.1
author: Nicholas Bergantz
---

# 06 — Typed Content Blocks (tier 2)

> **Outline.** Expand to full executable form when gate 1 opens. Detailing it now would be writing against layouts nobody has used yet.

## Goal

Return `metric` and `table` to `contentBlock.type`, each with a payload that can actually express it — the condition chunk 01 set for an arm to exist.

## Sketch

- `metric`: `value` (string or number), `label`, optional `caption`. Trivial; the layout region already carries the large font size.
- `table`: `rows` (array of arrays of cell objects), `header` (bool), optional `columnWidths` (px, summing to the region width), per-cell optional `color` (`themeColorRef`) and `bold`. No merges in tier 2 — they are where table models get complicated, and nothing has asked for them.
- Restore `metric-and-body` and `table` layouts from `schema/examples/Presentations/layouts-deferred.json`.
- Flat optional-bag only; no discriminated unions ([schemaCodegen.md](../specs/schemaCodegen.md)).

## Open at gate

Whether `columnWidths` is px or proportional. Proportional survives a region resize; px matches every other coordinate in the domain. Decide from how layouts are actually being edited by then.

## Out of scope

Charts (chunk 08), images, rich text (chunk 07).
