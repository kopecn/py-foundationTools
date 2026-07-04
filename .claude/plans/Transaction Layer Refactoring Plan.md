# Transaction Layer Refactoring Plan

## Goal

Unify the automation execution stack around a single layered transaction architecture.

Today there are effectively two independent concepts:

```
TransactionHandler
    ↑
device command lifecycle

CLITransact
    ↑
subprocess lifecycle

RsyncTransact
    ↑
rsync command construction
```

The first models long-lived protocol transactions.

The second models one-shot subprocess execution.

Although they solve different problems, they share the same architectural pattern:

- build work
- execute work
- normalize result
- evaluate success
- optionally transform output
- never leak implementation details

The proposal is **not** to merge them.

Instead, extract the common abstraction they already share.

---

# Architectural Layers

```
Application
      │
      ▼
Domain Transaction
(Device Commands, Rsync, SSH, etc.)
      │
      ▼
Execution Transaction
(CLITransact)
      │
      ▼
Execution Backend
(subprocess)
```

CLITransact becomes the generic execution kernel.

Higher layers become pure command builders and policy engines.

---

# Responsibility Split

## Layer 1 — Execution Engine

Responsible for:

- execute process
- sync / async
- timeout
- stdout/stderr normalization
- semantic success evaluation
- model parsing
- exception containment

Knows nothing about:

- rsync
- ssh
- retries
- network transports
- deployment

This is today's CLITransact.

---

## Layer 2 — Command Builders

Responsible for producing executable commands.

Examples:

```
SSHCommandBuilder
RsyncCommandBuilder
GitCommandBuilder
DockerCommandBuilder
```

These never execute.

They only return

```
list[str]
```

or

```
str
```

depending on required shell semantics.

---

## Layer 3 — Transaction Policies

Responsible for orchestration around execution.

Examples:

```
RetryPolicy
BackoffPolicy
TimeoutPolicy
ValidationPolicy
```

These decorate execution.

They never build commands.

They never invoke subprocess.

---

## Layer 4 — Domain Transactions

These become the public APIs.

Examples

```
SSHTransact
RsyncTransact
DockerTransact
GitTransact
```

Their responsibilities become intentionally tiny:

1. Build command
2. Select policy
3. Delegate to CLITransact

Nothing else.

---

# Why This Matters

Today RsyncTransact mixes three independent concerns.

```
command construction

+

retry policy

+

execution delegation
```

Those evolve independently.

Separating them allows:

- reusable retry engine
- reusable ssh command generation
- reusable command builders
- reusable execution kernel

---

# Proposed Package Layout

```
foundationCLIHelpers/

    cliTransact.py

    execution/
        cli_executor.py

    builders/
        rsync_builder.py
        ssh_builder.py

    policies/
        retry_policy.py
        backoff_policy.py
        success_policy.py

    transports/
        rsyncTransact.py
        sshTransact.py
```

The public API remains simple while the internal responsibilities become sharply separated.

---

# Relationship to automation_foundation_transactions

The two packages solve different layers.

```
automation_foundation_transactions
```

answers

> "How do I coordinate long-running work?"

whereas

```
foundationCLIHelpers
```

answers

> "How do I execute one unit of work?"

One should never depend on the other's internal implementation.

Instead:

```
TransactionHandler
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

or

```
TransactionHandler
        │
        ▼
SSHTransact
        │
        ▼
CLITransact
```

This produces clean layering with no circular dependencies.

---

# Design Philosophy

Each layer should own exactly one concern.

Execution should never know transport.

Transport should never know retry.

Retry should never know command construction.

Command builders should never execute.

Execution kernels should never orchestrate.

Keeping these boundaries strict allows new command families to be added with almost no duplicated code.
