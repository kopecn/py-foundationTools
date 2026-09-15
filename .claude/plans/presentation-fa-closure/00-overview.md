---
human_ask: >
  a series of FA's was generated from the first use of the build presentation tool.
  please review:
  /Users/nbergantz/__Workspaces__/pythonWorkspaces/py-clerical-tools/.claude/fa_reports
  and create a series action plan on closing these gaps.
goal: >
  Add the typed Presentations schema fields (R15–R22) the downstream deck renderer needs
  to close the FA gaps, additively and codegen-clean.
last_updated: 2026-09-14
semver: 0.0.1
author: Nicholas Bergantz
status: pending
---

# FA-closure — foundation (schema) series

## Summary goal

The downstream deck builder cannot fully close the 2026-09-14 visual-quality audit
without typed schema fields to consume: a responsive fit budget, bullet/metric/rhythm
tokens, media fit modes and region aspect/fill, semantic diagram styles, layout capacity
and roles, accessibility fields, and document metadata. This series adds those fields to
the four Presentations schemas, regenerates the types, and resolves them in the stdlib
layer.

**Scope boundary:** schema JSON + codegen + stdlib resolution + round-trip tests only.
This repo renders nothing and depends on no downstream code. Every addition is additive
and optional, so existing decks still validate and round-trip. The contracts are
[presentationSchema.md](../../specs/presentationSchema.md) R15–R22, accepted at the
FA-closure gate.

**Success condition:** each chunk's acceptance boxes pass, `make codegen-all` regenerates
cleanly, and `make uv-fullCheck` is green.

## Original ask

Preserved verbatim in [00-original-ask.md](./00-original-ask.md), with the scope split.

## Downstream coupling

These chunks unblock the foundation-dependent clerical chunks in
`py-clerical-tools/.claude/plans/fa-closure/`. Cross-repo edges (this series → clerical):

```text
F1 (01) → clerical 10 responsive shrink
F2 (02) → clerical bullets/rhythm token upgrade
F3 (03) → clerical 11 metric roles
F4 (04) → clerical 12 fit-mode placement, 14 media lint
F5 (05) → clerical 13 theme-bound diagram color
F6 (06) → clerical 14 capacity lint, reading order
F7 (07) → clerical 15 accessibility + metadata
```

Land and publish (release/tag per this repo's dependency BKM) each F chunk before the
clerical chunk that depends on it starts; the clerical repo co-develops against the
editable sibling.

## Conventions every chunk inherits

- **TDD:** write the failing round-trip/validation test first.
- **Codegen is the pipeline:** edit the JSON schema(s) under
  `schema/schemas/Presentations/`, then `make codegen-all` regenerates
  `src/foundationTypes/presentationTypes/Presentations.py`. Do **not** hand-edit the
  generated file. New nested objects that should inherit `DataModelHelper` are added to
  `CLASSES_FOR_BASE_PARENT` in `schema/scripts/generatePresentations.sh`.
- **Gate:** `make codegen-all` clean, then `make uv-fullCheck` green (flake8 → `mypy
  --strict` → pytest on `DEFAULT_PYTHON` 3.13).
- **Additive & optional:** no field is `required`; enum widenings only (non-breaking per
  R7). Assert an existing deck still validates and round-trips.
- **No defaults unless the spec says so:** adding a JSON Schema `default` is a contract
  change and bumps `presentationSchema.md` semver (R12). Only R18's `fit=contain` default
  is declared; keep all other new fields default-less.
- **Test naming:** files `test_*.py`, snake_case functions (existing convention, e.g.
  `test_presentation_resolvers.py`), under `tests/`.
- **Zero runtime dependencies** stays inviolate; resolution is stdlib-only, total
  functions, no I/O.
- **Frontmatter:** every chunk carries `last_updated`/`semver`/`author` + `status`, plus
  `human_ask` (copied from this overview) and a one-line `goal`.

## Chunk index

| # | chunk | spec | target schema |
|---|---|---|---|
| 01 | [responsive fit budget](01-responsive-fit-budget.md) | R15 | SlideLayouts (region) |
| 02 | [bullet + rhythm tokens](02-bullet-rhythm-tokens.md) | R16 | Deck (bullets), SlideLayouts (region) |
| 03 | [metric role styles](03-metric-role-styles.md) | R17 | SlideLayouts (region) |
| 04 | [media fit + aspect geometry](04-media-fit-aspect.md) | R18 | Deck (block), SlideLayouts (region) + `fit_into_box` |
| 05 | [semantic diagram styles](05-semantic-diagram-styles.md) | R19 | Deck (mermaid block) → theme refs |
| 06 | [layout capacity + roles](06-layout-capacity-roles.md) | R20 | SlideLayouts (region + layout) |
| 07 | [accessibility + metadata](07-accessibility-metadata.md) | R21, R22 | Deck (block, metadata) |

Chunks are mutually independent except: 05 reuses R4's color-reference enumeration; 04
defines `preferredAspectRatio` once and 06 `$ref`s it (land 04 before 06, or land the
shared field in whichever comes first).
