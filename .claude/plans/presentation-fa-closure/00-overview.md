---
human_ask: >
  a series of FA's was generated from the first use of the build presentation tool.
  please review:
  /Users/nbergantz/__Workspaces__/pythonWorkspaces/py-clerical-tools/.claude/fa_reports
  and create a series action plan on closing these gaps.
goal: >
  Add the typed Presentations schema fields (R15–R22) the downstream deck renderer needs
  to close the FA gaps, additively and codegen-clean.
last_updated: 2026-09-23
semver: 0.1.0
author: Nicholas Bergantz
status: in_progress
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
and optional, so existing decks still validate and round-trip. The implemented contracts
are [presentationSchema.md](../../specs/presentationSchema.md) R15–R22. Repository
artifacts record an FA-closure gate, but do not preserve independent evidence of that
human approval.

**Success condition:** each chunk's acceptance boxes pass, `make codegen-all` regenerates
cleanly, and both `make fullCheck` and `make uv-fullCheck` are green.

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
- **Gate:** `make codegen-all` clean, then both `make fullCheck` and `make uv-fullCheck`
  green (flake8 → `mypy --strict` → pytest; the uv runner uses `DEFAULT_PYTHON` 3.13).
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
defines `preferredAspectRatio` once and 06 shares that same region property (land 04
before 06, or land the shared field in whichever comes first).

## Corrective actions — 2026-09-23

Post-audit verdict: the seven original chunks are substantially complete, code generation is reproducible, and both repository gates pass. Three source-supported corrections remain. The current live post-audit request authorizes corrective planning; unresolved contract choices and downstream-only findings remain recorded without executable requirements.

### Corrective index

| # | chunk | origin | dependency |
|---|---|---|---|
| 08 | [export media-fit public API](08-export-media-fit-api.md) | PA-01 | none |
| 09 | [close presentation regression coverage](09-presentation-regression-coverage.md) | PA-02 | none |
| 10 | [align presentation and codegen documentation](10-documentation-convention-alignment.md) | PA-03–PA-08 | 08, 09 |

### Corrective dependency graph

```text
08 export media-fit API ──┐
                         ├──> 10 documentation/convention alignment
09 regression coverage ──┘
```

### Findings → chunks

| finding | confirmed evidence | disposition |
|---|---|---|
| PA-01 | `image_fit.py` declares four public helpers, while `foundation_tools.presentation` exports only `fit_into_box`; a fresh-interpreter probe confirmed the other three are absent | chunk 08 |
| PA-02 | R15–R22 tests prove valid generated-model round trips but leave several raw schema constraints, exact cover crop fractions, and externally consumed generated class names without durable regression assertions | chunk 09 |
| PA-03 | `presentationSchema.md` still states that no implementation or codegen package exists and labels implemented FA additions as pending | chunk 10 |
| PA-04 | `schemaCodegen.md` prescribes the removed `run_ruff` pipeline while the canonical scripts and project instructions use `run_black` | chunk 10 |
| PA-05 | both governing specs lack the required spec frontmatter keys and an explicit Goal or Scope section | chunk 10 |
| PA-06 | R18/R20 require `preferredAspectRatio` to be “defined once and `$ref`’d,” although both requirements use the same property on the same `region` object and the implementation correctly has one declaration | chunk 10 |
| PA-07 | R18 says all geometry math lives downstream, conflicting with the source-authorized image plan and implemented ownership of pure geometry in this repository | chunk 10 |
| PA-08 | R22 describes all core-property fields as additive and optional although `description`, `author`, and `version` predate R22 with their existing required/default behavior; only `keywords` was added | chunk 10 |

### Recorded, no action

| finding | disposition |
|---|---|
| NA-01 — Zero or negative dimensions expose undefined media-fit behavior; zero intrinsic dimensions can raise `ZeroDivisionError` | Open. The plan says “total” but defines no invalid-input result or error contract. Do not invent one in a corrective chunk. |
| NA-02 — Unknown `diagramStyle` and `diagramClassRole` keys are silently discarded by generated parsing | Open. “Bounded” constrains role values but does not authorize object closure or a class-name grammar. |
| NA-03 — Generated parsers enforce Python types but not JSON Schema numeric bounds | Resolved, no foundation change: the human decision preserved in [fix-17](../../archive/plans/repository-hardening/fix-17-presentation-schema-runtime-contract.md) makes JSON Schema authoritative, generated models typed representations rather than validators, and validation an application-boundary responsibility. |
| NA-04 — Exact `role`, `purpose`, and `density` vocabularies include agent-derived choices | Unsupported/open. Do not tighten or widen them without a human decision. |
| NA-05 — Focal-point application, bullet/rhythm consumption, capacity lint, and Mermaid default-placement coverage live in `py-clerical-tools` | Outside this repository and explicitly outside the foundation chunks. |
| NA-06 — Chunks 03, 06, and 07 touched necessary schema files omitted from their original file lists | Historical scope-record defect; implementation was goal-related and no corrective code change is warranted. |
| NA-07 — The original planning ask is preserved, but the later implementation command and scope-gate approval are only recorded by agent-authored artifacts | Authorization remains unverified from repository evidence. This audit does not retroactively assert it. |
