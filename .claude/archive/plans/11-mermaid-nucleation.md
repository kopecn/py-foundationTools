---
plan: ActionPlan11MermaidNucleation
scope: project
status: completed
last_updated: 2026-09-04
semver: 1.1.0
author: Nicholas Bergantz
---

# 11 — Mermaid nucleation point

Add the smallest typed attachment point for Mermaid source after the level-2 gate. Its
purpose is to reserve an agreed cross-repository shape for later growth, as explicitly
requested; descriptions must clearly state whether rendering is available.

Parsing, layout, image generation, CLI behavior, dependencies, and a full Mermaid
renderer are deliberately not scoped here.

## Ask ↔ result

**Objective:** deliver the tier-3 gate item "Mermaid has a bounded schema attachment
point" (`00-overview.md`) — a typed place to store Mermaid diagram source, reserving a
cross-repository shape for later growth, without building any rendering.

**Live request:** `/execute-plan 9-13` per tier 3 on `00-overview.md`, with explicit
authorization to make the minimal design decision this stub required.

**Design decision made (smallest usable form):**

- `contentBlock.type` enum gains one member: `"mermaid"`, appended after `"chart"` —
  `["text","bullets","metric","table","chart","mermaid"]`.
- One new sibling field, `contentBlock.mermaidSource` (string, default `""`), carries
  the raw Mermaid diagram source text — mirrors exactly how `text` serves a `text`
  block. No `diagramKind`, no node/edge structure, no second field.
- The `type` enum's shared description and `mermaidSource`'s own description both
  state plainly that this repository stores the source only and does not parse, lay
  out, or render it — rendering, if it ever exists, is a downstream/clerical-tools
  concern. This is a deliberate, narrow exception to `presentationSchema.md` R7's
  "every arm must be renderable" rule, recorded as new R14 (semver 0.5.0 → 0.6.0),
  citing this chunk and the overview's tier-3 gate line as the authorizing source.

**Delivered files:**

- `schema/schemas/Presentations/PresentationDeck-schema.json` — enum + `mermaidSource`.
- `src/foundationTypes/presentationTypes/Presentations.py` — regenerated
  (`ContentType.MERMAID`, `ContentBlock.mermaid_source`); no other class/enum changed.
- `tests/typeTests/test_presentation_schema_shape.py` — enum assertion updated;
  new `test_content_block_mermaid_payload_field_present`.
- `tests/typeTests/testPresentationDeck.py` — `_mermaid_deck_dict`, new
  `test_from_dict_builds_mermaid_block`, added to the round-trip case table.
- `.claude/specs/presentationSchema.md` — new R14, semver bump.

**Gate:** `make uv-fullCheck` clean, 543 tests.

**Gap/deferral:** none beyond what the chunk explicitly excludes (parsing, layout,
image generation, CLI, dependencies, rendering) — all untouched, as scoped.
