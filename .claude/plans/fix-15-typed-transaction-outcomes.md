---
plan: Fix15TypedTransactionOutcomes
scope: project
status: needs-approval
last_updated: 2026-09-05
semver: 1.1.0
author: Nicholas Bergantz
---

# Fix candidate 15 — truthful typed transaction outcomes

Evidence: CLI and socket typed transactions can return `success=True`, `model=None`, and
a parsing error. RetryPolicy consequently treats an unusable typed response as terminal
success. Mutable result dataclasses also permit contradictory states unrelated to any real
execution path.

Minimum fix: define separate execution and decoding outcomes, preferably with immutable,
discriminated result types that make invalid combinations unrepresentable. Align CLI,
socket, SSH/rsync forwarding, retry termination, documentation, and tests with that model.

This is an API-design task. Do not merely flip the existing `success` boolean, erase raw
transport output, retry permanent decode failures indiscriminately, or retain contradictory
states as legacy support without explicit approval.

## Session note — 2026-09-05 (not executed; own execution plan)

Status held at `needs-approval`. No implementation this session; this becomes its own
scoped execution plan.

Confirmed direction (user, 2026-09-05):

- Typed transaction outcomes must represent **transaction truth, not transport/execution
  truth**. A caller of a typed transaction does not care whether the engine, subprocess,
  socket, SSH connection, codec, or forwarding mechanism each succeeded in isolation —
  those are implementation details. The caller cares whether the requested transaction
  produced the requested result.
- A **successful** typed transaction contains a valid model; a **failed** typed
  transaction contains no model.
- Execution / transport / decoding failures may remain available as diagnostics but must
  not redefine the public meaning of transaction success.
- `success=True, model=None` (and other contradictory states) must be **unrepresentable**.
- Apply consistently across CLI, socket, SSH/rsync forwarding, retry termination,
  documentation, and tests.
- Retry operates on **transaction outcomes** and classifies failures by whether retrying
  the transaction can plausibly change its outcome; permanent response/decode failures
  are not retried indiscriminately.
- Not solved by flipping the `success` boolean, discarding raw transport information, or
  preserving contradictory result states for compatibility without explicit approval.

Coordinate the outcome boundary with `fix-16`; approval of one is not approval of both.
