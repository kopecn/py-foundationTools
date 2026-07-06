---
spec: SSHTransact
scope: project
status: implemented
applies_to: src/foundation_tools/cli_transaction/sshTransact.py
last_updated: 2026-07-05
semver: 0.3.0
author: Nicholas Bergantz
---

# SSH Transaction Manager Specification

## Overview

`SSHTransact` is a stateless transport wrapper that executes commands on a remote
host via OpenSSH.

It is responsible only for:

- constructing SSH command lines
- representing remote commands correctly
- configuring SSH transport parameters
- delegating execution to `CLITransact`

It is **not** responsible for:

- subprocess execution
- timeout implementation
- retries
- output normalization
- success evaluation
- model parsing
- exception handling

Those responsibilities belong exclusively to `CLITransact`.

---

# System Role

```
Application
      │
      ▼
SSHTransact
      │
      ▼
CLITransact
      │
      ▼
subprocess
```

SSHTransact is a transport layer.

CLITransact remains the execution kernel.

---

# Design Philosophy

SSHTransact is intentionally thin.

It exists to provide:

- a strongly typed interface
- deterministic SSH command construction
- reusable transport semantics

It should contain almost no execution logic.

---

# Public API

Exactly four stateless class methods.

| Method                    | Returns                   |
| ------------------------- | ------------------------- |
| run_sync(...)             | CLITransactResult         |
| run_async(...)            | CLITransactResult         |
| run_sync_with_model(...)  | CLITransactResultModel[T] |
| run_async_with_model(...) | CLITransactResultModel[T] |

Each method:

1. builds the SSH command
2. delegates directly to CLITransact (optionally through a `retry_policy`)
3. returns the CLITransact result unchanged

No additional result processing occurs.

Every method additionally accepts an optional, keyword-only
`retry_policy: RetryPolicy | None = None`. When supplied, the built command is
executed through `retry_policy.run_sync`/`run_async` instead of calling
`CLITransact` directly — see [Zero execution policy](#zero-execution-policy).

---

# Command Construction

SSHTransact produces argv-style commands suitable for direct execution.

Base command:

```
ssh
```

The transport is always constructed as:

```
ssh
    [-p <port>]
    [-i <identity_file>]
    <target>
    <remote command>
```

where

```
target =
    user@host
```

when a user is supplied, otherwise

```
host
```

---

# Remote Command Contract

The remote command follows the same dual-mode contract as CLITransact.

## String

```
command: str
```

Produces

```
ssh host "command"
```

The string becomes a single remote-shell argument.

This allows:

- pipes
- redirects
- shell operators
- variable expansion
- compound commands

Example:

```python
"cd /tmp && ls *.txt"
```

---

## List

```
command: list[str]
```

Produces

```
ssh host arg1 arg2 arg3
```

Each element becomes an independent argv component.

This avoids shell parsing.

Example:

```python
["python3", "--version"]
```

---

# SSH Parameter Rules

## Host

Required.

May be:

- hostname
- IPv4
- IPv6
- SSH alias from ~/.ssh/config

---

## User

Optional.

If omitted:

SSH resolves the username through:

- ~/.ssh/config
- system defaults

SSHTransact performs no resolution itself.

---

## Port

Optional (`port: int | None = None`).

`-p <port>` is emitted **only when a port is supplied**. No synthesized default is
ever emitted: a command-line `-p` overrides any `Port` declared for the host in
`~/.ssh/config`, so forcing `-p 22` would silently break SSH aliases whose config
sets a non-default port. When omitted, ssh resolves the port through its normal
config/default chain — exactly like the user rule.

Determinism is preserved: identical inputs always generate identical argv.

---

## Identity File

Added only when supplied.

```
-i /path/to/key
```

No validation occurs.

The path is passed directly to ssh.

---

# Delegation Contract

All execution delegates directly to CLITransact.

Example:

```
command = _build_ssh_command(...)

return CLITransact.run_sync(
    command,
    timeout=timeout,
    success_marker=success_marker,
)
```

SSHTransact performs no intermediate processing.

---

# Success Semantics

Success is determined entirely by CLITransact.

SSHTransact never modifies:

- return_code
- stdout
- stderr
- success

The optional success_marker is forwarded unchanged.

---

# Model Parsing

Model parsing is delegated entirely to CLITransact.

SSHTransact simply forwards:

- serializer
- timeout
- success_marker

No parser logic exists inside SSHTransact.

The canonical parser is `DataModelHelper.from_wire` on a schema-generated model —
see the **Wire Serialization Bridge** section of
[transport_transaction_architecture.md](transport_transaction_architecture.md).

---

# Error Handling

SSHTransact contains no exception handling.

Construction errors should be limited to programmer mistakes.

Execution failures are contained by CLITransact.

---

# Learned Behaviors

## Transport-only abstraction

SSHTransact exists solely to represent SSH transport semantics.

Execution belongs elsewhere.

---

## Deterministic command construction

The same inputs always generate the same argv sequence.

No environment inspection occurs.

---

## Explicit transport configuration

The generated SSH command is fully explicit.

Ports and identity files are emitted only when supplied.

No hidden defaults are injected — a synthesized `-p 22` would itself be a hidden
default, overriding `~/.ssh/config` port settings for aliases.

---

## Remote shell semantics are caller-selected

The remote command type determines execution behavior.

```
str
```

selects remote shell interpretation.

```
list[str]
```

selects argv semantics.

This mirrors CLITransact's own command contract.

---

## Zero execution policy

SSH itself has no retry semantics.

No retry, backoff, or recovery logic belongs in SSHTransact.

Higher layers may compose those behaviors externally. Per the policy-ownership rule
in [transport_transaction_architecture.md](transport_transaction_architecture.md),
SSHTransact MAY accept an optional policy parameter and pass execution through it,
but MUST NOT implement retry logic itself.

---

# Compliance Requirements

A compliant SSHTransact MUST:

1. expose exactly four stateless class methods
2. construct deterministic SSH commands
3. include `-p <port>` only when a port is supplied (never a synthesized default)
4. include `-i <identity_file>` only when supplied
5. construct the target as `user@host` when a user is provided
6. preserve the command type contract (`str` vs `list[str]`)
7. delegate execution exclusively to CLITransact
8. perform no retries
9. perform no parsing
10. modify no CLITransact results
