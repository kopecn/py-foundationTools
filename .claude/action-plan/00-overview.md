---
plan: ActionPlanOverviewMathABCs
scope: project
status: complete
last_updated: 2026-07-08
semver: 0.1.2
author: Nicholas Bergantz
---

# Action Plan — Math ABCs → `foundation_abc/math/`

Continues chunk numbering from the archived transaction/transport plan
([../archive/action-plan/00-overview.md](../archive/action-plan/00-overview.md),
chunks 01–20); its Conventions section (TDD, gate = `make uv-fullCheck`,
zero runtime deps, stay-in-scope, frontmatter, test naming) applies to every
chunk here unchanged.

## Chunk index

| # | chunk | status | depends on |
| --- | --- | --- | --- |
| 21 | [Math ABCs to foundation_abc](21-math-abcs-to-foundation-abc.md) | complete | — |
| 22 | [Math tier contract tests](22-math-tier-contract-tests.md) | complete | 21 |
| 23 | [Docs & convention sweep](23-docs-convention-sweep.md) | complete | 21 |

```
21 math ABCs move (complete)
├── 22 tier contract tests   (corrective, F1+F2)
└── 23 docs/convention sweep (corrective, F3+F4 — independent of 22)
```

## Corrective actions (post-audit, 2026-07-08)

Audit of chunk 21 (gate green: ruff + strict mypy + 312/312; all 13
reparentings, deletions, and spec edits verified firsthand). Verdict:
**substantially complete**; two implemented-but-untested gaps and two minor
convention drifts.

Findings → chunk traceability:

| finding | class | disposition |
| --- | --- | --- |
| F1 — ABC concrete `to_dict`s never executed; wire shape defined twice with no parity guard | (b) untested | chunk 22 |
| F2 — Invariant 4 (ABC-first base order) has no test | (b) untested | chunk 22 |
| F3 — chunk 21 frontmatter semver not bumped on execution edits | convention | chunk 23 |
| F4 — `mathEnums.py` docstring names nonexistent sibling modules | doc drift | chunk 23 |
| F5 — `*MathLike` docstring forward-refs; `schemaCodegen.md` golden-template staleness | out-of-scope (recorded in chunk 21) | no action |
| Investigation: keep `to_dict`/`from_dict` on the ABCs? | design question | **keep both**; parity test (chunk 22) mitigates the duplication cost |
