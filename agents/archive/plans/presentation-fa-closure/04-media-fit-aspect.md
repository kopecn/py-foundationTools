---
human_ask: >
  a series of FA's was generated from the first use of the build presentation tool.
  please review:
  /Users/nbergantz/__Workspaces__/pythonWorkspaces/py-clerical-tools/.claude/fa_reports
  and create a series action plan on closing these gaps.
goal: >
  Add media fit modes + region aspect/fill fields to the schema and extend fit_into_box
  with cover/fitWidth/fitHeight geometry.
last_updated: 2026-09-15
semver: 0.0.1
author: Nicholas Bergantz
status: completed
---

# F4 — Media fit + aspect geometry

Serves [Summary goal](./00-overview.md#summary-goal) · [Original ask](./00-original-ask.md).
Implements [presentationSchema.md](../../specs/presentationSchema.md) **R18**. Evidence:
`py-clerical-tools/.claude/fa_reports/FA-03-media-scaling-and-mermaid-legibility.md`.
Unblocks clerical chunks 12 and 14. **Land before F6** (shares `preferredAspectRatio`).

## Deliverable

- `image` and `mermaid` blocks (Deck schema) gain `fit` (`contain` | `cover` | `fitWidth`
  | `fitHeight`), with `contain` the **declared default for both** (the only new default
  in this series; bumps `presentationSchema.md` semver per R12). `cover` may carry
  focal-point metadata.
- a visual `region` (SlideLayouts) gains `preferredAspectRatio` (or min/max range) and
  `minFillRatio` — `preferredAspectRatio` defined **once** here and `$ref`'d by F6.
- `fit_into_box` family (in `src/foundation_tools/presentation/image_fit.py`) gains pure,
  total geometry for `cover` (crop fractions), `fitWidth`, `fitHeight`.

## Files

- `schema/schemas/Presentations/PresentationDeck-schema.json` — `fit` + focal point.
- `schema/schemas/Presentations/PresentationSlideLayouts-schema.json` —
  `preferredAspectRatio` (canonical definition) + `minFillRatio`.
- `src/foundation_tools/presentation/image_fit.py` — new pure functions (or a mode param
  on the existing family). No I/O.
- `src/foundationTypes/presentationTypes/Presentations.py` — regenerated.
- `tests/test_presentation_media_fit.py`, `tests/test_image_fit_modes.py` — new.

## Design constraints (decided here)

- `contain` default is declared on `fit` for both `image` and `mermaid` (so the renderer
  never chooses a default). This is the intentional R12 semver bump — note it in the spec
  changelog/frontmatter.
- Geometry functions are pure and total: given intrinsic w/h and box w/h, return the
  placement rect (and, for cover, crop fractions in [0,1)); no distortion for contain;
  deterministic crop for cover.
- `preferredAspectRatio` is one canonical definition; F6 `$ref`s it — do not duplicate.

## Literal recipe (cover geometry)

```python
def cover_box(iw: float, ih: float, bx: float, by: float, bw: float, bh: float):
    """Scale to fully cover the box, center, return (left, top, w, h, crop_l, crop_r, crop_t, crop_b)."""
    scale = max(bw / iw, bh / ih)
    sw, sh = iw * scale, ih * scale
    crop_x = (sw - bw) / sw / 2      # fraction cropped each side
    crop_y = (sh - bh) / sh / 2
    return bx, by, bw, bh, crop_x, crop_x, crop_y, crop_y
```

## TDD steps

1. Failing tests: `test_fit_field_roundtrip_with_default`,
   `test_region_aspect_and_fill_roundtrip`, `test_cover_geometry_deterministic`,
   `test_fitwidth_fitheight_geometry`, `test_contain_unchanged`.
2. Edit schemas; extend `image_fit.py`; `make codegen-all`.
3. `make uv-fullCheck` green.

## Acceptance criteria

- [x] `fit` (default `contain`) + region aspect/fill validate and round-trip.
- [x] `fit_into_box` family returns pure, deterministic geometry for all modes; contain
      unchanged.
- [x] `preferredAspectRatio` defined once (F6 will `$ref` it).
- [x] The declared `contain` default is recorded as an R12 semver bump.
- [x] `make codegen-all` clean; `make uv-fullCheck` green.

## Out of scope

- Applying fit modes in placement (clerical chunk 12); aspect/fill lint (clerical 14).

## Ask ↔ result

`human_ask`/`goal` (planning-only, recorded 2026-09-14) authorized scoping this chunk;
the live `/execute-plan` command in this session authorized implementing it now -- not a
conflicting ask, per the chunk frontmatter's own instruction. R18's exact text ("`image`
and `mermaid` blocks MAY declare a `fit` mode ... with `contain` the schema-declared
default for both ... `cover` MAY carry focal-point metadata. A visual region MAY declare
a `preferredAspectRatio` (or an acceptable min/max aspect range) and a `minFillRatio`")
maps directly onto what was built, with no gap: `fit` (enum `contain`/`cover`/
`fitWidth`/`fitHeight`, default `contain`) and `focalPoint` (`x`/`y` fractions, no
default) on `contentBlock`; `preferredAspectRatio`, `minAspectRatio`, `maxAspectRatio`,
`minFillRatio` (all no default) on `region`. `fit` is one field shared by every
`contentBlock` (not type-conditional in this schema), so `image` and `mermaid` both get
the same default, satisfying "the schema-declared default for both" without duplicating
the field. `contain` is the only new `default`, matching the plan's "one intentional new
default in this series." No deviation from the chunk as written.
