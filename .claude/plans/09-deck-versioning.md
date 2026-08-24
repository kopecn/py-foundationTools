---
plan: ActionPlan09DeckVersioning
scope: project
status: outline
last_updated: 2026-08-23
semver: 0.0.1
author: Nicholas Bergantz
---

# 09 — Deck Versioning (tier 3)

> **Outline.** Expand at gate 2.

## Goal

Give a deck a record of what it was built against, so migration has something to reason about. This is the deferred cost from tier 1 coming due.

## Sketch

- `theme.json` and `layouts.json` each gain `id` and `version` (semver).
- `deck.json` gains `builtAgainst: {themeId, themeVersion, layoutsId, layoutsVersion}`.
- `slide.id` becomes required and stable — migration needs slide identity that survives reordering.
- A theme/layout registry: a directory of named corporate standards the deployer can pull from.

## Known cost

Every deck authored between gate 1 and here predates these fields and needs migrating. That was the accepted trade when versioning was deferred. This chunk therefore ships a one-time upgrade path for unversioned decks, defaulting them to the earliest known standard.

## Out of scope

The migration engine itself (chunk 10).
