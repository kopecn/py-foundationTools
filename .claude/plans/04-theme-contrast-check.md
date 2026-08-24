---
plan: ActionPlan04ThemeContrastCheck
scope: project
status: complete
last_updated: 2026-08-23
semver: 0.0.2
author: Nicholas Bergantz
---

# 04 — Theme Contrast Check

## Goal

Make a corporate theme self-validating: report every text-on-background pairing that will be hard to read, at authoring time rather than on a projector.

Contract: [presentationSchema.md](../specs/presentationSchema.md), Resolution Layer.

## Depends on

Chunk 02 (generated types). Independent of chunk 03 — may run in parallel.

## Files

Edit:
- `src/foundation_tools/presentation/theme_resolver.py`

Create:
- `tests/test_theme_contrast.py`

## Design constraints

**WCAG 2.x relative luminance**, the standard definition, implemented in plain arithmetic:

```python
def _channel(c: int) -> float:
    s = c / 255.0
    return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4

def _luminance(color: PresentationColor) -> float:
    return 0.2126 * _channel(color.r) + 0.7152 * _channel(color.g) + 0.0722 * _channel(color.b)

def contrast_ratio(fg: PresentationColor, bg: PresentationColor) -> float:
    a, b = _luminance(fg), _luminance(bg)
    lighter, darker = max(a, b), min(a, b)
    return (lighter + 0.05) / (darker + 0.05)
```

The ratio is symmetric and lands in 1.0 to 21.0. Black on white is 21.0; identical colors give 1.0. Use those two as fixed-point tests.

**Thresholds.** WCAG AA is 4.5 for body text and 3.0 for large text. Presentation text is large and viewed at distance, so `validate_theme` reports against 4.5 but classifies rather than fails: `ok` at or above 4.5, `low` between 3.0 and 4.5, `fail` below 3.0.

**Which pairings.** The theme declares its own intent, so check exactly the pairings it asserts:
- `text` on `background`
- `mutedText` on `background`
- each accent's `text` on that same accent's `background`

Do not check every color against every other — the theme never claims those combinations are used, and reporting them is noise.

**Never blocks.** `validate_theme` returns a report. It does not raise and does not prevent a render. An illegible theme is a decision the author is allowed to make; the tool's job is to say so.

**Opacity is ignored,** with a comment saying why: `PresentationColor.opacity` exists in the schema but python-pptx exposes no public transparency API, so a contrast number computed against it would describe an appearance the renderer cannot produce.

## Steps (TDD)

1. Write `tests/test_theme_contrast.py`: black-on-white is 21.0 (within 1e-9); white-on-black is also 21.0 (symmetry); identical colors give 1.0; a known mid-grey pairing matches a hand-computed value; `validate_theme` on a deliberately illegible theme reports `fail` for the right pairing and `ok` for the others. Run — fails.
2. Implement `contrast_ratio`, `_luminance`, `validate_theme`, and the `ThemeReport` dataclass.
3. Re-run — passes.
4. `make uv-fullCheck`.

## Acceptance criteria

- [x] `contrast_ratio(black, white) == 21.0` and equals `contrast_ratio(white, black)` (symmetric).
- [x] `contrast_ratio(c, c) == 1.0` for any c.
- [x] `validate_theme` checks exactly `2 + len(accents)` pairings, not the cross product.
- [x] `validate_theme` never raises and returns a report even for a theme where every pairing fails.
- [x] No dependency added; the module imports only `foundationTypes` and the stdlib.
- [x] `make uv-fullCheck` passes.

## Out of scope

- Suggesting corrected colors, or auto-adjusting a theme.
- Contrast of content against region backgrounds — regions have no fill in tier 1.
- Colorblind simulation, gradients, patterns.
- Wiring the check into a CLI (tier 4 `deck validate`).

## Resolution notes

- Implemented directly in `theme_resolver.py` as the plan's Files section specifies (same module chunk 03 created), appending `contrast_ratio`, `_channel`, `_luminance`, `_classify`, `ContrastPairing`, `ThemeReport`, and `validate_theme` below chunk 03's `resolve_color`.
- **Accents enumerated generically.** `validate_theme` iterates `dataclasses.fields(theme)` and picks up every field whose value is a `PresentationAccent` instance, rather than a hardcoded 8-name list — so `2 + len(accents)` pairings is enforced structurally, not by a magic number, and stays correct if the theme gains a 9th accent.
- Pairing names for accents use the theme's own camelCase property naming (e.g. `accentBlue.text`) via the same snake-to-camel mapping used nowhere else in this codebase yet; introduced locally in `theme_resolver.py` since chunk 03's `_accent_attr_name` goes the opposite direction (camel to snake).
- No opacity handling: `PresentationColor.opacity` is read by nothing in `_luminance`, with the schema-cited rationale (no python-pptx transparency API) captured as a code comment per the design constraint.
