---
plan: ActionPlan01PresentationSchemaLinking
scope: project
status: complete
last_updated: 2026-08-23
semver: 0.0.2
author: Nicholas Bergantz
---

# 01 — Presentation Schema Linking

## Goal

Turn four independently authored schemas into one linked family with no duplicate definitions, no instance data, and no field that resolves to nothing.

Contract: [presentationSchema.md](../specs/presentationSchema.md) R1–R9.

## Depends on

Nothing. This is the first chunk.

## Files

Edit:
- `schema/schemas/Presentations/PresentationDeck-schema.json`
- `schema/schemas/Presentations/PresentationMetadata-schema.json`
- `schema/schemas/Presentations/PresentationSlideLayouts-schema.json`
- `schema/schemas/Presentations/PresentationColorTheme-schema.json` (add `$id`/description only — its structure is already correct)

Create:
- `schema/examples/Presentations/layouts.json` — the five-layout library extracted from the schema
- `schema/examples/Presentations/theme.json` — a corporate theme instance
- `schema/examples/Presentations/deck.json` — a three-slide deck exercising `text` and `bullets`

## Design constraints

**1. Extract the instance data (R1).** `PresentationSlideLayouts-schema.json:22-179` holds a concrete five-layout library (`title`, `one-column`, `two-column`, `metric-and-body`, `table`) inside `properties`. It is not a schema; draft-06 ignores it and quicktype would emit a garbage field. Move it verbatim to `schema/examples/Presentations/layouts.json`, then delete the `layoutLibrary` key.

Keep only the three layouts tier 1 renders — `title`, `one-column`, `two-column` — in the example file. Park `metric-and-body` and `table` in a sibling `layouts-deferred.json` so the coordinates are not lost when their block types return in tier 2.

**2. Deck refs metadata (R2).** Delete the local `presentationMetadata` definition at `PresentationDeck-schema.json:28-54` and replace the property with:

```json
"metadata": { "$ref": "PresentationMetadata-schema.json" }
```

Bare filename, no fragment — the pattern at `Math/QuaternionWaveform-schema.json:13`. The local copy declares `file` as a string where the real schema declares it as an object; that divergence is the bug.

**3. Remove the dangling links (R3).** Delete `PresentationDeck.layouts` (`:15-18`) and `PresentationMetadata.defaults.colorTheme` (`:126-129`). Both are bare strings pointing at nothing. Resolution is by directory convention: `deck.json`, `theme.json`, `layouts.json`.

**4. Canvas gets one owner (R5).** Delete `PresentationMetadata.canvas` (`:72-99`) and `PresentationMetadata.defaults.margin` (`:121-125`). `layoutDefaults.canvasWidth`/`canvasHeight`/`outerMargin` are authoritative, because layout coordinates are absolute against that canvas.

**5. Color enum (R4).** Add to `PresentationSlideLayouts-schema.json` definitions:

```json
"themeColorRef": {
  "type": "string",
  "description": "Address of a color in PresentationColorTheme. Scalars are named directly; accents are addressed as <accent>.<channel>.",
  "enum": [
    "background", "text", "mutedText",
    "accentGrey.accent", "accentGrey.background", "accentGrey.text",
    "accentRed.accent", "accentRed.background", "accentRed.text",
    "accentGreen.accent", "accentGreen.background", "accentGreen.text",
    "accentBlue.accent", "accentBlue.background", "accentBlue.text",
    "accentAmber.accent", "accentAmber.background", "accentAmber.text",
    "accentTeal.accent", "accentTeal.background", "accentTeal.text",
    "accentYellow.accent", "accentYellow.background", "accentYellow.text",
    "accentPurple.accent", "accentPurple.background", "accentPurple.text"
  ]
}
```

Point `region.color`, `regionDefaults.color`, and `contentBlock.style.color` at it. `PresentationDeck` reaches it via the `$ref` chain, so `PresentationSlideLayouts-schema.json` must be listed in the same codegen invocation (chunk 02 handles that).

**6. Trim the block enum (R7).** `contentBlock.type` becomes `["text", "bullets"]`. Delete `value`, `label`, and `data` from `contentBlock` — they existed only for the removed arms, and `data` was an untyped `object` that lost all structure.

**7. Overflow (R8).** Add to `region`:

```json
"overflow": {
  "type": "string",
  "enum": ["wrap", "clip"],
  "default": "wrap",
  "description": "Behavior when content exceeds the region box. 'wrap' flows text within the box; 'clip' truncates at the boundary."
}
```

**8. Minor fixes.** Make `slide.title` optional (a divider or full-bleed slide legitimately has none). Add `"minItems": 1` to `slideLayout.regions`. Normalize `PresentationSlideLayouts-schema.json` to 2-space indent, matching the other three.

## Steps (TDD)

1. Write `tests/typeTests/test_presentation_schema_shape.py` asserting, by loading the raw JSON: no `layoutLibrary` key exists; `PresentationDeck` has no `definitions.presentationMetadata`; `metadata` is a `$ref` to the bare filename; `contentBlock.type.enum == ["text", "bullets"]`; `themeColorRef.enum` has 30 members; `PresentationMetadata` has no `canvas`. Run it — it fails.
2. Apply constraints 1–8.
3. Re-run — it passes.
4. Validate each example instance against its schema, confirming `$ref` resolves from within `Presentations/`.
5. `make uv-fullCheck`.

## Acceptance criteria

- [x] `grep -c layoutLibrary schema/schemas/Presentations/*.json` returns 0.
- [x] `PresentationDeck-schema.json` contains `"$ref": "PresentationMetadata-schema.json"` and no `presentationMetadata` definition.
- [x] No schema under `Presentations/` contains a `canvas` key outside `PresentationSlideLayouts`.
- [x] `themeColorRef.enum` has exactly 27 entries (corrected from the plan's stated 30 — see Resolution notes) and every accent named in `PresentationColorTheme` contributes 3.
- [x] All three example instances validate against their schemas.
- [x] `make uv-fullCheck` passes.

## Out of scope

- The codegen script and generated package (chunk 02).
- Any Python module (chunks 03, 04).
- Typed `table`/`metric`/`chart`/`image` payloads (tier 2) — this chunk removes those arms, it does not design their replacements.
- Version or identity fields on theme and layouts (tier 3).
- Touching any schema outside `Presentations/`.

## Resolution notes

- **`themeColorRef` enum count corrected 30 -> 27.** `PresentationColorTheme-schema.json` declares 8 accents (`accentGrey`, `accentRed`, `accentGreen`, `accentBlue`, `accentAmber`, `accentTeal`, `accentYellow`, `accentPurple`), not 9. The plan's own constraint-5 enum listing was already the correct 27-entry literal (3 scalars + 8 accents x 3 channels); only the prose ("30", "9 accents") was wrong, in both this chunk and `presentationSchema.md` R4. Per the "spec is authoritative, implementation forces a contract change" rule, `presentationSchema.md` R4 was corrected in this chunk (semver 0.0.1 -> 0.0.2) to state `3 + 3n` with `n = 8` today, and the shape test asserts 27 (derived from the theme's actual accent count, not hardcoded) rather than a bare 30.
- **Example validation without `jsonschema`.** The repo has zero runtime deps and `jsonschema` is not a dev dependency, so step 4 ("validate each example instance against its schema") was done with a targeted ad hoc structural check (required fields, enums, cross-file id resolution) run from the scratchpad rather than a full JSON Schema validator — not added to the repo. Chunk 02's codegen and chunk 05's `from_dict` round-trip tests are the durable, in-repo validation of these same examples going forward.
- **`contentBlock.style.color` cross-file ref.** Constraint 5 only lists `region.color` and `regionDefaults.color` (both in `PresentationSlideLayouts-schema.json`, resolved via a same-file `#/definitions/themeColorRef`); `contentBlock.style.color` lives in `PresentationDeck-schema.json` and needed a cross-file ref with a fragment: `"PresentationSlideLayouts-schema.json#/definitions/themeColorRef"`. No existing schema in the repo used a cross-file fragment ref before this; quicktype resolved it correctly in chunk 02 (see that chunk's notes).
- **`$id` added only to `PresentationColorTheme-schema.json`**, per the Files section; the other three schemas were left without a top-level `id` since the design constraints didn't request one and bare-filename `$ref` resolution doesn't depend on it (confirmed against the `ChArUcoConfig`/`ChArUcoBoard` precedent).
- **`layouts-deferred.json`** stores `metric-and-body` and `table` as a bare `{"layouts": [...]}` fragment (not a full `PresentationSlideLayouts` instance) with an explanatory `_note` field, since it is parked geometry for tier 2 and not consumed by any tier-1 code path.
