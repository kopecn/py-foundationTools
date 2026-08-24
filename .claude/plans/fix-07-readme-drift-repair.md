---
plan: Fix07ReadmeDriftRepair
scope: project
status: pending
last_updated: 2026-08-23
semver: 0.0.1
author: Nicholas Bergantz
---

# Fix 07 — README Drift Repair

## Goal

Make the public onboarding path executable again: every documented import, method,
and Make target must exist in the current repository.

## Depends on

Fixes 01–06, so README wording describes the hardened behavior and final public
surface rather than an intermediate state.

## Defects

The README currently contains:

- removed module imports such as
  `foundationTypes.mathTypes.UnitSphericalSmallCircle` and
  `foundationTypes.mathTypes.QuaternionType`;
- camelCase `saveToFile`/`loadFromFile` calls instead of
  `save_to_file`/`load_from_file`;
- obsolete Make targets including `devInstall`, `lint`, `format`, `releaseTest`,
  `cleanBuild`, `cleanTest`, `docs`, and camelCase bump targets;
- descriptions of pylint/black even though the repository uses Ruff;
- a stale single-test path in `CONTRIBUTING.md`.

## Files

Edit:

- `README.md`
- `CONTRIBUTING.md`
- `.claude/CLAUDE.md` (remove the warning that the README is stale once it is true no
  longer)

Create:

- `tests/test_documentation_contract.py`

## Design constraints

**Document actual import paths.** Consolidated math models come from
`foundationTypes.mathTypes.MathTypes` using their generated class names, including
`UnitSphericalSmallCircleType`, `UnitSphericalArcType`, and `QuaternionType`.

**Use the Makefile as source of truth.** Replace commands with current targets:

- setup: `make dev`, `make e`;
- quality: `make test`, `make testInEnv`, `make uv-lint`, `make uv-format`,
  `make uv-typecheck`, `make uv-fullCheck`;
- build/release: `make build`, `make validateBuild`, `make release-test`, `make release`;
- cleanup: `make clean`, `make clean-build`, `make clean-test`;
- versions: `make bump-patch`, `make bump-minor`, `make bump-major`.

Do not advertise a Sphinx/docs target that does not exist. State plainly that the
repository currently ships Markdown documentation only.

**Prevent recurrence without parsing prose as a language.** The documentation contract
test should smoke-import every symbol used in the quick start and assert the curated
set of documented Make targets appears in `make help`. It should not snapshot the
entire README or fail on harmless prose changes.

**Examples remain safe.** File-I/O smoke examples use `tmp_path`; CLI examples use a
list-form command where practical and never execute deployment/SSH/rsync operations.

## Steps (TDD)

1. Add smoke tests for the README's intended public imports and snake_case data-model
   file methods. They fail against the currently documented paths/names.
2. Add a curated Make-target test based on `make help`.
3. Rewrite the README quick starts and development workflow to match the current API.
4. Fix the stale targeted-test example in `CONTRIBUTING.md`.
5. Remove the stale-README warning from `.claude/CLAUDE.md` and leave its command list
   synchronized with the corrected README.
6. Run every quick-start snippet in a clean interpreter or focused test.
7. Run `make uv-fullCheck`.

## Acceptance criteria

- [ ] Every README Python import succeeds in a fresh interpreter after installation.
- [ ] Data-model examples use `save_to_file` and `load_from_file`.
- [ ] Every advertised Make target appears in `make help`.
- [ ] No README reference to pylint, black, the removed math modules, or dead targets
  remains.
- [ ] `CONTRIBUTING.md` names an existing targeted test.
- [ ] `.claude/CLAUDE.md` no longer instructs agents to distrust the README.
- [ ] `make uv-fullCheck` passes.

## Out of scope

- Building a Sphinx/MkDocs documentation site.
- Reorganizing the public package namespace or adding compatibility alias modules.
- Broad prose/branding changes unrelated to executable accuracy.
- Publishing a release.

