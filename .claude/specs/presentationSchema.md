---
spec: PresentationSchema
scope: project
status: draft
applies_to: schema/schemas/Presentations/, schema/scripts/generatePresentations.sh, src/foundationTypes/presentationTypes/, src/foundation_tools/presentation/
last_updated: 2026-08-23
semver: 0.0.2
author: Nicholas Bergantz
---

# Presentation Schema Specification

> **Status — draft.** Nothing in this spec is implemented yet. The four schemas in `schema/schemas/Presentations/` exist but are unlinked and have no codegen script or generated package. This spec is the contract the tier-1 chunks build to. Keep it in sync with `schema/schemas/Presentations/` and `src/foundation_tools/presentation/` as they change.

## Overview

The Presentations domain describes a slide deck declaratively, so a downstream renderer in a separate repository can construct a real `.pptx` rather than fill in a template. This repository owns the schemas, the generated types, and stdlib-only resolution. It owns no rendering: `python-pptx` MUST NOT appear in this repository's dependencies, which are contractually empty.

The domain separates three concerns that are conventionally fused in a PowerPoint template:

- **Theme** — what colors and fonts mean (`PresentationColorTheme`).
- **Layout** — where content goes (`PresentationSlideLayouts`).
- **Content** — what is said (`PresentationDeck`, `PresentationMetadata`).

A deck therefore carries no literal color and no coordinate. It names a semantic color and a layout region, and resolution happens at build time. This is what allows a deck authored a year ago to re-render against a newer corporate standard.

## Design Goals

1. **Content survives a theme change.** A deck references meaning, never appearance.
2. **Unrepresentable states are unrepresentable.** A block type exists in the schema only when it has a payload capable of expressing it and a renderer capable of drawing it.
3. **One definition per concept.** Cross-file `$ref` by bare filename within the domain, never a re-declaration.
4. **Codegen-compatible.** Every construct must survive quicktype's dataclass codegen and `mypy --strict`.
5. **Zero runtime dependencies**, per the repository's core constraint.

## Core Requirements

### R1 — Domain layout

The domain SHALL consist of exactly four schemas under `schema/schemas/Presentations/`, named `<Title>-schema.json` with `title` matching the generated class name, `draft-06`, 2-space indent, and a `description` on the object and on every property (they become the generated docstrings).

Instance data SHALL NOT appear inside a schema. Example instances live under `schema/examples/Presentations/`.

### R2 — Linking

`PresentationDeck-schema.json` SHALL `$ref` `PresentationMetadata-schema.json` by bare filename and SHALL NOT declare a local metadata definition. This follows the established intra-domain precedent (`Math/QuaternionWaveform-schema.json` refs `Quaternion-schema.json`; `ComputerVisions/ChArUcoConfig-schema.json` refs `ChArUcoBoard-schema.json`).

The prohibition on cross-file `$ref` in [schemaCodegen.md](schemaCodegen.md) is scoped to **cross-domain** coupling and does not apply within `Presentations/`.

### R3 — The deck directory (tier 1 resolution model)

A deck is a **directory**, not a file. Resolution is by fixed filename:

```text
mydeck/
├── deck.json       → PresentationDeck
├── theme.json      → PresentationColorTheme
└── layouts.json    → PresentationSlideLayouts
```

Consequently `PresentationDeck.layouts` and `PresentationMetadata.defaults.colorTheme` — today bare strings resolving to nothing — SHALL be removed. A field that names a thing nothing can resolve is worse than its absence.

The semantic binding that matters is preserved by R4: content names theme *properties*, so swapping `theme.json` re-themes the deck. Identity and versioning (`theme.id`, `theme.version`, a registry of themes) are deferred to tier 3, where migration gives them meaning.

### R4 — Color references are enumerated

`region.color`, `regionDefaults.color`, and `contentBlock.style.color` SHALL be an enum over the theme's actual addressable colors, not a free string, so an unresolvable reference fails at validation instead of at render.

The enum SHALL contain exactly `3 + 3n` values, where `n` is the number of accents `PresentationColorTheme` declares: the three scalars `background`, `text`, `mutedText`, plus `<accent>.<channel>` for each accent across the 3 channels (`accent`, `background`, `text`). `PresentationColorTheme-schema.json` currently declares 8 accents (`accentGrey`, `accentRed`, `accentGreen`, `accentBlue`, `accentAmber`, `accentTeal`, `accentYellow`, `accentPurple`), so the enum has exactly 27 values today. (Corrected 2026-08-23: an earlier draft of this spec asserted 9 accents / 30 values without a 9th accent ever existing in the theme schema — chunk 01 found and fixed the discrepancy.)

**Invariant:** this enum is derived from `PresentationColorTheme`'s property names. Adding an accent to the theme SHALL add its three channels to the enum in the same change.

### R5 — Canvas has one owner

Canvas dimensions and outer margin SHALL be defined once, in `PresentationSlideLayouts.defaults` (`canvasWidth`, `canvasHeight`, `outerMargin`), because layout coordinates are absolute against that canvas and must not be able to disagree with it.

`PresentationMetadata.canvas` and `PresentationMetadata.defaults.margin` SHALL be removed. Metadata describes the document; it does not define geometry.

### R6 — The unit invariant

All coordinates are pixels against the canvas. PowerPoint works in EMU (914400 per inch). At the 1920x1080 canvas over a 16:9 slide (13-1/3 x 7-1/2 in) the mapping is exactly 144 px/in:

```python
EMU_PER_PX: Final[int] = 6350  # 914400 EMU/in / 144 px/in - exact, no rounding
```

1920 x 6350 = 12192000 and 1080 x 6350 = 6858000, which are precisely PowerPoint's widescreen slide dimensions. The conversion is lossless in both directions for integer pixel values.

This constant SHALL be defined once, in `src/foundation_tools/presentation/units.py`, and SHALL NOT be re-derived by any consumer.

### R7 — Block types must be renderable

`contentBlock.type` SHALL contain only arms with a payload sufficient to express them. Tier 1 therefore ships:

```json
"enum": ["text", "bullets"]
```

`metric`, `table`, `chart`, `image`, and `quote` are removed until the tier that gives each a typed payload. Adding an enum value later is a non-breaking schema change; shipping an arm that validates and then fails to render is not.

`contentBlock.data` (untyped `object`) SHALL be removed — it is the mechanism by which structure was being lost.

### R8 — Overflow is declared, not discovered

`region` SHALL carry `overflow` with tier-1 values `wrap` (default) and `clip`. Text that does not fit is the dominant failure mode of generated decks, and the schema must say what should happen rather than leave it to renderer accident. `shrink` is deferred to tier 2, where font metrics make it honest.

### R9 — No discriminated unions

Per [schemaCodegen.md](schemaCodegen.md), quicktype cannot generate discriminated unions. `contentBlock` SHALL remain a flat bag: a `type` enum plus optional sibling fields. Correspondence between the arm and its fields is enforced by the consumer, not the schema.

### R10 — Codegen

One script, `schema/scripts/generatePresentations.sh`, SHALL own the module, listing all four schemas in `INPUT_SCHEMA_FILES` (quicktype resolves `$ref` only within a single invocation and emits exactly one file per invocation). It SHALL be structurally identical to the golden `generateDiskUsage.sh` apart from its variable block, per the chamber-match rule.

`OUTPUT_PYTHON_REL="presentationTypes/Presentations.py"`. No Makefile edit is required — `codegen-all` globs `schema/scripts/*.sh`.

## Resolution Layer

`src/foundation_tools/presentation/` — pure stdlib, no I/O, total functions.

```python
# units.py
EMU_PER_PX: Final[int] = 6350
def px_to_emu(px: float) -> int: ...
def emu_to_px(emu: int) -> float: ...

# theme_resolver.py
def resolve_color(theme: PresentationColorTheme, ref: ThemeColorRef) -> PresentationColor: ...
def contrast_ratio(fg: PresentationColor, bg: PresentationColor) -> float: ...
def validate_theme(theme: PresentationColorTheme) -> ThemeReport: ...

# layout_resolver.py
def resolve_layout(layouts: PresentationSlideLayouts, layout_id: str) -> LayoutResult: ...
def resolve_region(layout: SlideLayout, region_id: str) -> RegionResult: ...
```

Resolution SHALL report failure through result objects rather than exceptions, per the repository's error convention. A missing layout id or region id is an expected authoring error, not an exceptional condition.

`contrast_ratio` implements the WCAG 2.x relative-luminance formula. `validate_theme` reports every text-on-background pairing the theme declares whose ratio falls below the threshold, so an illegible corporate palette is caught when it is authored rather than on a projector.

## Error Handling

| Condition | Behavior |
|---|---|
| Unknown layout id | `LayoutResult` failure naming the id and listing available ids |
| Unknown region id | `RegionResult` failure naming the region and its layout |
| Color ref not in enum | Rejected at schema validation, before resolution runs |
| Contrast below threshold | Reported by `validate_theme`; never raises, never blocks a render |

## Compliance Requirements

A compliant Presentations domain MUST:

1. Define each concept exactly once, with intra-domain `$ref` by bare filename and no re-declaration.
2. Contain no instance data inside any schema file.
3. Resolve every `contentBlock.region` to a `region.id` present in the referenced layout, checked by the consumer at load time.
4. Restrict every color reference to the enumerated theme addresses of R4.
5. Define canvas geometry in exactly one schema (R5).
6. Round-trip every model through `to_dict()` -> `from_dict()` without data loss, per [dataModelHelper.md](dataModelHelper.md).
7. Generate cleanly under `make codegen-all` and pass `make uv-fullCheck` with `mypy --strict`.
8. Introduce no runtime dependency.
