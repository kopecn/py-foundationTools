---
human_ask: >
  a series of FA's was generated from the first use of the build presentation tool.
  please review:
  /Users/nbergantz/__Workspaces__/pythonWorkspaces/py-clerical-tools/.claude/fa_reports
  and create a series action plan on closing these gaps.
goal: Align the presentation and codegen specs with verified repository behavior and authoring rules.
last_updated: 2026-09-23
semver: 0.0.1
author: Nicholas Bergantz
status: pending
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

- [ ] Neither spec lacks `version`, `type`, `name`, `purpose`, `last_updated`, `semver`, or `author` frontmatter.
- [ ] Each spec has an explicit `## Goal` or `## Scope` section.
- [ ] `presentationSchema.md` no longer says the implemented domain, generator, or generated package does not exist.
- [ ] The FA-closure heading no longer says “proposed, pending gate,” and no new claim of independently verified historical approval is added.
- [ ] R18/R20 describe one shared `region.preferredAspectRatio` property without requiring a redundant `$ref`.
- [ ] R18 assigns pure fit geometry to this repository and intrinsic-dimension reading/placement downstream.
- [ ] R22 distinguishes reused metadata fields from the new optional/default-free `keywords` field.
- [ ] `schemaCodegen.md` contains no `run_ruff`, `ruff format`, `ruff check`, or ruff-autofix pipeline claim.
- [ ] `schemaCodegen.md` matches `schema/scripts/generateDiskUsage.sh`, `schema/scripts/reuse/codegen.sh`, and `make codegen-all` on `run_black`, normalization, and black formatting.
- [ ] `make fullCheck` and `make uv-fullCheck` pass.

## Out of scope

- Production code, schemas, generated models, tests, and downstream documentation.
- Resolving any item listed under the overview's “Recorded, no action” table.

## Spec back-reference

- User specification-authoring rules: `/Users/nbergantz/.environment/claude-skills-memory/claude/specs/principles/spec-authoring.md`
- Project [Presentation Schema](../../specs/presentationSchema.md)
- Project [Schema Codegen](../../specs/schemaCodegen.md)
