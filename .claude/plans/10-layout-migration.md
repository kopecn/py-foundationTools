---
plan: ActionPlan10LayoutMigration
scope: project
status: outline
last_updated: 2026-08-23
semver: 0.0.1
author: Nicholas Bergantz
---

# 10 — Layout Migration (tier 3)

> **Outline.** Expand at gate 2.

## Goal

Re-point an old deck at the current corporate standard: `migrate(deck, target_layouts) -> MigrationResult`. Pure, stdlib-only.

## Sketch

- Colors need no migration — content names theme properties, so a new `theme.json` already applies. This is the payoff of R4 and worth stating plainly: **re-theming is free; only layout drift needs work.**
- Layout migration is a remap of layout ids and region ids. A remap table ships alongside each layouts version.
- Unmappable content is reported, never dropped. A block whose region no longer exists surfaces in the result with its slide number and text, for a human to place.
- Migration is a pure function over models; writing files back is the CLI's job.

## Open at gate

Whether remap tables are hand-authored per version bump or inferred by matching region `type` and geometry. Inference is seductive and probably wrong.

## Out of scope

Rendering, file I/O, any interactive conflict resolution.
