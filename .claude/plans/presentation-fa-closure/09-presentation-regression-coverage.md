---
human_ask: >
  a series of FA's was generated from the first use of the build presentation tool.
  please review:
  /Users/nbergantz/__Workspaces__/pythonWorkspaces/py-clerical-tools/.claude/fa_reports
  and create a series action plan on closing these gaps.
goal: Add durable assertions for the implemented R15–R22 schema and geometry contracts.
last_updated: 2026-09-23
semver: 0.0.1
author: Nicholas Bergantz
status: pending
---

# 09 — Presentation regression coverage

Serves [Summary goal](./00-overview.md#summary-goal) · [Original ask](./00-original-ask.md).

## Goal

Close the confirmed test-only gaps without changing schemas, generated models, or runtime behavior.

## Origin

PA-02: valid round-trip tests exist, but several raw JSON Schema constraints, exact cover crop results, and generated class names consumed by the sibling repository are not directly guarded.

## Deliverable

Focused tests mechanically assert the implemented schema properties behind R15–R22, the exact centered cover crop, and the generated names `ContentType`, `RegionType`, and `Style`.

## Files

- `tests/typeTests/test_presentation_schema_shape.py` — add raw-schema assertions for the FA-closure fields.
- `tests/test_image_fit_modes.py` — assert exact horizontal and vertical cover crop fractions.
- `tests/typeTests/testPresentations.py` — add an import-time guard for the three externally consumed generated class names.
- `tests/test_presentation_diagram_styles.py` — assert `themeBinding` and `classRoles` schema shape already implemented by R19.

## Design constraints

- Test existing behavior only; do not edit production code, schemas, codegen scripts, or generated output.
- Inspect parsed schema dictionaries rather than adding a runtime JSON Schema dependency.
- Preserve the human-approved boundary recorded in [`fix-17`](../../archive/plans/repository-hardening/fix-17-presentation-schema-runtime-contract.md): JSON Schema owns validation, while generated models remain typed representations rather than validators.
- Assert only requirements explicit in R15–R22 and the completed chunks; do not encode an object-closure policy, class-name regex, invalid-dimension behavior, or new enum vocabulary.
- Keep schema assertions grouped by requirement so a failure names the affected contract.

## TDD steps

1. Add schema assertions for enum membership, numeric/array bounds, `$ref` reuse, optionality, and declared/default absence or presence exactly as R15–R22 specify.
2. Add exact crop assertions: a 2000×500 source covering a 1000×1000 box crops `0.375` from each horizontal side, and the transposed case crops `0.375` vertically.
3. Add direct imports of `ContentType`, `RegionType`, and `Style` from the generated module.
4. Demonstrate each new assertion fails when its inspected in-memory value is temporarily mutated, restore it, then run the focused tests and both gates.

## Acceptance criteria

- [ ] R15 assertions cover `shrink`, `maxLines.minimum == 1`, `scaleLadder.items.type == number`, optionality, and no new default.
- [ ] R16 assertions cover the exact bullet-style enum, bullet indent bounds, paragraph-rhythm minima, optionality, and no defaults.
- [ ] R17 assertions cover the three shared style `$ref` values, metric-gap minimum, permitted-flag types, optionality, and no defaults.
- [ ] R18 assertions cover the exact fit enum and `contain` default, focal-point bounds, aspect/fill bounds, and optionality.
- [ ] R19 assertions cover semantic color refs, the `classRoles` value `$ref`, the exact `themeBinding` enum, and absence of a `themeBinding` default without adding closure requirements.
- [ ] R20 assertions cover the content-type `$ref`, occupancy enum, capacity minima, and optional/default-free shape without changing agent-derived role/purpose/density vocabularies.
- [ ] R21–R22 assertions cover `altText`, font fallback/substitution fields, and `keywords` as optional/default-free additions.
- [ ] Cover tests assert `0.375` crop fractions for both orientations.
- [ ] `ContentType`, `RegionType`, and `Style` import successfully by name.
- [ ] `make codegen-all` leaves the worktree unchanged; `make fullCheck` and `make uv-fullCheck` pass.

## Out of scope

- Runtime enforcement of JSON Schema bounds by generated `from_dict` methods; the approved contract assigns validation to an application boundary.
- New schema constraints, enum changes, object closure, downstream renderer tests, and codegen pipeline changes.

## Spec back-reference

- [Presentation Schema R15–R22](../../specs/presentationSchema.md#r15--responsive-fit-budget-fa-01)
