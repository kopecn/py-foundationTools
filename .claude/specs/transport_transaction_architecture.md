---
spec: TransportTransactionArchitecture
scope: project
status: proposed
applies_to: foundationCLIHelpers
---

# Transport Transaction Architecture

## Overview

`CLITransact` is the universal execution kernel for external command execution.

Transport-specific modules (SSH, rsync, Docker, Git, SCP, etc.) are thin transactional layers that construct commands, optionally apply execution policies, and delegate execution to `CLITransact`.

This architecture separates execution mechanics from transport semantics.

---

# Layered Architecture

```
Transport Transaction
        │
        ▼
Command Builder
        │
        ▼
Execution Policy
        │
        ▼
CLITransact
        │
        ▼
subprocess
```

Each layer owns one responsibility.

---

# Layer 1 — CLITransact

Status: Implemented

Responsible for:

- subprocess execution
- sync execution
- async execution
- timeout handling
- output normalization
- semantic success evaluation
- optional model parsing
- exception containment

Must never know:

- rsync
- ssh
- git
- docker
- retries
- deployment logic

CLITransact is intentionally transport-agnostic.

---

# Layer 2 — Command Builders

Status: Proposed

Command builders produce executable command vectors.

Examples:

```
RsyncCommandBuilder
SSHCommandBuilder
DockerCommandBuilder
GitCommandBuilder
```

Each exposes a pure function:

```python
build(...) -> list[str]
```

or

```python
build(...) -> str
```

Properties:

- deterministic
- stateless
- side-effect free

Command builders never execute commands.

---

# Layer 3 — Execution Policies

Status: Proposed

Execution policies decorate command execution.

Examples include:

- RetryPolicy
- BackoffPolicy
- SuccessPolicy
- TimeoutPolicy

Policies are composable and independent.

Example:

```
RetryPolicy
    ↓
CLITransact.run_sync(...)
```

A policy may invoke CLITransact multiple times.

CLITransact itself never retries.

---

# RetryPolicy

RetryPolicy owns:

- retry count
- transient error classification
- exponential backoff
- jitter
- retry termination

It never builds commands.

It never performs subprocess execution directly.

---

# BackoffPolicy

Defines retry timing.

Default algorithm:

```
delay = min(max_delay, base_delay * 2 ** attempt)
```

Optional full jitter:

```
delay = random(0, delay)
```

Backoff algorithms should be independently replaceable.

---

# SuccessPolicy

Defines semantic success beyond process exit status.

Examples:

- stdout contains marker
- stderr must be empty
- parser validation
- domain-specific validation

CLITransact implements the default policy:

```
return_code == 0

AND

success_marker is present
```

Future transports may compose richer validation without modifying CLITransact.

---

# Layer 4 — Transport Transactions

Status: Proposed

Transport transactions are the public user-facing APIs.

Examples:

```
SSHTransact
RsyncTransact
GitTransact
DockerTransact
```

Each transport transaction:

1. validates inputs
2. builds the command
3. selects policies
4. delegates execution

Transport transactions never invoke subprocess directly.

---

# RsyncTransact Responsibilities

RsyncTransact owns:

- rsync command construction
- SSH transport injection
- Windows compatibility options
- default option presets
- retry policy selection

It delegates execution to CLITransact.

---

# SSHTransact Responsibilities

SSHTransact owns:

- ssh command construction
- remote command formatting
- identity file handling
- port configuration

It delegates execution to CLITransact.

---

# Dependency Direction

Dependencies are strictly one-way.

```
CLITransact

↑

RetryPolicy

↑

RsyncTransact
SSHTransact
DockerTransact

↑

Application
```

Lower layers never depend on higher layers.

---

# Extension Model

Adding a new transport should require only:

1. a command builder
2. optional execution policies
3. a thin transaction wrapper

Example:

```
KubectlTransact

↓

KubectlCommandBuilder

↓

RetryPolicy

↓

CLITransact
```

No modification to CLITransact should be necessary.

---

# Design Invariants

A compliant transport transaction MUST:

1. never invoke subprocess directly
2. delegate execution exclusively to CLITransact
3. remain stateless
4. construct commands deterministically
5. own only transport-specific behavior
6. apply execution policies outside CLITransact
7. preserve CLITransact result semantics without modification

---

# Architectural Principle

Execution is infrastructure.

Policies are orchestration.

Builders are composition.

Transactions are transport semantics.

Each layer should remain independently testable, independently replaceable, and independently extensible.
