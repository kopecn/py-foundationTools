---
plan: PresentationsOverview
scope: project
status: pending
last_updated: 2026-08-23
semver: 0.0.3
author: Nicholas Bergantz
---

# Action Plan — Presentations Domain

## Goal

Make the four schemas in `schema/schemas/Presentations/` a linked, codegen-able family with a stdlib-only resolution layer, so a renderer in `py-clerical-tools` can construct real decks. Contract: [presentationSchema.md](../specs/presentationSchema.md).

This repository owns schema, types, and resolution. It never renders, and it never gains a dependency.

## Usability north star

A deck author names meaning — `accentBlue.accent`, `body`, `two-column` — and never a hex value or a coordinate. Swapping `theme.json` re-themes the deck.

## Gates

Four tiers, each independently functional, each ending in a revision point.

| tier | chunks | gate exit |
|---|---|---|
| 1 — MVP | 01–05 | Types generate and round-trip; resolvers correct; a real `.pptx` builds from the clerical side. **Gate 1 reached: chunks 01-05 complete and green.** Chunk 05 was unblocked by `fix-08` (`.claude/plans/fix-08-generated-guard-typeerror.md`), which rewrote every generated `from_dict`'s dict-type guard to raise `TypeError` instead of `AssertionError`, closing the cross-cutting `from_union` gap in `src/foundationTypes/data_model_helper.py` — see [05-presentation-type-tests.md](05-presentation-type-tests.md#resolution-notes). |
| 2 — narrative depth | 06–08 | Typed table/metric/chart, rich text, bullet levels |
| 3 — advanced | 09–11 | Versioning + migration; mermaid nucleation only |
| 4 — distribution | — | No foundation work; see the clerical plan set |

**Chunks 01–05 are fully specified. Chunks 06–11 are outlines by design** — each tier's gate is a revision point, and detailing tier 3 against layouts nobody has used yet would be writing fiction. Expand a tier's chunks to full executable form when its gate opens.

## Chunk dependency graph

```text
01 schema-linking
 └── 02 codegen ──┬── 03 resolvers ── 04 contrast
                  └────────────────────┴── 05 type-tests   [GATE 1]
                                            │
                       06 typed-blocks ─────┤
                       07 rich-text ────────┤
                       08 chart-spec ───────┘             [GATE 2]
                                            │
                       09 versioning ───────┤
                       10 migration ────────┤
                       11 mermaid-nucleus ──┘             [GATE 3]
```

## Conventions (every chunk)

1. **TDD** — failing test first, then implement, then the gate.
2. **Gate** — `make uv-fullCheck` (ruff + `mypy --strict` + pytest).
3. **Zero runtime deps** — `[project].dependencies` stays empty. `python-pptx` never appears here.
4. **Result objects, not exceptions**, for expected authoring errors.
5. **Spec is authoritative** — if implementation forces a contract change, update [presentationSchema.md](../specs/presentationSchema.md) in the same chunk and bump its semver.
6. **Stay in scope** — each chunk lists explicit out-of-scope items; do not fold adjacent work in.
7. **Frontmatter** — any created or edited managed markdown carries `last_updated` / `semver` / `author`.
8. **Test naming** — files `test*.py`, functions `test*`; generated models are tested with `unittest.TestCase` in `tests/typeTests/`, matching `testUnitSphericalArc.py`.
9. **Generated files are read-only** — a generated `.py` that fails the gate means the schema or the pipeline is wrong. Never hand-edit it.

## Chunk index

| # | chunk | tier | depends on |
|---|---|---|---|
| 01 | [presentation-schema-linking](01-presentation-schema-linking.md) | 1 | — |
| 02 | [presentation-codegen](02-presentation-codegen.md) | 1 | 01 |
| 03 | [presentation-resolvers](03-presentation-resolvers.md) | 1 | 02 |
| 04 | [theme-contrast-check](04-theme-contrast-check.md) | 1 | 02 |
| 05 | [presentation-type-tests](05-presentation-type-tests.md) | 1 | 03, 04 |
| 06 | [typed-content-blocks](06-typed-content-blocks.md) | 2 | gate 1 |
| 07 | [rich-text-and-bullets](07-rich-text-and-bullets.md) | 2 | 06 |
| 08 | [chart-spec](08-chart-spec.md) | 2 | 06 |
| 09 | [deck-versioning](09-deck-versioning.md) | 3 | gate 2 |
| 10 | [layout-migration](10-layout-migration.md) | 3 | 09 |
| 11 | [mermaid-nucleation](11-mermaid-nucleation.md) | 3 | 06 |

## Pending input

A prior working `python-pptx` deck script exists outside both repositories. If its path is supplied before chunk 01 runs, read it first: its real corporate RGB values, slide geometry, and actually-used block types are better evidence than anything inferred from the schemas. The plan does not block on it.
