---
plan: Fix09SocketRequestRegistrationAtomicity
scope: project
status: completed
last_updated: 2026-09-05
semver: 1.0.1
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

## Ask ↔ result

- **Objective (from "Minimum fix"):** make frame preparation and pending registration
  one rollback-safe operation in `TransactionRouter.request`; registration stays before
  the first awaited send so a fast reply cannot race ahead of correlation; on any failure
  before the reply-await, roll the registration back completely. Add a regression test
  proving an injector failure leaves no pending ID and that the generated ID stays reusable.
- **Authorizing request:** `/execute-plan fix-09 and onward`; user explicitly approved
  fix-09 for execution this session on 2026-09-05 ("I approve 09, 10, ...").
- **Delivered:**
  - `src/foundation_tools/socket_transaction/transaction_router.py` — `request` now
    generates/decides the tx_id, then `self._register(...)`, then a single
    `try: frame = inject(...) ; await transport.send(encode(frame))` guarded by
    `except BaseException: self._pending.pop(resolved_tx_id, None); raise`. The
    contract order (generate → register → inject → encode → send) is unchanged; the
    injector call moved inside the rollback guard that previously covered only
    `encode` + `send`, and the guard widened from `except Exception` to
    `except BaseException` so a cancellation at the send await also rolls back
    (matching the sibling reply-await guard). `_register`'s duplicate-in-flight
    `RuntimeError` stays outside the guard so it never pops another request's entry.
  - `tests/test_transaction_router.py` — new `TestRequestRegistrationAtomicity`
    (+ `_FlakyInjector` helper): `test_injector_failure_rolls_back_registration`
    asserts (a) `router._pending == {}` and nothing written to the transport after
    an injector raise, and (b) the fixed generated id `"regen-1"` is reused by a
    later successful request (a leaked entry would raise "already in-flight").
- **Gate:** `make uv-fullCheck` passes — ruff clean, mypy strict clean (62 + 36 files),
  545 pytest passed (baseline 544 + 1 new test). Confirmed the new test fails without
  the source change (`_pending` retains `{'regen-1': <Future pending>}`).
- **Deviation:** widened the pre-send guard from `except Exception` to
  `except BaseException`. The chunk names only "if injection raises" (a plain
  `Exception`); the wider catch is justified by "roll back ... on any failure before
  that point" and consistency with the existing reply-await guard. No behavior change
  for the `Exception` path.
- **Gap:** none. Explicit-`tx_id` API-mode question and the broader socket lifecycle
  (fix-12) untouched.
