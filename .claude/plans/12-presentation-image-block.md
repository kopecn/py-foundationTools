---
human_ask: >
  I would like to add to the schemas for Presentation generating the means to take in an
  image file path as an arguement and inject it into the layout that could contain an
  image. Clarification: path lives on disk, and then needs to be injected into the
  presentation; scale it to bounding box.
goal: >
  Give the Presentation schemas an image region and an image content block carrying an
  on-disk file path, plus the pure fit-to-bounding-box geometry a renderer needs, so a
  deck can place an image into a layout region.
last_updated: 2026-09-04
semver: 0.0.1
author: Nicholas Bergantz
status: completed
---

# Plan 12 — Presentation image region + image content block

## Problem

A deck cannot place an image. There is no way for a layout to declare an image region and
no way for a slide to name an image file to draw into one. This plan adds that capability
to the schemas and the stdlib helper layer. It is the schema/helper half; the actual
`add_picture` render is the clerical-tools half (see that repo's plan 15).

## Evidence / Investigation Findings

- **No image region type.** `PresentationSlideLayouts-schema.json` `region.type` enum is
  `title, subtitle, body, column, metric, table, chart, footer, notes` — no `image`
  (`schema/schemas/Presentations/PresentationSlideLayouts-schema.json:145`).
- **No image content block.** `PresentationDeck-schema.json` `contentBlock.type` enum is
  only `text, bullets`, and the block's payload fields are `text` (string) and `items`
  (string array). There is no field that could hold a file path
  (`schema/schemas/Presentations/PresentationDeck-schema.json:86`).
- **Schema-driven, not hand-written.** `RegionType` and `ContentType` are generated enums
  in `src/foundationTypes/presentationTypes/Presentations.py:438,827`; adding an enum
  member and a field is done by editing the schema and regenerating, never by editing the
  `.py`. The generator is `schema/scripts/generatePresentations.sh`, which lists all four
  presentation schemas and every nested class in `CLASSES_FOR_BASE_PARENT`. Governed by
  [`.claude/specs/schemaCodegen.md`](../specs/schemaCodegen.md).
- **This repo owns schema + stdlib helpers, not rendering.** The presentation helper layer
  (`src/foundation_tools/presentation/`) already holds exactly "everything a renderer needs
  and cannot compute for itself": unit conversion (`units.py`), color resolution
  (`theme_resolver.py`), layout/region resolution (`layout_resolver.py`). Contain-fit
  geometry is pure math of the same kind and belongs here; reading image pixel dimensions
  needs a library and stays downstream.

## Proposed Approach

Minimal schema arm mirroring the existing `text`/`bullets` pattern, plus one pure helper.

1. **Layout can declare an image region.** Add `"image"` to `region.type` enum in
   `PresentationSlideLayouts-schema.json`. Geometry (`x/y/width/height`) already exists on
   every region and is the bounding box; no new geometry is needed.

2. **Deck can name an image file.** In `PresentationDeck-schema.json`:
   - Add `"image"` to `contentBlock.type` enum.
   - Add a `source` string property to `contentBlock`: "Filesystem path to the image file
     for an `image` block." One field, matching how `text` serves `text` blocks and `items`
     serves `bullets` blocks.

3. **Regenerate types.** Run `bash schema/scripts/generatePresentations.sh` (or
   `make codegen-all`). This adds `RegionType.IMAGE`, `ContentType.IMAGE`, and
   `ContentBlock.source` to the generated `Presentations.py`. No hand edits to that file.

4. **Pure fit-to-bounding-box helper.** Add `src/foundation_tools/presentation/image_fit.py`
   with one pure function and export it from the package `__init__`:

   ```python
   def fit_into_box(
       intrinsic_width: float, intrinsic_height: float,
       box_x: float, box_y: float, box_width: float, box_height: float,
   ) -> tuple[float, float, float, float]:
       """Scale (intrinsic_width, intrinsic_height) to fit inside the box preserving
       aspect ratio, centered. Returns (x, y, width, height) in the same pixel units."""
   ```

   "Scale it to bounding box" is read as aspect-preserving *contain* (fit fully inside,
   centered), because a plain stretch to `width`/`height` distorts the image — the
   surprising outcome. The renderer supplies the intrinsic pixel size (which it can only
   get from the image library) and this returns the placement rectangle. Stdlib-only, no
   I/O, result is a plain tuple — same shape as `resolve_geometry` downstream already uses.

## Alternatives Considered

- **Image path as a runtime argument to a build function** rather than a deck field.
  Rejected: the ask says "add to the schemas," and a deck that references its own figures
  is self-contained and re-renderable without out-of-band arguments — consistent with how
  `text`/`bullets` content already lives in the deck.
- **Stretch-to-box instead of contain.** Simpler (no intrinsic-size read, no helper) but
  distorts every non-matching aspect ratio. Rejected against the stated "scale it."
- **Putting the fit math in clerical-tools.** Rejected: it is pure geometry with no
  dependency, and this repo is the single home for renderer-agnostic presentation math.

## Risks

- **Enum widening is a compatibility change.** Adding enum members is backward-compatible
  for readers of old decks (old decks have no image blocks); a new deck using `image` fails
  to load against an un-regenerated consumer. Clerical-tools must re-sync the generated
  types (uv-sync-local) before it can read image decks — the known cross-repo sync trap.
- **Codegen re-derivation.** Regeneration overwrites `Presentations.py` wholesale; any
  drift between the checked-in file and the schemas surfaces here. Run the gate after.

## Open Questions

- Should the image block carry optional `alt` text and/or an explicit `fit`
  (`contain`/`cover`/`stretch`) later? Deferred — `source` + contain-fit is the minimum
  that satisfies the ask. Not adding speculative fields now.
- Path resolution base (deck-relative vs cwd vs absolute) is a *render* decision and is
  owned by clerical-tools plan 15, not this schema.

## Implementation Steps

- [x] Add `"image"` to `region.type` enum in `PresentationSlideLayouts-schema.json`.
- [x] Add `"image"` to `contentBlock.type` enum and a `source` string property in
      `PresentationDeck-schema.json`.
- [x] Regenerate: `bash schema/scripts/generatePresentations.sh`; confirm `RegionType.IMAGE`,
      `ContentType.IMAGE`, and `ContentBlock.source` appear in the generated file.
- [x] Add `src/foundation_tools/presentation/image_fit.py` (`fit_into_box`) and export it
      from `src/foundation_tools/presentation/__init__.py` `__all__`.
- [x] Unit test `fit_into_box`: wider-than-box, taller-than-box, exact-fit, and
      already-smaller cases; assert aspect ratio preserved and result centered.
- [ ] `make uv-fullCheck`. **BLOCKED** — see "Ask ↔ result" below.

## Ask ↔ result

- **`human_ask` / `goal`**: add an image region + image content block carrying an
  on-disk file path, plus pure fit-to-bounding-box geometry, so a deck can place an
  image into a layout region. `human_ask` and `goal` agree; no internal conflict.
- **Live request**: `/execute-plan` chunk 12, authorizing the build now.
- **Delivered** (all verified against actual repo state, not assumed):
  - `RegionType.IMAGE`, `ContentType.IMAGE`, `ContentBlock.source: str | None` — added
    to the two schemas and regenerated via `schema/scripts/generatePresentations.sh`;
    diff of `Presentations.py` contains only these three additions plus their
    `from_dict`/`to_dict` wiring, per `git diff`.
  - `src/foundation_tools/presentation/image_fit.py` — `fit_into_box(...)`, pure
    stdlib, contain-fit (aspect-preserving, centered), exported from the package
    `__init__.py` `__all__`.
  - `tests/test_image_fit.py` — 5 unit tests (wider-than-box, taller-than-box,
    exact-fit, already-smaller, box-offset), written first and confirmed failing
    (`ModuleNotFoundError`) before `image_fit.py` existed; all 5 pass now.
  - `make uv-lint` and `make uv-typecheck` pass clean.
- **Gap — gate blocked, not resolved unilaterally**: `make uv-fullCheck` fails on two
  pre-existing tests in `tests/typeTests/test_presentation_schema_shape.py`
  (`test_content_block_type_enum_includes_metric_table_chart` and
  `test_content_block_untyped_data_bag_stays_removed`), committed by chunk 11
  (`81d0fd0 11 Mermaid schema nucleation point`). That second test asserts, quoting
  its own comment: *"R7: ... image/quote stay out of the enum until a tier gives each
  a typed payload"* and explicitly fails if `"image"` is in `contentBlock.type.enum`.
  `.claude/specs/presentationSchema.md` R7 (semver 0.6.0, `last_updated: 2026-09-04`)
  carries the same claim: *"`image` and `quote` remain removed until the tier that
  gives each a typed payload."*
  This plan's own `human_ask`/`goal` (recorded human intent) is the tier that gives
  `image` its typed payload (`source`), so R7's own escape clause ("Adding an enum
  value later is a non-breaking schema change") appears to anticipate exactly this
  landing — but neither this guard test nor R7's text is named in this chunk's
  Implementation Steps, and the executing session's scope fence forbids touching
  files the chunk doesn't name. Updating that test and R7 to reflect chunk 12 landing
  is therefore left as an explicit, human-gated decision rather than made
  unilaterally. Schema/codegen/helper changes above are complete and correct against
  this plan as written; only the gate step is blocked pending that decision.

## Supervisor notes

- **Guard/spec reconciliation (authorized).** Chunk 11's guard tests and R7 asserted `image`
  stays out of the enum "until the tier that gives it a typed payload." Chunk 12 IS that tier
  (`source` is image's typed payload), so the supervisor updated
  `tests/typeTests/test_presentation_schema_shape.py` (enum now includes `image`; `quote` remains
  the only unshipped arm) and R7 (image now a renderable arm; semver 0.6.0 → 0.7.0). This
  fulfills R7's own stated condition — authorized by R7's text + this plan's `human_ask`, not a
  new requirement. The executor correctly stopped at this conflict rather than editing files
  outside its named set.
- **Out-of-scope README/docs reverted.** An executor had added a `docs/` documentation set (new
  untracked `docs/*.md`) and a README link to it — unrelated to chunk 12. README reverted; the
  untracked `docs/*.md` left in place for the user to keep or discard (not committed).
