---
plan: ActionPlan15RsyncBuilderHostlessSsh
scope: project
status: pending
last_updated: 2026-07-06
semver: 0.1.0
author: Nicholas Bergantz
---

# 15 — Rsync Builder Host-less SSH Injection (corrective)

## Goal

Fix the latent defect in `build_rsync_command`: SSH injection triggers when *any*
of `ssh_host`/`ssh_port`/`ssh_identity_file` is supplied, but when triggered by
`ssh_port` or `ssh_identity_file` **alone** (`ssh_host=None`), the remote side is
formatted as the literal string `"None:/path"` — an invalid rsync argv with no
guard and no test. `RsyncTransact` inherits the defect via passthrough.

Contract: [rsyncTransact.md](../specs/rsyncTransact.md) command-construction rules.

## Origin

Chunk 04/07 audit finding (corrective follow-up to plans 00–13).

## Depends on

None — independent.

## Files

- `src/foundation_tools/builders/rsync_builder.py` (validation guard)
- `.claude/specs/rsyncTransact.md` (validation clause; semver bump)
- `tests/test_builders.py` (ValueError cases, golden-argv `"None"` sweep)
- `tests/test_rsync_transact.py` (propagation test)

## Design constraints

- **Poka yoke**: `build_rsync_command` raises `ValueError` when SSH injection is
  triggered by `ssh_port`/`ssh_identity_file` but `ssh_host is None`. This is a
  build-time caller bug, distinct from execution failures; precedent: framing
  codecs raise `ValueError` at encode. Silently ignoring the port/identity (local
  fallback) would drop user intent and is rejected.
- The never-raise containment rule applies to **execution**, not to invalid
  arguments: `RsyncTransact` lets the builder's `ValueError` propagate before any
  subprocess is spawned. Document this boundary in `rsyncTransact.md` (validation
  clause + injection-trigger rule) and bump its semver in the same chunk
  (convention #5).
- `ssh_user` alone still does NOT trigger injection (unchanged rule); it remains
  ignored in local mode.
- Optional, recorded decision: `_build_ssh_transport_argument` stays a local
  mirror of the ssh formatting rules (the `-e` string vs argv shapes differ enough
  that extraction is not clearly better); add a cross-reference comment pointing
  at `ssh_builder.py` so the two cannot drift silently.

## Steps (TDD)

1. Failing tests first: `ssh_port` alone → `ValueError`; `ssh_identity_file`
   alone → `ValueError`; both without host → `ValueError`; golden-argv sweep
   asserting no valid injected command ever contains the substring `"None"`;
   `RsyncTransact.run_sync` propagation test (raises before execution, kernel
   never invoked — assert via mock).
2. Implement the guard in `build_rsync_command`.
3. Update `rsyncTransact.md` (validation clause, semver bump).
4. `make uv-fullCheck`.

## Acceptance criteria

- [ ] Host-less injection triggers `ValueError` at build time; no argv containing
      `"None:"` can be produced.
- [ ] All existing golden-argv tests pass unchanged (valid combinations
      unaffected).
- [ ] `rsyncTransact.md` documents the validation boundary; frontmatter bumped.
- [ ] `make uv-fullCheck` passes.

## Out of scope

- Changing the injection-trigger rule itself (any-of-three stays).
- Extracting a shared ssh-formatting helper (recorded as declined, see design
  constraints).
- Validation of other argument combinations not implicated by the finding.
