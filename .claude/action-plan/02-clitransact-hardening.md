---
plan: ActionPlan02CLITransactHardening
scope: project
status: pending
last_updated: 2026-07-03
semver: 0.0.1
author: Nicholas Bergantz
---

# 02 — CLITransact Kernel Hardening

## Goal

Close the remaining review findings and lock the kernel contract with tests, so the
sibling layers build on a verified base.

Contract: [cliTransact.md](../specs/cliTransact.md).
Review source: [.claude/review-for-fixes/02-cliTransact.md](../review-for-fixes/02-cliTransact.md).

## Depends on

01 (package restructure).

## Files

- `src/foundation_tools/cli_transaction/cliTransact.py`
- `tests/test_cli_transact.py` (new or extend existing)

## Review findings status

- **Grace-period escalation** — already fixed in code (`GRACE_PERIOD_CAP_SECONDS`,
  `min(cap, timeout)`); add a regression test, no code change.
- **Fragile `success: bool = False` default** — open. Any code constructing
  `CLITransactResult` directly can forget `success`. Fix: route all construction
  through the existing `_finalize_result` / `_framework_error` factories and make
  that the documented rule (do **not** add `__post_init__` magic — the dataclass
  stays a dumb container per spec). Verify no construction site bypasses a factory.

## Steps (TDD)

1. Write contract tests (failing where behavior is untested):
   - success matrix: rc=0 ± marker present/absent; rc>0; rc=-1 sentinel
   - normalization: empty/whitespace stdout/stderr → `None`
   - containment: nonexistent binary, empty command, parser raise (stderr appended,
     `success` unchanged, `model is None`)
   - sync timeout partial-capture; async timeout `terminate → kill` with grace cap
     (short-timeout regression)
   - sync/async equivalence for the same command
2. Apply the factory-only construction fix.
3. `make fullCheck`.
4. Sync [cliTransact.md](../specs/cliTransact.md) if any contract wording shifted;
   bump its semver.

## Acceptance criteria

- [ ] Every Compliance Requirement in cliTransact.md has at least one test.
- [ ] No direct `CLITransactResult(...)` construction outside the factories.
- [ ] `make fullCheck` passes.

## Out of scope

- Retry/backoff (chunk 03), builders (04), any new public API.
- Changing the `str ⇒ shell` input contract.
