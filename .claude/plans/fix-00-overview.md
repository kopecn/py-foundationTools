---
plan: RepositoryHardeningOverview
scope: project
status: pending
last_updated: 2026-08-23
semver: 0.0.2
author: Nicholas Bergantz
---

# Repository Hardening Stack

## Goal

Close the seven concrete gaps found in the 2026-08-23 repository review without
mixing repo-wide maintenance into the presentation-domain roadmap.

This stack deliberately uses the `fix-` prefix. Presentation chunks keep their
existing `00`–`11` numbering and dependency graph.

## Baseline

At review time:

- `pytest`: 416 tests and 16 subtests pass when localhost socket access is available.
- `ruff check src tests`: passes.
- the Makefile's package-oriented strict-mypy workflow passes.
- the defects below are uncovered contract gaps, not existing red tests.

## Ordered stack

| # | plan | reason for position |
|---|---|---|
| 01 | [MCP schema JSON repair](fix-01-mcp-schema-json-repair.md) | Unblocks the fleet-wide codegen gate used by presentation chunk 02. |
| 02 | [Framing-codec configuration validation](fix-02-framing-codec-configuration-validation.md) | Removes two constructor states that can make `feed()` loop forever. |
| 03 | [Socket-router failure containment](fix-03-socket-router-failure-containment.md) | Converts malformed inbound data into deterministic request failure and clean teardown. |
| 04 | [Logger external-rotation detection](fix-04-logger-external-rotation-detection.md) | Makes the file handler honor its documented replacement/removal behavior. |
| 05 | [Path root containment](fix-05-path-root-containment.md) | Prevents `../` and absolute patterns from escaping the caller's declared root. |
| 06 | [Physical-constant finiteness](fix-06-physical-constant-finiteness.md) | Enforces the already-documented positive, finite uncertainty invariant. |
| 07 | [README drift repair](fix-07-readme-drift-repair.md) | Documents the corrected public surface and removes dead commands/imports. |
| 08 | [Generated `from_dict` guards raise `TypeError`](fix-08-generated-guard-typeerror.md) | Replaces quicktype's bare assert across all 190 generated guards; unblocks presentation chunk 05. |

## Dependency graph

```text
fix-01 MCP JSON ───────────────> presentation chunk 02 codegen
fix-08 generated guards ───────> presentation chunk 05 type-tests

fix-02 codec validation ───────> fix-03 router containment

fix-04 logger ─────────┐
fix-05 path containment├───────> fix-07 README drift repair
fix-06 constant finite ┘
```

`fix-04`, `fix-05`, and `fix-06` are independent and may be implemented in any
order. The numbered order is the preferred landing order, not an artificial code
dependency.

## Conventions for every fix

1. Reproduce the defect with a focused failing test before changing production code.
2. Preserve the zero-runtime-dependency rule; `[project].dependencies` remains empty.
3. Keep expected transaction failures in result/future channels instead of leaking
   background-task exceptions.
4. Add a user-facing bullet under `HISTORY.md` `[Unreleased]` when runtime behavior
   changes. Pure schema syntax and documentation repairs do not need a changelog item.
5. Do not hand-edit generated Python models. Schema changes go through the codegen
   pipeline.
6. Finish each chunk with its focused tests, then `make uv-fullCheck`.
7. Keep unrelated presentation work and existing untracked files untouched.

## Stack exit criteria

- [ ] Every linked plan's acceptance criteria pass.
- [ ] `make codegen-all` succeeds and is idempotent.
- [ ] `make uv-fullCheck` passes.
- [ ] README quick-start imports and commands match the actual package and Makefile.
- [ ] No runtime dependency is added.

