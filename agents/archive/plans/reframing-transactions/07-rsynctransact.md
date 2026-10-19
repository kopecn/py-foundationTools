---
plan: ActionPlan07RsyncTransact
scope: project
status: complete
last_updated: 2026-07-05
semver: 0.1.0
author: Nicholas Bergantz
---

# 07 — RsyncTransact

## Goal

Implement the rsync transport transaction: build via the rsync builder, optionally
route through a retry policy, delegate to `CLITransact`.

Contract: [rsyncTransact.md](../specs/rsyncTransact.md).

## Depends on

04 (rsync builder), 03 (policy layer).

## Files

- `src/foundation_tools/cli_transaction/rsyncTransact.py`
- `src/foundation_tools/cli_transaction/__init__.py` (add export)
- `tests/test_rsync_transact.py`

## Design constraints

- Same four stateless classmethods as `CLITransact`/`SSHTransact`; always passes
  `list[str]` argv to the kernel.
- `src`/`dst`: `str | Path`; local, pull, and push modes per spec.
- Optional `retry_policy` parameter (selection allowed, implementation forbidden).
  The documented recommended classification for that policy — transient
  `{10, 12, 30, 35, -1}`, permanent `{2, 4, 23, 24}` — is surfaced as a module
  constant callers can hand to `RetryPolicy`; RsyncTransact never retries by itself.
- Re-export `WINDOWS_SAFE_RSYNC_OPTIONS` from the builder; never applied
  automatically. `blocking_io` stays opt-in and out of the preset.
- Forwards `success_marker` / `output_parser` unchanged; no result mutation.

## Steps (TDD)

1. Tests first: argv delegation for local/pull/push, option-precedence matrix
   surfaced through the public API, SSH injection triggers, policy pass-through,
   result returned unchanged; a real local-to-local rsync smoke test if `rsync` is
   present (skip otherwise).
2. Implement the four methods.
3. `make fullCheck`.

## Acceptance criteria

- [x] All 12 Compliance Requirements in rsyncTransact.md have tests.
- [x] No subprocess import, no retry loop, no option merging/dedup in the module.
- [x] `make uv-fullCheck` passes (`make fullCheck` no longer exists).

## Out of scope

- rsync daemon (`rsync://`) mode, `--delete` safety rails, bandwidth limiting.
- Cross-run resume orchestration (higher-layer workflow concern).

## Implementation notes

Reused chunk 04's `remote_side: Literal["src", "dst"] = "dst"` parameter
(documented there) to select pull vs. push, since the spec doesn't otherwise give
the transaction a heuristic-free way to know which side is remote. The rsync
binary was present locally (`openrsync` on macOS), so the local-to-local smoke
test in the Steps section ran for real rather than being skipped.
