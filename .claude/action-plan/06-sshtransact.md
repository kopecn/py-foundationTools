---
plan: ActionPlan06SSHTransact
scope: project
status: pending
last_updated: 2026-07-03
semver: 0.0.1
author: Nicholas Bergantz
---

# 06 — SSHTransact

## Goal

Implement the thin SSH transport transaction: build → delegate to `CLITransact` →
return unchanged.

Contract: [sshTransact.md](../specs/sshTransact.md).

## Depends on

04 (ssh builder), 03 (policy layer, for the optional parameter).

## Files

- `src/foundation_tools/cli_transaction/sshTransact.py`
- `src/foundation_tools/cli_transaction/__init__.py` (add export)
- `tests/test_ssh_transact.py`

## Design constraints

- Exactly four stateless classmethods mirroring `CLITransact`
  (`run_sync` / `run_async` / `run_sync_with_model` / `run_async_with_model`),
  keyword-only `timeout` / `success_marker`, plus optional `retry_policy` — when
  supplied, execution routes through the policy; SSHTransact itself implements zero
  retry logic (policy-ownership rule).
- Command construction delegated to `build_ssh_command` (chunk 04); no inline argv
  assembly.
- No result modification, no parsing, no exception handling; forwards
  `output_parser` / `timeout` / `success_marker` unchanged.

## Steps (TDD)

1. Tests first: each method builds the expected argv (assert via mock/spy on
   `CLITransact`) and returns the kernel result identically; `str` vs `list`
   remote-command modes; policy pass-through invoked when supplied; live smoke test
   against `CLITransact` using a local command only if practical (no network in CI).
2. Implement the four methods.
3. `make fullCheck`.

## Acceptance criteria

- [ ] All 10 Compliance Requirements in sshTransact.md have tests.
- [ ] Module contains no subprocess import, no try/except, no result mutation.
- [ ] `make fullCheck` passes.

## Out of scope

- SCP/SFTP, connection multiplexing, known-hosts management.
- Retry implementation (policies own it).
