---
human_ask: >
  a series of FA's was generated from the first use of the build presentation tool.
  please review:
  /Users/nbergantz/__Workspaces__/pythonWorkspaces/py-clerical-tools/.claude/fa_reports
  and create a series action plan on closing these gaps.
goal: Align the presentation and codegen specs with verified repository behavior and authoring rules.
last_updated: 2026-09-28
semver: 0.0.2
author: Nicholas Bergantz
status: active
---

# 10 — Documentation and convention alignment

Serves [Summary goal](./00-overview.md#summary-goal) · [Original ask](./00-original-ask.md).

## Goal

Remove confirmed descriptive drift from the two governing specifications without changing unresolved contracts or implementation behavior.

## Origin

PA-03–PA-08: the governing specs contain stale implementation/tooling claims, omit required authoring structure, and contradict implemented single-property, geometry-ownership, and metadata behavior.

## Dependencies

Run after chunks 08 and 09 so descriptive status reflects the final verified implementation and tests.

## Deliverable

The presentation and codegen specifications accurately describe the implemented repository state and current black-based codegen pipeline, while preserving unresolved decisions as open rather than silently choosing them.

## Files

- `.claude/specs/presentationSchema.md` — correct stale implementation-status prose and normalize required spec metadata/structure.
- `.claude/specs/schemaCodegen.md` — replace stale `run_ruff`/ruff pipeline statements with the verified `run_black`/black pipeline and normalize required spec metadata/structure.

## Design constraints

- Add `version`, `type`, `name`, and `purpose` frontmatter while preserving existing project-specific fields; bump each spec's semver minor and `last_updated`.
- Rename or add an explicit `## Goal` or `## Scope` section without duplicating the existing overview content.
- In `presentationSchema.md`, remove the false claim that no implementation, codegen script, or generated package exists and remove the internally contradictory “proposed, pending gate” label.
- Do not claim that repository artifacts independently prove the historical human scope gate.
- Align R18/R20 wording with the implemented single-definition outcome: `preferredAspectRatio` is one shared property on `region`; do not add a redundant definition or `$ref`.
- Align R18 ownership with the source-authorized image plan: this repository owns pure fit geometry, while downstream owns intrinsic-dimension reading and placement.
- Clarify R22 without changing schema behavior: `description`, `author`, and `version` are reused pre-existing fields with their existing required/default semantics; `keywords` is the new optional/default-free field.
- Do not change normative behavior for invalid media dimensions, diagram-object closure, role/purpose/density vocabularies, or runtime JSON Schema validation.
- In `schemaCodegen.md`, describe the actual canonical order ending in `run_black` then `ensure_py_typed`; state that normalization runs inside `run_black` and the fleet-wide `make codegen-all` sweep formats with black.
- Do not edit historical completion narratives in chunks 01–07.

## TDD steps

1. Add or update documentation checks if the repository has an applicable structural test; otherwise use exact `rg` assertions for removed stale terms and required replacement terms.
2. Edit only the two listed specifications.
3. Verify local Markdown links still resolve, then run both repository gates.

## Acceptance criteria

- [x] Neither spec lacks `version`, `type`, `name`, `purpose`, `last_updated`, `semver`, or `author` frontmatter.
- [x] Each spec has an explicit `## Goal` or `## Scope` section.
- [x] `presentationSchema.md` no longer says the implemented domain, generator, or generated package does not exist.
- [x] The FA-closure heading no longer says “proposed, pending gate,” and no new claim of independently verified historical approval is added.
- [x] R18/R20 describe one shared `region.preferredAspectRatio` property without requiring a redundant `$ref`.
- [x] R18 assigns pure fit geometry to this repository and intrinsic-dimension reading/placement downstream.
- [x] R22 distinguishes reused metadata fields from the new optional/default-free `keywords` field.
- [x] `schemaCodegen.md` contains no `run_ruff`, `ruff format`, `ruff check`, or ruff-autofix pipeline claim.
- [x] `schemaCodegen.md` matches `schema/scripts/generateDiskUsage.sh`, `schema/scripts/reuse/codegen.sh`, and `make codegen-all` on `run_black`, normalization, and black formatting.
- [ ] `make fullCheck` and `make uv-fullCheck` pass. — `make fullCheck` passes (flake8, mypy --strict on 69+52 files, 981 tests). `make uv-fullCheck` fails at `uv-lint` on a pre-existing, unrelated flake8-bugbear finding (`tests/test_transaction_codecs.py:69:13: B018`), confirmed present on this branch before this chunk's edits via `git stash` (this chunk touched only the two spec files). Left unchecked and reported, not fixed — `tests/` is explicitly Out of scope for this chunk.

## Out of scope

- Production code, schemas, generated models, tests, and downstream documentation.
- Resolving any item listed under the overview's “Recorded, no action” table.

## Ask ↔ result

- **`human_ask` / `goal`**: the overview's `human_ask` records the original FA-review request; this chunk's own `goal` is to align the presentation and codegen specs with verified repository behavior and authoring rules. The two agree — no internal conflict.
- **Live request**: `/execute-plan .claude/plans/presentation-fa-closure/10-documentation-convention-alignment.md`, authorizing execution of this chunk now (chunks 08 and 09, its dependencies, are both `status: completed`).
- **Delivered** (each correction verified against live repository state before writing, not assumed):
  - PA-03 — removed the false claim that no implementation/codegen script/generated package exists; confirmed `schema/scripts/generatePresentations.sh` and `src/foundationTypes/presentationTypes/Presentations.py` both exist. `status: draft` is kept but now explained as "broader lifecycle open," not "nothing implemented."
  - PA-04 — replaced every `run_ruff` pipeline claim in `schemaCodegen.md` with the verified `run_black` pipeline, confirmed by reading `schema/scripts/generateDiskUsage.sh`, `schema/scripts/reuse/codegen.sh` (no `run_ruff` function exists; `run_black` calls `fix_to_dict_return_type` + `fix_from_dict_classmethod` + black), and the Makefile's `codegen-all` target (black-only fleet sweep, no ruff).
  - PA-05 — added `version`, `type`, `name`, `purpose` frontmatter (per the cited `spec-authoring.md` Required Frontmatter) to both specs, preserving existing project-specific keys; bumped each spec's semver minor (`presentationSchema.md` 0.9.0 → 0.10.0, `schemaCodegen.md` 0.5.0 → 0.6.0) and `last_updated` to 2026-09-28. Added an explicit `## Goal` section to each, distinct from the existing `## Overview`.
  - PA-06 — reworded R18/R20 to state `region.preferredAspectRatio` is one shared property (confirmed by reading `PresentationSlideLayouts-schema.json`: the property is declared once, as a plain `number`, never `$ref`'d), removing the "defined once and `$ref`'d" claim.
  - PA-07 — reworded R18 to assign pure fit geometry (the placement-rectangle math) to this repository, confirmed by reading `src/foundation_tools/presentation/image_fit.py` (`fit_into_box`, `cover_into_box`, `fit_width_into_box`, `fit_height_into_box`) and the source-authorized image plan (`archive/plans/presentation-schema/12-presentation-image-block.md`: "Contain-fit geometry ... belongs here; reading image pixel dimensions needs a library and stays downstream" / "the actual `add_picture` render is the clerical-tools half"). Intrinsic-dimension reading and the actual rendered placement (e.g. `add_picture`) remain downstream.
  - PA-08 — reworded R22 to state `description`, `author`, and `version` predate this chunk with their existing required/default semantics, and `keywords` is the field R22 actually added — confirmed by reading `PresentationMetadata-schema.json` (`author` required, `description`/`version` each carry an existing default, `keywords` has neither) and `git log --follow -p`, which shows `author`/`description`/`version` added in commit `d1fd125` (2026-09-08) and only `keywords` (plus unrelated R21 fields) added in commit `ea3feb8` (2026-09-15, chunk 07).
  - No production code, schema, generated model, or test file was touched; no item from the overview's "Recorded, no action" table was resolved.
- **Gap**: `make uv-fullCheck` does not pass, for a reason unrelated to and pre-dating this chunk's changes (see the unchecked acceptance box above). This is a pre-existing gate blocker recorded for human review, not resolved unilaterally, since fixing it would require editing `tests/`, which this chunk's Out-of-scope section forbids.

## Spec back-reference

- User specification-authoring rules: `/Users/nbergantz/.environment/claude-skills-memory/claude/specs/principles/spec-authoring.md`
- Project [Presentation Schema](../../specs/presentationSchema.md)
- Project [Schema Codegen](../../specs/schemaCodegen.md)
