---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Implement thread-safe transaction ID allocation, registration, discard, and atomic stage waits.
last_updated: 2026-09-12
semver: 0.0.1
author: Nicholas Bergantz
status: completed
---

# 05 — Transaction core registration and waits

Scope: [summary goal](00-overview.md#summary-goal) · [original ask](00-original-ask.md) · Contract: [pending transaction and core](../../../specs/threadedTransactionProtocol.md#pending-transaction)

## Deliverable

Create internal `PendingTransaction` and the state-management half of `TransactionCore`: ID sequences, epoch-bound registration, duplicate rejection, discard, and race-safe ACK/completion waits.

## Depends on

02 transaction values.

## Files

- Create `src/foundation_tools/socket_transaction/transaction_core.py`.
- Create `tests/test_transaction_core.py`.

## Design constraints

- Inject a `logging.Logger`; never call `getLogger` or instantiate a logger.
- Validate positive integer `first_tx_id` and `tx_id_step`, excluding booleans.
- Protect pending state and ID allocation with one lock; never hold it while `Event.wait` blocks.
- Duplicate registration raises without replacing or mutating the incumbent pending record.
- Wait timeouts accept `None` or finite non-negative numbers; zero is an immediate check.

## Timeout race recipe

```python
signaled = pending.ack_event.wait(timeout)
with self._lock:
    current = self._pending.get(tx_id)
    if current is None:
        return None
    if current.ack_status is unresolved:
        # This lock acquisition is the linearization point versus route().
        current.ack_status = AckStatus.TIMED_OUT
    return current.ack_status
```

The completion path uses the same pattern. Do not snapshot mutable pending fields outside the lock.

## TDD steps

1. Add failing validation and odd/even sequence tests.
2. Add concurrent allocation, duplicate rejection, and idempotent discard tests.
3. Add barrier-controlled arrival-versus-timeout tests proving exactly one side settles each stage.
4. Implement state and waits; routing remains for chunk 06.
5. Run `pytest tests/test_transaction_core.py -k "state or wait or timeout"` and `make fullCheck`.

## Acceptance criteria

- [x] Client sequence configuration yields `1, 3, 5`; server yields `2, 4, 6` under concurrent allocation without duplicates.
- [x] Duplicate registration preserves the original pending object's identity and events.
- [x] A timeout-racing settlement produces either success/failure or `TIMED_OUT`, never an overwritten hybrid.
- [x] No lock is held across an event wait.
- [x] `make fullCheck` passes.

## Out of scope

- Frame routing and callbacks.
- Socket epochs beyond storing the supplied epoch value.
- Public package exports.

## Ask ↔ result

- **Objective (`human_ask` + `goal`):** the top-level ask directed reducing the asyncio socket stack to threading/sockets via bite-sized tasks; this chunk's recorded goal was to implement thread-safe transaction ID allocation, registration, discard, and atomic stage waits. No conflict between `human_ask` and `goal`.
- **Live request:** `/execute-plan .claude/plans/25-threaded-socket-transaction`, explicitly authorizing execution of this chunk now.
- **Delivered:** `src/foundation_tools/socket_transaction/transaction_core.py` with internal `PendingTransaction` (mutable dataclass: `epoch`, `tx_id`, independent `ack_event`/`done_event` threading Events, `ack_status`/`completion_status` as `None`-while-unresolved, `acked`, `result`, `ack_error`, `completion_error`, arrival-ordered `events` list) and the state half of `TransactionCore(logger, *, first_tx_id=1, tx_id_step=1)`: `next_tx_id`, `register`, `discard`, `wait_ack`, `wait_completion`. Constructor validates positive-int `first_tx_id`/`tx_id_step` excluding booleans; wait timeouts validate to `None` or a finite non-negative number, zero is an immediate check; a single lock guards allocation/pending state and is never held across `Event.wait`; duplicate `register` raises `RuntimeError` without touching the incumbent; `discard` is idempotent; each wait re-acquires the lock immediately after its `Event.wait` returns as the linearization point, settling an unresolved stage to `TIMED_OUT` or returning an already-settled value unchanged. `route`, `fail_epoch`, the handler setters, and `finalize_outcome` are not implemented (chunk 06). No package exports were added.
- `tests/test_transaction_core.py` (57 tests): constructor validation (positive-int + boolean exclusion for both params, no-`getLogger`-call AST check), odd/even/default sequence generation plus a 16-thread/50-allocation-each concurrent `next_tx_id` stress test asserting zero duplicates against the exact expected id set, `register`/duplicate-rejection/identity-preservation (mutating the incumbent's own state, then a live-object comparison via `wait_ack`, is used to prove the RuntimeError path never replaced the pending record), `discard` idempotency and id-reuse after discard, timeout validation (rejects negative/inf/NaN/non-numeric, accepts `None`/`0`), unknown-id `None` returns, timeout settlement (single and repeated), barrier-controlled arrival-vs-timeout races for both ACK and completion stages (arrival-wins, timeout-wins-and-is-never-overwritten, and a 50-iteration contention stress loop asserting exactly one legal, idempotently-re-readable outcome), and a lock-freedom test proving unrelated `next_tx_id`/`register`/`discard` calls complete promptly while another thread is blocked inside `wait_ack`.
- `make fullCheck`: flake8 clean, strict mypy clean (66 `src` files + 42 `tests` files), pytest 784 passed (57 new).
- **Gap:** none identified against this chunk's scope. The barrier/contention-based race tests reach into `TransactionCore._lock`/`._pending` directly to simulate a chunk-06-style routing settlement (`route()` does not exist yet) — a deliberate white-box technique, not a scope violation, since it only exercises the state layer this chunk owns.
