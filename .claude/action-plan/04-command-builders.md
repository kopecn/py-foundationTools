---
plan: ActionPlan04CommandBuilders
scope: project
status: pending
last_updated: 2026-07-03
semver: 0.0.1
author: Nicholas Bergantz
---

# 04 — Command Builders

## Goal

Implement the pure, deterministic command builders for SSH and rsync. Builders
return command vectors and never execute anything.

Contracts: Layer 2 of
[transport_transaction_architecture.md](../specs/transport_transaction_architecture.md);
construction rules in [sshTransact.md](../specs/sshTransact.md) and
[rsyncTransact.md](../specs/rsyncTransact.md).

## Depends on

03 (sequencing only — builders have no code dependency on policies).

## Files

- `src/foundation_tools/builders/ssh_builder.py`
- `src/foundation_tools/builders/rsync_builder.py`
- `src/foundation_tools/builders/__init__.py` (exports)
- `tests/test_builders.py`

## Design constraints

**SSH builder** (`build_ssh_command(...) -> list[str]`):
- always `-p <port>` (even 22); `-i <identity_file>` only when supplied (no
  validation); target `user@host` when user given, else `host`
- remote command contract: `str` → single remote-shell argument;
  `list[str]` → argv segments appended

**Rsync builder** (`build_rsync_command(...) -> list[str]`, never `str`):
- option precedence exactly: `options` not None → use exactly; `[]` → no defaults;
  None → `default_options`. No merging, no dedup, caller order preserved.
- SSH injection via `-e "ssh -p PORT [-i FILE]"` whenever any of `ssh_host`,
  non-default `ssh_port`, `ssh_identity_file` present; reuse the SSH builder's
  formatting rules for the inner command.
- `src`/`dst` accept `str | Path` (stringified); remote side formatted
  `[user@]host:path`; local/pull/push modes.
- expose `WINDOWS_SAFE_RSYNC_OPTIONS = ["-avz", "--partial", "--append-verify",
  "--timeout=30", "--contimeout=15"]` — a recommendation constant, never applied
  automatically.
- `blocking_io: bool = False` appends `--blocking-io`; opt-in only, never in the
  preset.
- pure: no filesystem probing, no env inspection, no side effects.

## Steps (TDD)

1. Tests first: golden argv comparisons for every rule above (precedence matrix,
   SSH-injection triggers, preset content, determinism: same input → identical list).
2. Implement `ssh_builder`, then `rsync_builder` (reusing ssh formatting).
3. `make fullCheck`.

## Acceptance criteria

- [ ] Builders import nothing from subprocess, policies, or transactions.
- [ ] Every construction rule in both specs has a golden-argv test.
- [ ] `make fullCheck` passes.

## Out of scope

- Executing commands, success semantics, retries (transactions own delegation).
- Docker/Git/Kubectl builders (extension model exists; add on demand).
