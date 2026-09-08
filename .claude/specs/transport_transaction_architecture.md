---
spec: TransportTransactionArchitecture
scope: project
status: accepted
applies_to: src/foundation_tools/cli_transaction/, src/foundation_tools/builders/, src/foundation_tools/policies/, src/foundation_tools/socket_transaction/
last_updated: 2026-08-15
semver: 0.4.2
author: Nicholas Bergantz
---

# Transport Transaction Architecture

## Overview

This is the umbrella spec for the transaction/transport stack. It covers **two
transport families** that share one design ethos (stateless surfaces, result objects,
strict layer ownership) and one serialization bridge (`DataModelHelper`):

1. **Process transactions** — one-shot external command execution.
   `CLITransact` is the execution kernel; SSH, rsync, Docker, Git, etc. are thin
   transactional layers above it.
2. **Stream transports** — long-lived byte-stream connections (TCP sockets, serial,
   EtherCAT) built on the `foundation_abc.PeripheralByteTransport` ABC, with framing
   codecs and a transaction router layered on top (see
   [socketTransact.md](socketTransact.md)).

Both families live under `src/foundation_tools/` and meet the data-model layer through
`DataModelHelper` wire serialization (see [Wire Serialization Bridge](#wire-serialization-bridge)).

This architecture separates execution mechanics from transport semantics.

---

# System Map

```
                        Application
                             │
        ┌────────────────────┴────────────────────┐
        ▼                                         ▼
  Process transactions                     Stream transports
  (one-shot commands)                      (long-lived connections)
        │                                         │
  SSHTransact / RsyncTransact / …           SocketTransact
        │                                         │
  Command Builders + Execution Policies     Tx Router + Framing Codecs
        │                                         │
     CLITransact                           SocketByteTransport
        │                                  (PeripheralByteTransport ABC)
        ▼                                         ▼
    subprocess                              asyncio streams
        └────────────────────┬────────────────────┘
                             ▼
              DataModelHelper (to_wire / from_wire)
              shared serialization bridge
```

---

# Package Layout

All modules live under the `foundation_tools` package:

```
src/foundation_tools/
    cli_transaction/
        cliTransact.py          # execution kernel (implemented)
        sshTransact.py          # implemented
        rsyncTransact.py        # implemented
    builders/
        ssh_builder.py          # implemented
        rsync_builder.py        # implemented
    policies/
        retry_policy.py         # implemented
        backoff_policy.py       # implemented
    socket_transaction/
        socket_byte_transport.py    # implemented
        framing_codecs.py           # implemented
        transaction_router.py       # implemented
        socketTransact.py           # implemented — client facade
        socketTransactServer.py     # implemented — server facade
```

`cliTransact.py` **is** the execution kernel — there is no separate
`cli_executor.py`; earlier drafts that listed both were describing one module.

---

# Public Surface (usability north star)

End users interact with exactly two kinds of objects:

1. **Layer-4 transactions** — `CLITransact`, `SSHTransact`, `RsyncTransact`,
   `SocketTransact`. Each is a one-call, stateless surface mirroring the existing
   four-classmethod pattern (`run_sync` / `run_async` / `run_sync_with_model` /
   `run_async_with_model`, or the socket equivalent).
2. **Result objects** — `CLITransactResult`, `CLITransactResultModel[T]`,
   `SocketTransactResult`. Transaction surfaces return results; they never raise.

Builders, policies, and codecs are **internal-but-importable**: available for
composition by advanced users, never required for the common path. Adding a
transport must not add required end-user I/O beyond one method call.

---

# Layered Architecture (process-transaction family)

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

Status: Implemented (`src/foundation_tools/cli_transaction/cliTransact.py`,
contract in [cliTransact.md](cliTransact.md))

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

Status: Implemented (`src/foundation_tools/builders/`) — `build_ssh_command`
(`ssh_builder.py`) and `build_rsync_command` (`rsync_builder.py`). Docker/Git
builders below are illustrative examples of the pattern, not implemented.

Command builders produce executable command vectors.

Examples:

```
build_ssh_command      (implemented)
build_rsync_command    (implemented)
DockerCommandBuilder    (hypothetical — illustrates the extension pattern)
GitCommandBuilder       (hypothetical — illustrates the extension pattern)
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

Status: Implemented (`src/foundation_tools/policies/`) — `RetryPolicy` and
`BackoffPolicy`. `SuccessPolicy`/`TimeoutPolicy` below are illustrative examples
of the pattern, not implemented as separate classes: success evaluation and
per-attempt timeout are already owned by `CLITransact` itself (see
[cliTransact.md](cliTransact.md)), so no dedicated policy class exists for them.

Execution policies decorate command execution.

Examples include:

- RetryPolicy (implemented)
- BackoffPolicy (implemented)
- SuccessPolicy (hypothetical — `CLITransact` already owns success evaluation)
- TimeoutPolicy (hypothetical — `CLITransact` already owns per-attempt timeout)

Policies are composable and independent.

Example:

```
RetryPolicy
    ↓
CLITransact.run_sync(...)
```

A policy may invoke CLITransact multiple times.

CLITransact itself never retries.

## Policy ownership (canonical rule)

Policies are a **separate layer**. A transport transaction MAY *accept or select* a
policy — an optional parameter, or a documented recommended default — but MUST NOT
*implement* retry, backoff, or recovery logic itself. This wording is canonical;
[cliTransact.md](cliTransact.md), [sshTransact.md](sshTransact.md), and
[rsyncTransact.md](rsyncTransact.md) defer to it.

## Policy composition (canonical rules)

- **Timeout is per-attempt.** The `timeout` a caller passes governs each individual
  execution attempt; a retry policy introduces no overall deadline. Worst-case wall
  time ≈ `attempts × timeout` plus the sum of backoff delays. Callers needing a hard
  total deadline enforce it outside the policy.
- **Policies wrap the whole call.** For the `run_*_with_model` variants the policy
  wraps the full callable (execution + parse), not the bare execution. Retry
  classification reads only `return_code`; a parser failure never changes `success`
  and therefore never triggers a retry. Since success terminates retries, parsing
  runs at most once — on the terminal attempt.

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

Status: Implemented (`SSHTransact`, `RsyncTransact`) — `GitTransact`/`DockerTransact`
below are illustrative examples of the extension pattern, not implemented.

Transport transactions are the public user-facing APIs.

Examples:

```
SSHTransact       (implemented)
RsyncTransact     (implemented)
GitTransact       (hypothetical — illustrates the extension pattern)
DockerTransact    (hypothetical — illustrates the extension pattern)
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
- retry policy **selection** (never implementation — see
  [Policy ownership](#policy-ownership-canonical-rule))

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

# Stream-Transport Family (socket)

Status: Implemented — full contract in [socketTransact.md](socketTransact.md).

The socket family is the long-lived-connection counterpart to the process family.
It is **asyncio-native** and layers as:

```
SocketTransact              # Layer 4 — public facade, result objects
        │
Transaction Router          # tx_id correlation via asyncio futures
        │
Framing Codecs              # delimiter / length-prefixed framing,
        │                   # DataModelHelper to_wire / from_wire
SocketByteTransport         # implements foundation_abc.PeripheralByteTransport
        │
asyncio streams
```

Parallels with the process family are deliberate:

| process family | stream family |
| --- | --- |
| CLITransact (kernel) | SocketByteTransport (raw bytes) |
| Command Builders | Framing Codecs |
| Execution Policies | Transaction Router policies (timeout, correlation) |
| SSHTransact / RsyncTransact | SocketTransact |
| `CLITransactResult` | `SocketTransactResult` |

The raw transport keeps the ABC's raising semantics (`ConnectionError`,
`TimeoutError`); the **transaction surface** (`SocketTransact`) converts failures to
result objects, matching the process family's containment ethos.

The family covers both roles: `SocketTransact` (client) and `SocketTransactServer`
(server — accepts connections, services plural inbound requests concurrently, and
replies tagged with each request's tx_id). The layers beneath the facades (codecs,
correlation pair) are shared between roles.

---

# Wire Serialization Bridge

`DataModelHelper` is the single serialization contract joining both families to the
data-model layer:

- **Process family:** `DataModelHelper.from_wire` (or `from_bytes` / a
  `from_dict`-based parser) is the canonical `output_parser` for the
  `run_*_with_model` methods. Models parsed from CLI output should be
  schema-generated `DataModelHelper` subclasses, not ad-hoc classes.
- **Stream family:** framing codecs encode outbound payloads with
  `DataModelHelper.to_wire` and decode inbound frames with
  `DataModelHelper.from_wire` (via the `wire_encode` / `wire_decode` ClassVars).

No transport module defines its own serialization format; they compose the bridge.

The bridge's invocation half is the `wire_invoke` ClassVar (see
[dataModelHelper.md](dataModelHelper.md)): the class-level constant naming the
request that produces a model's wire input, independent of `wire_encode`/
`wire_decode`. `CLITransact.run_*_with_model` accepts a bare `DataModelHelper`
subclass and resolves `wire_invoke` + `from_wire` for it (see
[cliTransact.md](cliTransact.md)) — today only for `str`/`list[str]` requests.
Should `SSHTransact`/`SocketTransact` grow the same model-based call form, the
same asymmetry holds: `wire_invoke` is the request, `from_wire` parses the
result, and an arm a given transport doesn't understand (e.g.
`type[DataModelHelper]` for a transport that isn't request/response-over-model)
raises rather than inventing a meaning for it — this is a forward-looking note,
not an implemented capability of those transports.

---

# Dependency Direction

Dependencies are strictly one-way.

```
CLITransact / SocketByteTransport

↑

Policies / Codecs / Router

↑

RsyncTransact
SSHTransact
SocketTransact

↑

Application
```

Lower layers never depend on higher layers.

---

# Extension Model

Adding a new transport should require only:

1. a command builder (process family) or codec (stream family)
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
2. delegate execution exclusively to CLITransact (process family) or the
   socket stack (stream family)
3. remain stateless
4. construct commands deterministically
5. own only transport-specific behavior
6. apply execution policies outside the execution kernel — selection allowed,
   implementation forbidden
7. preserve kernel result semantics without modification
8. expose no required end-user surface beyond the one-call transaction API
9. use `DataModelHelper` wire serialization for all model encode/decode

---

# Architectural Principle

Execution is infrastructure.

Policies are orchestration.

Builders and codecs are composition.

Transactions are transport semantics.

Each layer should remain independently testable, independently replaceable, and
independently extensible.
