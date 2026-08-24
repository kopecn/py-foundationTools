---
plan: ActionPlan03PresentationResolvers
scope: project
status: complete
last_updated: 2026-08-23
semver: 0.0.2
author: Nicholas Bergantz
---

# 03 — Presentation Resolvers

## Goal

Stdlib-only resolution: pixels to EMU, semantic color name to RGB, layout id to layout, region id to region. This is everything the renderer needs and cannot compute for itself.

Contract: [presentationSchema.md](../specs/presentationSchema.md) R6 and the Resolution Layer section.

## Depends on

Chunk 02 — the generated types must exist to be imported.

## Files

Create:
- `src/foundation_tools/presentation/__init__.py`
- `src/foundation_tools/presentation/units.py`
- `src/foundation_tools/presentation/theme_resolver.py`
- `src/foundation_tools/presentation/layout_resolver.py`
- `tests/test_presentation_resolvers.py`

## Design constraints

**The unit constant is exact and belongs here alone.**

```python
EMU_PER_PX: Final[int] = 6350  # 914400 EMU/in / 144 px/in - exact, no rounding
```

The 1920x1080 canvas over a 13-1/3 x 7-1/2 in 16:9 slide is exactly 144 px/in. 1920 x 6350 = 12192000 and 1080 x 6350 = 6858000, PowerPoint's widescreen dimensions. Integer pixels convert losslessly both ways; `px_to_emu` takes `float` for fractional coordinates and rounds half-up.

**Result objects, not exceptions.** An unknown layout id is an authoring mistake, not an exceptional condition. Follow the repository convention already used by `CLITransactResult`:

```python
@dataclass(frozen=True)
class LayoutResult:
    layout: SlideLayout | None
    error: str | None
    @property
    def ok(self) -> bool: return self.error is None
```

A failure message names what was missing and what was available: `unknown layout 'two-col'; available: title, one-column, two-column`. That message is the whole user experience of a typo, so make it good.

**Color addressing.** `resolve_color` parses the `themeColorRef` enum values from chunk 01. Two forms: a bare scalar (`background`, `text`, `mutedText`) reads a top-level theme property; a dotted form (`accentBlue.accent`) reads a channel of an accent. Split on `.` once; anything else is a failure result. The enum already constrains input, so this is defence in depth rather than the primary check.

**Purity.** No file I/O, no logging, no global state. These functions take already-parsed models and return values. Loading `deck.json` from disk belongs to the consumer.

## Steps (TDD)

1. Write `tests/test_presentation_resolvers.py` covering: `px_to_emu(1920) == 12192000`; `px_to_emu(1080) == 6858000`; `emu_to_px(px_to_emu(n)) == n` for integer n; `resolve_color` on both address forms; `resolve_color` failure on an unknown accent; `resolve_layout` hit and miss with the available-ids message; `resolve_region` hit and miss. Run — fails on import.
2. Implement `units.py`, then `theme_resolver.py`, then `layout_resolver.py`.
3. Re-run — passes.
4. `make uv-fullCheck`.

## Acceptance criteria

- [x] `px_to_emu(1920) == 12192000` and `px_to_emu(1080) == 6858000` exactly.
- [x] `emu_to_px(px_to_emu(n)) == n` for every integer n in 0..1920.
- [x] `EMU_PER_PX` is defined exactly once in the repository (one `EMU_PER_PX: Final[int] = 6350` assignment; `grep -rn "6350" src/` also matches two prose mentions in `units.py`'s docstring, not additional definitions).
- [x] Every resolver returns a result object; `grep -n "raise" src/foundation_tools/presentation/*.py` finds no `raise` statement (its one hit is the word "raises" inside a docstring).
- [x] A failed `resolve_layout` message contains both the bad id and the available ids.
- [x] No import of anything outside the stdlib and `foundationTypes`.
- [x] `make uv-fullCheck` passes.

## Out of scope

- Contrast checking (chunk 04).
- Reading files from disk — the deck directory is the renderer's concern.
- Anything importing `python-pptx`.
- Style cascade / precedence resolution: the renderer owns that (see `deckBuilder.md` R4), and duplicating it here would create two sources of truth.

## Resolution notes

- **`resolve_color` returns a `ColorResult`, not a bare `PresentationColor`.** `presentationSchema.md`'s Resolution Layer pseudocode shows `resolve_color(...) -> PresentationColor` (unwrapped), but this chunk's own design constraints and TDD steps ("resolve_color failure on an unknown accent") require a failure path, and the chunk's opening line states "Result objects, not exceptions" as the governing convention for the whole module. Treated the pseudocode as illustrative shorthand, not a literal signature — implemented `ColorResult(color, error)` with an `.ok` property, matching `LayoutResult`/`RegionResult`. No spec edit needed since `presentationSchema.md`'s own prose immediately below the code block already states resolution "SHALL report failure through result objects rather than exceptions."
- **Accent-name mapping is derived, not hardcoded.** `resolve_color`'s dotted form (`accentBlue.accent`) maps to the generated field `accent_blue` via a small camelCase-to-snake_case regex, rather than a hardcoded 8-accent table — so a theme with a 9th accent resolves without a code change here, consistent with R4's invariant.
- `px_to_emu` rounds half-up via `math.floor(px * EMU_PER_PX + 0.5)`, correct for the non-negative pixel-coordinate domain this function is scoped to (documented as such rather than handling negative inputs it will never see).
