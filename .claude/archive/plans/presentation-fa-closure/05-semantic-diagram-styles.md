---
human_ask: >
  a series of FA's was generated from the first use of the build presentation tool.
  please review:
  /Users/nbergantz/__Workspaces__/pythonWorkspaces/py-clerical-tools/.claude/fa_reports
  and create a series action plan on closing these gaps.
goal: >
  Add a typed diagram-style object whose colors are semantic theme references, plus a
  class→role map and a themeBinding opt-out.
last_updated: 2026-09-15
semver: 0.0.1
author: Nicholas Bergantz
status: completed
---

# F5 — Semantic diagram styles

Serves [Summary goal](./00-overview.md#summary-goal) · [Original ask](./00-original-ask.md).
Implements [presentationSchema.md](../../specs/presentationSchema.md) **R19**. Evidence:
`py-clerical-tools/.claude/fa_reports/FA-04-mermaid-theme-token-leakage.md`. Unblocks
clerical chunk 13. Reuses R4's color-reference enumeration.

## Deliverable

A typed diagram-style object (on the `mermaid` block, Deck schema) whose values are
**semantic theme references** (the same enumerated color addresses as R4), covering at
least background, primary/secondary/tertiary fill, border, text, line, error/success;
plus a bounded map from a custom node-class name to those semantic roles; plus a
`themeBinding` flag (`themed` default | `fixed`). Regenerated types + round-trip tests.

## Files

- `schema/schemas/Presentations/PresentationDeck-schema.json` — the diagram-style object +
  class→role map + `themeBinding`, referencing the color enumeration by `$ref`.
- `schema/scripts/generatePresentations.sh` — add the new object(s) to
  `CLASSES_FOR_BASE_PARENT`.
- `src/foundationTypes/presentationTypes/Presentations.py` — regenerated.
- `tests/test_presentation_diagram_styles.py` — new.

## Design constraints (decided here)

- **Semantic refs, not CSS:** values are theme color references (reuse the R4 enum /
  color-ref shape), never hex strings. This is the one normative `SHALL` among R15–R22.
- **Bounded class map:** class name → {fill, border, text} roles; no free-form string
  interpolation.
- `themeBinding` default `themed`; `fixed` is the explicit opt-out. `themed` default may
  be a declared `default` (R12 semver bump) or absence-means-themed documented in the
  description — prefer absence-means-themed to avoid a second default; state it in the
  description.
- Flat bag / no discriminated union (R9).

## TDD steps

1. Failing tests: `test_diagram_style_semantic_refs_roundtrip`,
   `test_class_role_map_roundtrip`, `test_theme_binding_fixed_roundtrip`,
   `test_diagram_refs_use_color_enumeration` (assert the refs are the R4 addresses),
   `test_existing_mermaid_block_still_valid`.
2. Edit schema; add base-parent entries; `make codegen-all`.
3. `make uv-fullCheck` green.

## Acceptance criteria

- [x] Diagram-style object + class map + themeBinding validate and round-trip.
- [x] Color values are semantic theme references (R4 enumeration), no hex.
- [x] Existing mermaid blocks still valid.
- [x] `make codegen-all` clean; `make uv-fullCheck` green.

## Out of scope

- Resolving refs into an mmdc config and the retheme regression (clerical chunk 13).

## Ask ↔ result

`human_ask` (recorded, planning-only) asked to review the clerical FA reports and create
an action plan closing the gaps; that ask authorized planning, not this implementation.
The live `/execute-plan` command in this session explicitly authorized executing this
chunk now. `goal` — add a typed diagram-style object whose colors are semantic theme
references, plus a class→role map and a themeBinding opt-out — matches R19's text
exactly; no divergence found between `human_ask`, `goal`, and R19, so no stop condition
applied.

Implemented exactly what R19 and this chunk specify: `diagramStyle` (on the `mermaid`
arm of `contentBlock`) carries `background`, `primaryFill`, `secondaryFill`,
`tertiaryFill`, `border`, `text`, `line`, `error`, `success` — each a bare `$ref` to
`PresentationSlideLayouts-schema.json#/definitions/themeColorRef` (R4's existing
enumeration, reused, not re-declared) — plus `classRoles` (a bounded map from a custom
node-class name to a `diagramClassRole` of `fill`/`border`/`text`, each the same
`themeColorRef` $ref) and `themeBinding` (`themed` | `fixed`, no default, absence
documented as meaning `themed` per R12 guidance to avoid a second semver bump). Verified
directly in the raw schema JSON (`test_diagram_refs_use_color_enumeration`) that every
one of these color properties is a bare `$ref` to the R4 enumeration with no `enum` or
hex/CSS literal anywhere in either new definition.
