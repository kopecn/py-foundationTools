---
plan: Fix18RemoteTransferValueObjects
scope: project
status: needs-approval
last_updated: 2026-09-05
semver: 1.1.0
author: Nicholas Bergantz
---

# Fix candidate 18 — valid SSH/rsync transfer configuration

Evidence: rsync construction accepts ten contextual parameters and repeats most of them
across four transaction methods. Combinations such as `ssh_user` without a host are silently
ignored, `remote_side` is meaningful only in remote mode, and SSH transport formatting is
duplicated "by hand." The exported `WINDOWS_SAFE_RSYNC_OPTIONS` constant is a mutable list.

Minimum fix: model local and remote endpoints plus transfer direction/options as immutable
value objects whose constructors reject invalid combinations. Share SSH transport formatting,
reduce forwarding duplication, quote/encode identity paths correctly for rsync `-e`, and
publish immutable option presets.

Do not change rsync defaults, invent remote hosts from ambient configuration, or retain every
invalid keyword combination through compatibility branches unless separately approved.

## Session note — 2026-09-05 (BLOCKED; not executed)

An execution attempt this session (user approved fix-18 on 2026-09-05) stopped without
changing code. Two issues need a human decision.

**1. Spec contradiction on `ssh_user` without host.** fix-18's defect statement and
required-work item 1 name *"`ssh_user` without a host"* as an invalid combination to
reject at construction. [`rsyncTransact.md`](../specs/rsyncTransact.md) mandates the
opposite: *"`ssh_user` alone SHALL NOT trigger injection and SHALL NOT raise; it remains
ignored in local mode (unchanged rule)"*, and Compliance Requirement 13 deliberately
scopes the build-time `ValueError` to `ssh_port` / `ssh_identity_file` without host,
excluding `ssh_user`. Enforced by passing tests in `tests/test_builders.py`
(`TestBuildRsyncCommandHostlessSshGuard`, `TestBuildRsyncCommandGoldenArgvNoneSweep`).
Same tension for `remote_side` silently ignored in local mode (spec `.md` silent, but
builder docstring + golden sweep exercise the no-raise behavior).

**2. Additive vs. replacement scope.** `fix-00-overview.md` frames fix-18 as *"replace
SSH/rsync parameter combinations with valid endpoint/transfer values"*, but
`rsyncTransact.md` describes the current ~10-loose-kwarg model across six normative
sections. Need direction:

- **(a) additive** — value objects are a new optional layer; `build_rsync_command`'s
  speced kwarg contract (including the `ssh_user`-alone rule) stays byte-for-byte intact.
  Satisfies the spec; leaves the "silently ignored kwarg" path fix-18 calls the defect.
- **(b) replacement** — the loose-kwarg public surface is genuinely replaced (breaking);
  `rsyncTransact.md` is revised separately by the spec owner first.

**Non-blocked subset** (could proceed under either path, no spec conflict): make
`WINDOWS_SAFE_RSYNC_OPTIONS` immutable (`list` → `tuple`); one shared SSH transport
formatter consumed by both `ssh_builder` and `rsync_builder` (replacing the hand-mirrored
`_build_ssh_transport_argument`), with `shlex.quote` on identity paths in the `-e` string;
collapse the four-method kwarg duplication in `RsyncTransact` behind one internal helper.

Status stays `needs-approval` (blocked).
