---
plan: ActionPlan09DeckVersioning
scope: project
status: completed
last_updated: 2026-09-04
semver: 1.1.0
author: Nicholas Bergantz
---

# 09 — theme and layout version identity

Add only the identity/version information needed to determine which corporate theme and
layout standard a deck used. The model must support later updating without forcing a
registry or storage service into this library.

Choose compatibility semantics from real level-2 artifacts. Remote registries,
discovery services, and release management are out of scope.

## Ask ↔ result

`human_ask` (00-overview.md objective): "allow old presentations to adopt later corporate
standards -- 'CSS for pptx.'" Tier 3 (this chunk) exists to give a deck enough identity to
make that later adoption decidable, without this repository owning any registry, storage,
or discovery service for the standards themselves.

`live_request`: `/execute-plan 9-13 per tier 3 on 00-overview.md` -- user was told 09-11 are
thin stubs requiring a design decision and explicitly chose to execute anyway, authorizing
the minimal design decision this chunk needs.

`design_choice`: `PresentationMetadata-schema.json` (deck-level metadata) gains two
optional, fully-additive nested objects, each with two flat optional string fields
(default `""`), mirroring the existing `Defaults`/`File` nesting precedent already used in
the same schema:

- `themeVersion: { id, version }` -- identity of the `PresentationColorTheme` the deck was
  authored against.
- `layoutVersion: { id, version }` -- identity of the `PresentationSlideLayouts` standard
  the deck was authored against.

Neither field is in `PresentationMetadata.required`, so every deck predating this chunk
(no version stamp at all) still validates and round-trips unchanged -- confirmed by
`test_theme_and_layout_version_identity_is_optional`. `id`/`version` are opaque strings the
author or an external tool sets and reads; this library performs no lookup, comparison, or
resolution against them (that machinery -- matching a stamped id/version to an actual
theme/layout document, and any registry that would make discoverable -- is explicitly
deferred to a later migration tool, per chunk 10 and the overview's out-of-scope list).

`delivered`:

- `schema/schemas/Presentations/PresentationMetadata-schema.json` -- `themeVersion` and
  `layoutVersion` properties added (see above).
- `schema/scripts/generatePresentations.sh` -- `ThemeVersion` and `LayoutVersion` added to
  `CLASSES_FOR_BASE_PARENT` (nested dataclasses need the `DataModelHelper` parent, same
  reasoning as every other nested class in this script).
- `src/foundationTypes/presentationTypes/Presentations.py` -- regenerated via
  `generatePresentations.sh`; new `ThemeVersion`/`LayoutVersion` dataclasses,
  `PresentationMetadata` gains `theme_version`/`layout_version` (wire keys
  `themeVersion`/`layoutVersion`), both `... | None = None`. No other class, enum
  (`RegionType` included), or field touched by the regen.
- `tests/typeTests/test_presentation_schema_shape.py` --
  `test_metadata_theme_and_layout_version_identity_present_and_optional` (schema shape:
  object type, `{id, version}` properties, both string, neither required).
- `tests/typeTests/testPresentationDeck.py` -- `_versioned_deck_dict` fixture,
  `test_from_dict_builds_theme_and_layout_version_identity`,
  `test_theme_and_layout_version_identity_is_optional`, and `versioned` added to the
  round-trip case set.
- `.claude/specs/presentationSchema.md` -- new R13 records the contract; R3 updated to
  point at it instead of "deferred to tier 3." semver 0.4.0 -> 0.5.0.

Gate after: `make uv-fullCheck` clean, 535 tests total. This chunk added 3 test functions
(1 schema-shape, 2 deck round-trip/optionality) plus one new case in the existing
parametrized round-trip test; the pre-chunk-09 baseline was not independently measured, so
no delta is claimed here.

`gap`: None against this chunk's stated scope. Whether the theme/layout documents
themselves should someday carry a matching self-declared `id`/`version` (so a migration
tool has something authoritative to compare the stamp against) is a design question for
chunk 10 (layout migration), not decided here -- adding it now would be inventing registry
adjacent scope this chunk was told to avoid.

## Supervisor notes

- **Out-of-scope change reverted.** The executor also rewrote `src/foundation_tools/file_tools/path_tools.py` (changing `expand_glob_patterns`'s public signature `pattern: str -> Path`, `root: Path | str -> Path`) and its tests `tests/test_path_tools.py` — a breaking API refactor of the fix-05 file, unrelated to deck versioning. Reverted to HEAD before commit; gate re-run clean (535) on the presentation-only diff.
- **Ratification needed on R13.** The spec's R3 pre-deferred `theme.id`/`theme.version` to tier 3, so the *direction* is authorized; the specific shape (`themeVersion`/`layoutVersion`, id+version strings, `layoutVersion` added symmetrically) is the executor's design choice, now written as a normative `SHALL`. Spec is `status: draft` (0.5.0) — confirm or adjust the shape.
