---
plan: ActionPlan12DocsAndDriftSync
scope: project
status: pending
last_updated: 2026-07-03
semver: 0.0.2
author: Nicholas Bergantz
---

# 12 — Docs & Drift Sync (final gate)

## Goal

Close the loop: make every document tell the truth about the shipped stack, and
pass the full CI gate one last time.

## Depends on

All other chunks (run last).

## Files

- `.claude/CLAUDE.md` — flip "planned" wording to "implemented" for shipped
  modules; verify import-path examples
- `.claude/specs/{cliTransact,sshTransact,rsyncTransact,socketTransact,transport_transaction_architecture}.md`
  — update `status:` frontmatter (`proposed`/`planned` → `implemented`), bump
  semver, correct any contract wording that shifted during implementation
- `README.md` — only the section touching the transaction stack, if any
- `.claude/action-plan/*.md` — mark chunk `status:` fields `done`

## Steps

1. Run a drift pass over the touched specs (the repo-to-spec-sync discipline):
   compare each spec's compliance list against the code and tests; fix the spec,
   never invent unimplemented claims.
2. Sweep for stale references:
   `grep -ri "foundationCLIHelpers" src/ tests/ README.md examples/` must return
   nothing. Exempt by design: cliTransact.md's intentional naming-history note and
   `.claude/action-plan/` / `.claude/plans/` files that record the rename. Every
   `applies_to:` path must exist.
3. Verify frontmatter on all touched markdown (`last_updated`, `semver`, `author`).
4. `make fullCheck` and `make testInEnv` (packaging path validates the new
   subpackages ship).

## Acceptance criteria

- [ ] Zero `foundationCLIHelpers` references in `src/`, `tests/`, `README.md`,
      and `examples/` (spec/plan naming-history notes exempt).
- [ ] Every spec `status:` and `applies_to:` matches reality.
- [ ] `make fullCheck` and `make testInEnv` pass.

## Out of scope

- New features of any kind.
- README overhaul beyond the transaction-stack section (the README's stale tooling
  claims are a separately-scoped known issue).
