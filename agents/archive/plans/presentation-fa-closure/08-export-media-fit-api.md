---
human_ask: >
  a series of FA's was generated from the first use of the build presentation tool.
  please review:
  /Users/nbergantz/__Workspaces__/pythonWorkspaces/py-clerical-tools/.claude/fa_reports
  and create a series action plan on closing these gaps.
goal: Export every public media-fit helper from the presentation package root.
last_updated: 2026-09-23
semver: 0.0.2
author: Nicholas Bergantz
status: completed
---

# 08 — Export media-fit public API

Serves [Summary goal](./00-overview.md#summary-goal) · [Original ask](./00-original-ask.md).

## Goal

Make the presentation package's declared public surface expose all four media-fit operations implemented for R18.

## Origin

PA-01: `src/foundation_tools/presentation/image_fit.py` declares `fit_into_box`, `cover_into_box`, `fit_width_into_box`, and `fit_height_into_box` public, while the package root re-exports only `fit_into_box`.

## Deliverable

Callers can import all four helpers from `foundation_tools.presentation`, and the package `__all__` contains the same four names.

## Files

- `src/foundation_tools/presentation/__init__.py` — import and export the three missing helpers.
- `tests/test_image_fit_modes.py` — verify package-root imports for all four helpers.

## Design constraints

- Keep the existing helper names, signatures, return tuples, and arithmetic unchanged.
- Preserve direct imports from `foundation_tools.presentation.image_fit`.
- Do not add aliases or a dispatch wrapper.

## TDD steps

1. Change `tests/test_image_fit_modes.py` to import all four helpers from `foundation_tools.presentation`; confirm collection fails because three names are absent.
2. Add the three imports and `__all__` entries in `src/foundation_tools/presentation/__init__.py`.
3. Run the focused test, then both repository gates.

## Acceptance criteria

- [x] `from foundation_tools.presentation import cover_into_box, fit_height_into_box, fit_into_box, fit_width_into_box` succeeds in a fresh interpreter.
- [x] `foundation_tools.presentation.__all__` contains each helper exactly once.
- [x] `pytest tests/test_image_fit_modes.py` passes.
- [x] `make fullCheck` and `make uv-fullCheck` pass.

## Out of scope

- Geometry behavior, invalid-dimension semantics, focal-point cropping, and schema changes.
- Changes to downstream placement code.

## Spec back-reference

- [Presentation Schema R18](../../specs/presentationSchema.md#r18--media-fit-intent-and-region-aspect-fa-03)
- Package public-surface declaration: `src/foundation_tools/presentation/__init__.py` lines 8–10.

## Ask ↔ result

The recorded ask requested an action plan to close presentation failure-analysis gaps, and this chunk's goal narrowed one corrective action to exporting every public media-fit helper from the presentation package root. The live request to execute chunk 08 authorized implementing that planned correction. The package root now imports and exports all four existing helpers, and the focused test verifies package-root imports plus exactly one `__all__` entry per helper. The fresh-interpreter probe, focused test, code-generation gate, and both repository gates passed. No gap remains against this chunk's goal.
