---
human_ask: >
  I would also like to have the means to change the font for the deck. Clarification: font
  is a string, needs to set all text appropriately for its respective domains, we should
  have a global default one that we prescribe and a means to override it in layouts
  respectively.
goal: >
  Keep the prescribed deck-global font family and add a per-region font-family override in
  the layouts schema, so a layout region can set its own font while unset regions inherit
  the global default.
last_updated: 2026-09-04
semver: 0.0.1
author: Nicholas Bergantz
status: completed
---

# Plan 13 — Per-region font-family override

## Problem

A deck can set one global font family, but a layout region cannot override it. The ask is a
prescribed global default plus "a means to override it in layouts respectively" — i.e. per
region, so titles and body can carry different fonts. This is the schema half; wiring the
override into the render cascade is clerical-tools plan 16.

## Evidence / Investigation Findings

- **Global font family already exists and already works.** `PresentationMetadata`
  `defaults.fontFamily` is a schema field defaulting to `"Aptos"`
  (`schema/schemas/Presentations/PresentationMetadata-schema.json:76`), generated as
  `Defaults.font_family` (`src/foundationTypes/presentationTypes/Presentations.py:642`).
  The clerical renderer reads it and applies `run.font.name = font_family` to every run
  (`py-clerical-tools/src/py_clerical_tools/deck_builder/renderer.py:184,411`). So "the
  global default one that we prescribe" is present today — this plan keeps it, it does not
  reinvent it.
- **The gap is per-region override.** Font *size* already cascades region → regionDefaults
  (title/body) → metadata.defaults → schema default (`_resolve_font_size`,
  `renderer.py:456`). Font *family* has no such cascade: neither `region` nor
  `regionDefaults` has a `fontFamily` property, so family is deck-global only.
- **Same generated-code mechanism as plan 12.** `Region` and `RegionDefaults` are generated
  classes (`Presentations.py:461,284`); the override fields are added by editing
  `PresentationSlideLayouts-schema.json` and regenerating, per
  [`.claude/specs/schemaCodegen.md`](../specs/schemaCodegen.md).

## Proposed Approach

Add an optional `fontFamily` string at the two layout levels that already carry font size,
so family cascades exactly like size does. No block-level field (the ask says "in
layouts").

1. In `PresentationSlideLayouts-schema.json`, add an optional `fontFamily` string to:
   - `region` (per-region override), and
   - `regionDefaults` (per-region-*type* default, sits beside the existing `fontSize`).
   Description: "Font family override. When unset, inherits `metadata.defaults.fontFamily`."

2. Regenerate: `bash schema/scripts/generatePresentations.sh`. Adds `Region.font_family`
   and `RegionDefaults.font_family` to `Presentations.py`.

3. Keep `metadata.defaults.fontFamily` unchanged as the prescribed global default and the
   schema-declared fallback (`"Aptos"`). The resolution order the renderer will implement
   (clerical plan 16) mirrors `_resolve_font_size`:
   `region.fontFamily → regionDefaults(title/body).fontFamily → metadata.defaults.fontFamily → "Aptos"`.

No `image` region has text, so this override is inert for image regions — no interaction
with plan 12.

## Alternatives Considered

- **Separate `headingFontFamily` / `bodyFontFamily` on metadata.** Rejected: it only covers
  two fixed domains and does not compose with the region cascade already used for size. A
  per-region override generalizes to every region type and reuses the proven size pattern
  (chamber match with `_resolve_font_size`).
- **Block-level `style.fontFamily`** (to match `style.fontSize`). Deferred: the ask scopes
  override to layouts. Recorded as an open question, not built.

## Risks

- **Low.** Adding optional properties is backward-compatible: existing layouts omit
  `fontFamily` and resolve to the unchanged global default, so a deck rendered before and
  after this change is byte-identical. The only coupled change is regenerating types and
  re-syncing clerical-tools (uv-sync-local) before plan 16 can consume the new fields.

## Open Questions

- Add block-level `style.fontFamily` later for parity with `style.fontSize`? Out of scope
  now per the ask; revisit only on a separate request.

## Implementation Steps

- [x] Add optional `fontFamily` string to `region` and `regionDefaults` in
      `PresentationSlideLayouts-schema.json` with the inherit-from-global description.
- [x] Regenerate: `bash schema/scripts/generatePresentations.sh`; confirm
      `Region.font_family` and `RegionDefaults.font_family` appear.
- [x] `make uv-fullCheck`.

## Ask ↔ result

**human_ask / goal:** a global prescribed font default plus a means to override it per
layout region, string-typed, applying to all text domains. The live `/execute-plan 9-13`
request authorized building exactly this now; `human_ask` and `goal` agreed on the
objective, so no stop was needed.

**Delivered:** `PresentationSlideLayouts-schema.json` gained an optional `fontFamily`
string on both `region` (per-region override) and `regionDefaults` (per-region-*type*
default), each with the description "Font family override. When unset, inherits
`metadata.defaults.fontFamily`." Neither field carries a schema `default` — absence is
meaningful (inherit), not a substituted value, mirroring how `region.color` deliberately
has no default. `metadata.defaults.fontFamily` ("Aptos") is untouched and remains the
terminal fallback. Regeneration
(`bash schema/scripts/generatePresentations.sh`) added exactly `Region.font_family: str
| None` and `RegionDefaults.font_family: str | None` (plus their `from_dict`/`to_dict`
wiring) to `src/foundationTypes/presentationTypes/Presentations.py` — confirmed via
`git diff --stat` showing only that one file, 14 insertions/1 deletion, nothing else
generated-side changed.

Tests written first (red confirmed before regen): `test_region_and_region_defaults_have_font_family_override`
in `tests/typeTests/test_presentation_schema_shape.py` (schema-shape: field present,
`string`-typed, optional, no default, description content) and two tests in
`tests/typeTests/testPresentationSlideLayouts.py` —
`test_region_and_region_defaults_font_family_override_roundtrips` (a region and a
regionDefaults entry each setting `fontFamily` round-trip byte-identically) and
`test_region_font_family_omitted_still_validates_and_inherits` (an existing layout that
omits `fontFamily` still validates and emits no key on the wire).

**Gap:** none against this chunk's scope. Per the chunk's own Out-of-scope note, the
resolution cascade (`region.fontFamily → regionDefaults.fontFamily →
metadata.defaults.fontFamily → "Aptos"`) is not implemented here — that is clerical-tools
plan 16, a separate repository. No block-level `style.fontFamily` was added (deferred,
per the plan's Open Questions, matching the ask's "in layouts" scope).
