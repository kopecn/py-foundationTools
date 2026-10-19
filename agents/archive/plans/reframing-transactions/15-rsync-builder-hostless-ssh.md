---
plan: ActionPlan15RsyncBuilderHostlessSsh
scope: project
status: complete
last_updated: 2026-07-06
semver: 0.2.0
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

- [x] Host-less injection triggers `ValueError` at build time; no argv containing
      `"None:"` can be produced.
- [x] All existing golden-argv tests pass unchanged (valid combinations
      unaffected).
- [x] `rsyncTransact.md` documents the validation boundary; frontmatter bumped.
- [x] `make uv-fullCheck` passes.

## Out of scope

- Changing the injection-trigger rule itself (any-of-three stays).
- Extracting a shared ssh-formatting helper (recorded as declined, see design
  constraints).
- Validation of other argument combinations not implicated by the finding.

## Resolution notes

- Added the `ValueError` guard in `build_rsync_command`
  (`src/foundation_tools/builders/rsync_builder.py`): raised when SSH injection is
  triggered (`ssh_host`/`ssh_port`/`ssh_identity_file` any-of-three, unchanged)
  but `ssh_host is None`. `ssh_user` alone still does not trigger injection and
  does not raise.
- New tests: `TestBuildRsyncCommandHostlessSshGuard` and
  `TestBuildRsyncCommandGoldenArgvNoneSweep` in `tests/test_builders.py` (the
  latter sweeps every combination of `ssh_host`/`ssh_user`/`ssh_port`/
  `ssh_identity_file`/`remote_side`, asserting any non-raising combination's argv
  contains no `"None"` substring); `TestRsyncTransactHostlessSshGuardPropagation`
  in `tests/test_rsync_transact.py` (asserts `CLITransact.run_sync` is never
  called when the builder raises).
- Deviation from "existing golden-argv tests pass unchanged": two pre-existing
  tests directly exercised the defect being fixed —
  `test_injected_when_only_ssh_port_supplied` and
  `test_injected_when_only_ssh_identity_file_supplied` in
  `TestBuildRsyncCommandSshInjection` asserted that port/identity-file alone
  (no `ssh_host`) produced a (buggy) injected command. These are exactly the
  invalid combinations the guard now rejects, so they were updated in place to
  assert `ValueError` (renamed to `..._but_host_missing_raises`) rather than left
  as regressions. All tests covering genuinely valid combinations are unchanged.
- `.claude/specs/rsyncTransact.md`: added "Validation: Host-less SSH Injection"
  section (rationale + the never-raise-is-about-execution-not-build-args
  boundary) and Compliance Requirement #13; semver 0.3.0 → 0.4.0,
  `last_updated` → 2026-07-06.
- Recorded-decision cross-reference comment added to
  `_build_ssh_transport_argument` in `rsync_builder.py`, pointing at
  `ssh_builder.py`'s formatting rules; no shared helper extracted (per design
  constraints).
- Gate: `make uv-fullCheck` passes (298 tests). `ruff format --check` also
  verified clean on all touched files (not part of `uv-fullCheck`, which
  excludes format per the Makefile's own comment, but checked anyway).
