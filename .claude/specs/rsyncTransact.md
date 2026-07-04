---
spec: RsyncTransact
scope: project
status: planned
applies_to: src/foundation_tools/cli_transaction/rsyncTransact.py
last_updated: 2026-07-03
semver: 0.1.0
author: Nicholas Bergantz
---

# Rsync Transaction Manager Specification

> **Status — planned.**
>
> `RsyncTransact` is the rsync-specific command builder that sits immediately above
> `CLITransact`. It owns rsync command construction, transfer semantics, SSH transport
> injection, and rsync-specific behavioral policy. It **does not** execute subprocesses
> directly; all execution is delegated to `CLITransact`.
>
> This document defines the required contract for the future implementation.

---

# Overview

`RsyncTransact` provides a deterministic, stateless interface for constructing and
executing rsync file transfers.

It is responsible for:

- rsync command construction
- SSH transport injection
- local vs remote path construction
- option precedence
- Windows/MSYS2 compatibility options
- rsync-specific success policy
- delegation to `CLITransact`

It is **not** responsible for:

- subprocess execution
- timeout implementation
- stdout normalization
- success evaluation
- exception containment
- retry/backoff execution

Those behaviors belong to `CLITransact` or higher orchestration layers.

---

# System Role

```text
Application
      │
      ▼
Retry Policy (planned)
      │
      ▼
RsyncTransact
      │
      ▼
CLITransact
      │
      ▼
subprocess
```

The responsibility boundary is strict:

- `RsyncTransact` builds commands.
- `CLITransact` executes commands.

`RsyncTransact` MUST NEVER call `subprocess`, `asyncio.create_subprocess_exec`, or
`subprocess.run` directly.

---

# Design Philosophy

`RsyncTransact` is a command builder—not a transfer engine.

Its responsibilities are deliberately narrow:

- deterministic
- stateless
- functional
- transport-aware
- execution-agnostic

Every public API constructs an rsync command and immediately delegates execution to
`CLITransact`.

---

# Public API

The public API mirrors `CLITransact`.

Exactly four stateless class methods SHALL exist.

| method | returns |
|----------|----------|
| `run_sync(...)` | `CLITransactResult` |
| `run_async(...)` | `CLITransactResult` |
| `run_sync_with_model(...)` | `CLITransactResultModel[T]` |
| `run_async_with_model(...)` | `CLITransactResultModel[T]` |

No public method owns execution logic.

Every method SHALL perform:

```text
build rsync argv

↓

delegate to CLITransact

↓

return CLITransactResult
```

---

# Input Contract

Source and destination accept

```python
str | Path
```

Both SHALL be converted internally to strings before command construction.

---

# Transfer Modes

The module supports both local and remote transfers.

## Local

```text
/source/path

↓

/destination/path
```

No SSH transport is constructed.

---

## Pull

When `ssh_host` is provided:

```text
remote:path

↓

local
```

The source SHALL become

```text
[user@]host:path
```

---

## Push

Future implementations SHALL support

```text
local

↓

[user@]host:path
```

without changing the public API.

---

# SSH Transport

SSH transport is constructed inline using rsync's

```text
-e
```

option.

Example:

```text
-e "ssh -p 2222 -i ~/.ssh/key"
```

SSH transport SHALL be injected whenever any of the following are present:

- `ssh_host`
- non-default `ssh_port`
- `ssh_identity_file`

The SSH command is constructed independently of rsync options.

---

# SSH Construction Rules

The generated SSH command SHALL follow:

```text
ssh
```

always

```text
-p PORT
```

always present (including port 22)

```text
-i identity_file
```

only when supplied

Host formatting:

```text
user@host
```

when a user exists

otherwise

```text
host
```

---

# Option Precedence

Option precedence is an explicit invariant.

```text
options != None

↓

use options exactly
```

```text
options == []

↓

disable all defaults
```

```text
options is None

↓

use default_options
```

No merging occurs.

No deduplication occurs.

Caller order is preserved exactly.

---

# Default Options

The module SHALL NOT impose rsync defaults.

Instead,

```python
default_options
```

is supplied by the caller.

This keeps policy separate from mechanics.

---

# Windows Compatibility Preset

The module SHALL expose

```python
WINDOWS_SAFE_RSYNC_OPTIONS
```

containing:

```text
-avz
--partial
--append-verify
--timeout=30
--contimeout=15
```

These options represent the recommended defaults for unreliable Windows/MSYS2 rsync
hosts.

They SHALL remain a recommendation only.

The preset is never applied automatically.

---

# Blocking IO

The module SHALL expose

```python
blocking_io: bool = False
```

When enabled,

```text
--blocking-io
```

is appended to the command.

It SHALL remain opt-in.

It SHALL NOT be included in

`WINDOWS_SAFE_RSYNC_OPTIONS`.

This separation exists because blocking I/O is a compatibility workaround rather than
normal transfer behavior.

---

# Command Construction

The command builder SHALL always produce

```python
list[str]
```

Never

```python
str
```

Example:

```text
[
    "rsync",
    "-avz",
    "--partial",
    "-e",
    "ssh -p 22",
    "user@host:/remote",
    "/local"
]
```

This command SHALL be passed directly to `CLITransact`.

---

# Success Handling

`RsyncTransact` does not compute success.

All success evaluation is delegated to `CLITransact`.

When supplied,

```python
success_marker
```

is forwarded unchanged.

---

# Model Parsing

The model variants SHALL delegate directly to

```text
CLITransact.run_*_with_model()
```

No rsync-specific parsing occurs inside this module.

The caller supplies the parser.

---

# Learned Behaviors

These behaviors were derived from production automation experience and are considered
part of the module contract.

## 1. Rsync is a transport protocol, not a workflow.

This module builds commands only.

It performs no retries.

It performs no orchestration.

---

## 2. Resume is preferred over restart.

Whenever retry policies are expected,

```text
--partial
```

and

```text
--append-verify
```

should be recommended.

---

## 3. SSH is transport.

SSH parameters influence only transport construction.

They never modify rsync semantics.

---

## 4. Local and remote addressing are deterministic.

Given identical inputs,

the generated argv SHALL always be identical.

No filesystem probing.

No environment inspection.

No implicit discovery.

---

## 5. Options are caller-owned.

The module never silently inserts archive flags, compression, deletion, or recursion.

Only documented transport options may be injected.

---

## 6. Command construction is pure.

The builder has no side effects.

It performs no validation beyond formatting.

---

## 7. Execution belongs elsewhere.

All timeout handling,

stdout normalization,

stderr normalization,

exception containment,

and semantic success evaluation

belong exclusively to `CLITransact`.

---

# Future Retry Integration

Retry behavior is intentionally **outside** this module.

Per the policy-ownership rule in
[transport_transaction_architecture.md](transport_transaction_architecture.md),
`RsyncTransact` MAY **accept or select** a `RetryPolicy` (an optional parameter, or a
documented recommended default) and route execution through it — but it MUST NOT
implement retry, backoff, or recovery logic itself.

Future retry engines MAY classify rsync return codes as transient.

The recommended transient set is

```text
10
12
30
35
-1
```

representing

- socket I/O
- interrupted protocol stream
- timeout
- daemon timeout
- CLI framework timeout

The following are considered permanent failures and SHOULD NOT be retried:

```text
2
4
23
24
```

Retry orchestration belongs to a separate policy layer.

---

# Compliance Requirements

A compliant `RsyncTransact` implementation MUST:

1. Never invoke subprocess APIs directly.
2. Delegate every execution path to `CLITransact`.
3. Return only `CLITransactResult` or `CLITransactResultModel`.
4. Construct deterministic argv lists.
5. Preserve caller option ordering.
6. Honor option precedence exactly.
7. Inject SSH transport only when requested.
8. Keep `--blocking-io` opt-in.
9. Expose `WINDOWS_SAFE_RSYNC_OPTIONS`.
10. Contain no retry or backoff implementation.
11. Contain no execution policy beyond rsync command construction.
12. Remain stateless.
