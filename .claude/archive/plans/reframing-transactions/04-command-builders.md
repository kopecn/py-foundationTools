---
plan: ActionPlan04CommandBuilders
scope: project
status: complete
last_updated: 2026-07-04
semver: 0.1.0
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
- `port: int | None = None` — `-p <port>` only when a port is supplied, never a
  synthesized default (a command-line `-p` overrides `~/.ssh/config` `Port`
  settings, breaking SSH aliases; see [sshTransact.md](../specs/sshTransact.md));
  `-i <identity_file>` only when supplied (no validation); target `user@host`
  when user given, else `host`
- remote command contract: `str` → single remote-shell argument;
  `list[str]` → argv segments appended

**Rsync builder** (`build_rsync_command(...) -> list[str]`, never `str`):
- option precedence exactly: `options` not None → use exactly; `[]` → no defaults;
  None → `default_options`. No merging, no dedup, caller order preserved.
- SSH injection via `-e "ssh [-p PORT] [-i FILE]"` whenever any of `ssh_host`,
  `ssh_port`, `ssh_identity_file` is supplied; reuse the SSH builder's
  formatting rules for the inner command (`-p` only when a port is supplied).
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

- [x] Builders import nothing from subprocess, policies, or transactions.
- [x] Every construction rule in both specs has a golden-argv test.
- [x] `make uv-fullCheck` passes (`make fullCheck` no longer exists).

## Out of scope

- Executing commands, success semantics, retries (transactions own delegation).
- Docker/Git/Kubectl builders (extension model exists; add on demand).

## Implementation notes

`rsyncTransact.md` describes pull/push modes but gives the builder no
filesystem-probing-free way to tell which of `src`/`dst` is remote from
`ssh_host` alone. Resolved by adding an explicit `remote_side: Literal["src",
"dst"] = "dst"` parameter (defaults to push, the common case); `"src"` selects
pull. Kept out of the spec's literal parameter list since it's additive and
doesn't change any documented rule — flagging here in case chunk 07
(`RsyncTransact`) wants to promote it into the spec itself.
