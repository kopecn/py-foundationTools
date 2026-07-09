---
plan: ActionPlan20RsyncGuardPropagationTests
scope: project
status: complete
last_updated: 2026-07-08
semver: 0.2.0
author: Nicholas Bergantz
---

# 20 — Rsync Guard Propagation Tests (corrective)

## Goal

Close the one coverage gap the second audit confirmed: `rsyncTransact.md`
Compliance Requirement #13 states the host-less-SSH `ValueError` propagates out
of **all four** `RsyncTransact` methods (`run_sync` / `run_async` /
`run_sync_with_model` / `run_async_with_model`) before any delegation to
`CLITransact`, but only `run_sync` has a propagation test
(`tests/test_rsync_transact.py::TestRsyncTransactHostlessSshGuardPropagation`).
The other three paths are correct in code (confirmed by runtime probe during the
audit — all raise the builder's `ValueError` with no subprocess spawned) but
unproven by the suite.

Contract: [rsyncTransact.md](../specs/rsyncTransact.md) Requirement #13 and
"Validation: Host-less SSH Injection" → "Boundary with the never-raise
containment rule".

## Origin

Second post-audit (2026-07-06, chunks 14–19) finding: category (b)
implemented-but-untested — spec claims four propagation paths, tests cover one.

## Depends on

None — independent (chunk 15's guard and spec clause are already in place).

## Files

- `tests/test_rsync_transact.py` (extend
  `TestRsyncTransactHostlessSshGuardPropagation`)

## Design constraints

- Tests-only chunk; zero production or spec changes expected. If a test exposes
  a real defect, fix minimally in this chunk and record it in the resolution
  notes (spec bump if contract-visible).
- Mirror the existing `run_sync` propagation test's shape: patch the
  corresponding `CLITransact` kernel method, assert `pytest.raises(ValueError)`,
  and assert the kernel mock was never called. Async variants use the module's
  existing `pytest-asyncio` pattern.
- `*_with_model` variants need a trivial `output_parser` argument; any callable
  satisfies the signature since it must never be reached.
- Reuse the existing fixtures/imports in `tests/test_rsync_transact.py`; no new
  fakes.

## Steps (TDD)

1. Add three tests to `TestRsyncTransactHostlessSshGuardPropagation`:
   `run_async`, `run_sync_with_model`, `run_async_with_model` — each with
   `ssh_port=2222` and no `ssh_host`, asserting `ValueError` propagates and the
   patched kernel method is never invoked. Expected outcome is pass (behavior
   exists); a failure is a defect handled per design constraints.
2. `make uv-fullCheck`.

## Acceptance criteria

- [x] All four methods named by Requirement #13 have a passing propagation test
      asserting the kernel is never invoked.
- [x] No production or spec changes (or, if a defect surfaced, it is fixed
      minimally and recorded in the resolution notes).
- [x] `make uv-fullCheck` passes.

## Out of scope

- Changing the guard, the injection-trigger rule, or the spec text.
- Any other `RsyncTransact` coverage not implicated by the finding.

## Resolution notes

Added `test_run_async_raises_before_kernel_invoked`,
`test_run_sync_with_model_raises_before_kernel_invoked`, and
`test_run_async_with_model_raises_before_kernel_invoked` to
`TestRsyncTransactHostlessSshGuardPropagation` in `tests/test_rsync_transact.py`,
mirroring the existing `run_sync` test's shape. All three passed on first run —
no defect surfaced; the guard already propagates correctly on every path. No
production or spec changes made. `make uv-fullCheck` passes (310/310 tests).
