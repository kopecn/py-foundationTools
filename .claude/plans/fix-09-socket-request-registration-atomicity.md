---
plan: Fix09SocketRequestRegistrationAtomicity
scope: project
status: needs-approval
last_updated: 2026-09-04
semver: 1.0.0
author: Nicholas Bergantz
---

# Fix candidate 09 — socket request registration atomicity

Evidence: `TransactionRouter.request` registers a generated transaction ID before
calling `tx_id_injector`. If injection raises, control never reaches the cleanup block,
so `_pending` retains an orphan future. `SocketTransact.request` converts the exception
to a failure result and hides the corrupted router state from the caller.

Minimum fix: make frame preparation and pending registration one rollback-safe operation.
Registration must still happen before the first awaited send so a fast reply cannot race
ahead of correlation. Add a regression test proving an injector failure leaves no pending
ID and that the same generated ID can be used by a later request.

Do not add retries, reconnect behavior, protocol-specific IDs, or a compatibility path
for the leaked state. The explicit-`tx_id` API-mode question is separate from this defect.
