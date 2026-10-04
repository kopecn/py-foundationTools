---
human_ask: >
  a series of FA's was generated from the first use of the build presentation tool.
  please review:
  /Users/nbergantz/__Workspaces__/pythonWorkspaces/py-clerical-tools/.claude/fa_reports
  and create a series action plan on closing these gaps.
goal: >
  Add machine-readable layout capacity, occupancy, semantic roles, and density to the
  region/layout schema.
last_updated: 2026-09-15
semver: 0.0.2
author: Nicholas Bergantz
status: completed
---

# F6 — Layout capacity + roles

Serves [Summary goal](./00-overview.md#summary-goal) · [Original ask](./00-original-ask.md).
Implements [presentationSchema.md](../../specs/presentationSchema.md) **R20**. Evidence:
`py-clerical-tools/.claude/fa_reports/FA-05-layout-contract-and-authoring-skill.md`.
Unblocks clerical chunk 14 (capacity/media lint + reading order). **Land after F4**
(reuses its `preferredAspectRatio`).

## Deliverable

A `region` (SlideLayouts) gains verifiable capacity/intent fields, each with a named
downstream consumer (per R20): `allowedContentTypes`, occupancy (`required` |
`recommended` | `optional`), `maxLines`, `maxCharacters`, `maxItems`,
`maxCharactersPerItem`, `preferredAspectRatio` (`$ref` to F4's canonical definition), and
a semantic `role`. A layout gains an optional `purpose`/tag set and `density` class.

## Files

- `schema/schemas/Presentations/PresentationSlideLayouts-schema.json` — region capacity +
  role fields; layout purpose/density. `preferredAspectRatio` via `$ref` to F4.
- `src/foundationTypes/presentationTypes/Presentations.py` — regenerated.
- `tests/test_presentation_layout_capacity.py` — new.

## Design constraints (decided here)

- Only verifiable constraints (R20): every field maps to a named consumer — capacity to
  clerical lint, `role` to renderer reading-order/shape-identity, `purpose`/`density` to
  the authoring skill. Qualitative guidance stays in human notes (not schema).
- `role` and occupancy are enums with descriptive docstrings.
- Reuse F4's `preferredAspectRatio` by `$ref`; do not re-declare.
- All optional; no defaults.

## TDD steps

1. Failing tests: `test_region_capacity_roundtrip`, `test_occupancy_and_role_enums`,
   `test_layout_purpose_density_roundtrip`, `test_preferred_aspect_ref_shared`
   (assert the field is the same definition as F4, not a copy),
   `test_existing_layout_still_valid`.
2. Edit schema; `make codegen-all`.
3. `make uv-fullCheck` green.

## Acceptance criteria

- [x] Capacity/occupancy/role + layout purpose/density validate and round-trip.
- [x] `preferredAspectRatio` is shared via `$ref` with F4 (single definition).
- [x] Existing layouts still valid; no defaults.
- [x] `make codegen-all` clean; `make uv-fullCheck` green.

## Ask ↔ result

- **Ask (R20 + design constraints):** add region capacity/occupancy/role fields and
  layout purpose/density; reuse F4's `preferredAspectRatio` via `$ref`, never
  redeclaring it.
- **Result — `preferredAspectRatio`:** already the single declaration on `region`
  (added by chunk 04, on the same object R20 targets). No second declaration or `$ref`
  was added or needed; `grep -c '"preferredAspectRatio":'` on the schema file returns
  `1`, and `test_preferred_aspect_ref_shared` asserts this by reading the schema file
  directly.
- **Result — `maxLines` collision (not explicitly addressed by the chunk):** R20 lists
  `maxLines` as one of its own capacity fields, but `region` already carries a
  `maxLines` property from R15 (chunk 01, responsive-fit shrink budget) with a
  different named consumer (the renderer's shrink logic vs. R20's design-lint tier).
  JSON Schema (and the generated dataclass) cannot hold two properties of the same
  name on the same object, so a second declaration was never possible. Resolution:
  the existing R15 `maxLines` field now serves both consumers — its description was
  extended to name the design-lint consumer, no new field was added. This mirrors the
  `preferredAspectRatio` shared-field pattern one level further than the chunk spelled
  out; flagging it here since it wasn't explicit in the chunk text.
- **Result — `allowedContentTypes`:** items `$ref` `PresentationDeck-schema.json#/definitions/contentBlock/properties/type`
  per spec Design Goal 3 ("one definition per concept... never a re-declaration").
  quicktype only converges cross-references onto one generated class when the
  referenced node carries an explicit `title` (the existing `Style` reuse for
  `valueStyle`/`labelStyle`/`deltaStyle` already relies on this); the `type` property
  on `PresentationDeck-schema.json`'s `contentBlock` had none, so referencing it
  first produced a second, differently-named enum class (`PresentationDeckSchema`)
  duplicating `ContentType`'s values, and inlining the enum literal instead caused
  quicktype to rename unrelated existing classes (`ContentType`→`TypeElement`,
  `RegionType`→`PurpleType`) via its collision-disambiguation heuristic — a
  regression to already-committed, tested types. Fix: added `"title": "ContentType"`
  to that one property node in `PresentationDeck-schema.json` (a metadata-only
  addition, no value change) so codegen converges both usages onto the existing
  `ContentType` class. This is the one file touched outside the chunk's declared
  `Files` list — a targeted, non-semantic addition, not a new declaration.
- **Correction — `RegionType` rename was NOT harmless (supervision blocker):**
  the initial pass above assessed the `RegionType`→`TypeEnum` rename as harmless
  because nothing in *this* repo imports `RegionType` by name. That check was
  incomplete: the downstream consumer `py-clerical-tools` (`deck_builder/renderer.py`,
  `.../validation.py`) imports `RegionType` by name and uses it heavily
  (`RegionType.BODY`, `.TITLE`, `.COLUMN`, etc.), so the rename would have broken
  that consumer on the next sibling sync — a cross-repo regression this repo's own
  gate cannot see. Fix: added `"title": "RegionType"` to the region `type` property
  node in `PresentationSlideLayouts-schema.json` (metadata-only, same pattern as the
  `ContentType` title above), which pins quicktype's generated name back to
  `RegionType`. Re-ran `make codegen-all`; verified `class RegionType` present,
  `class TypeEnum` gone, `type: Optional[RegionType]` on the `Region` dataclass, and
  diffed the full enum-class set against `HEAD` (`comm -13`/`-23` on sorted class
  names): the only net-new classes are `Density`, `Occupancy`, `Purpose`, `Role`
  (`ContentType` already existed at HEAD and is unchanged in name and values) — no
  pre-existing class was removed or renamed. `make uv-fullCheck` re-run green
  (962 passed). Lesson: a same-repo "nothing references this name" check is
  insufficient evidence for a codegen class-name rename in a schema whose generated
  types are consumed by a sibling repo; the identity of every renamed class needs
  checking, not just the ones this chunk directly touched.
- **`role` enum values:** limited to the four examples R20's text and FA-05 name
  (`presenterName`, `deckTitle`, `metricValue`, `evidence`) rather than inventing
  additional roles, since that is the only evidence-grounded set.
- **`purpose` tag vocabulary:** drawn from FA-05's corrective-action sentence
  ("section/statement, evidence, comparison, process, metric, and closing layouts")
  — `section`, `statement`, `evidence`, `comparison`, `process`, `metric`, `closing`.
- **`density` enum values (assumption):** no source text enumerates density levels;
  chose the minimal ordinal set `sparse` | `balanced` | `dense` as the smallest
  reasonable classification for an authoring-skill layout-selection signal. Flagging
  as an assumption, not a sourced requirement.

## Out of scope

- Lint rules and reading-order rendering (clerical chunk 14).
