---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Let a failed ACK terminate an independently pending completion stage even when the ACK wait already timed out.
last_updated: 2026-09-13
semver: 0.1.0
author: Nicholas Bergantz
status: completed
---

# 23 - Route failed ACK after ACK timeout

Scope: [summary goal](00-overview.md#summary-goal) · [original ask](../../archive/plans/25-threaded-socket-transaction/00-original-ask.md) · Contract: [failed ACK](../25-threaded-socket-transaction.md#28-ack-routing), [independent waits](../25-threaded-socket-transaction.md#38-ack-waiting), and [protocol settlement](../../specs/threadedTransactionProtocol.md#routing)

## Origin

PA25-07: after ACK timeout, `_route_ack` drops a failed ACK as late before settling unresolved completion, so a subsequent result wait times out instead of observing transaction failure.

## Deliverable

Preserve first-settlement ACK status while allowing a later failed ACK to settle an independently unresolved completion stage as `ERROR` and wake its waiter.

## Depends on

None.

## Files

- Edit `src/foundation_tools/socket_transaction/transaction_core.py`.
- Edit `tests/test_transaction_core.py`.
- Edit `tests/test_transacting_socket_handler.py`.

## Design constraints

- Never overwrite `AckStatus.TIMED_OUT`; ACK and completion remain independent stages.
- A failed ACK may set `CompletionStatus.ERROR` only while completion is unresolved.
- A late successful ACK after ACK timeout remains non-terminal for completion.
- A failed ACK must not overwrite an existing result, protocol error, completion timeout, or connection-closed status.
- Preserve exact failed-ACK diagnostic construction and signal `done_event` when completion settles.

## Routing recipe

```python
if pending.ack_status is AckStatus.TIMED_OUT:
    if frame.code != 0 and pending.completion_status is None:
        settle_completion_from_failed_ack(pending, frame)
    return
```

Keep all state mutation under the transaction lock and preserve late-frame logging.

## TDD steps

1. Add a failing core test for ACK timeout followed by failed ACK and completion wait.
2. Add losing-race cases for result/error/completion-timeout before the late failed ACK.
3. Add a facade test with sequential ACK and result waits.
4. Implement the independent completion settlement and run focused tests plus the gate.

## Acceptance criteria

- [x] ACK timeout remains `TIMED_OUT` after a later failed ACK.
- [x] An unresolved requested completion becomes `ERROR` with the failed-ACK diagnostic and wakes immediately.
- [x] A late successful ACK does not complete the transaction.
- [x] No already-settled completion is overwritten.
- [x] `make fullCheck` passes.

## Out of scope

- Changing timeout durations or the two-wait ordering.
- Redesigning `TransactionOutcome` fields or diagnostics.
- Reusable transaction IDs or multiple owner waiters per transaction.

## Ask ↔ result

**Objective (human_ask/goal):** `human_ask` is the planning-phase ask that produced this
chunk (decompose the top-level socket spec into bite-sized threading-only tasks). The
chunk's own `goal` narrows that to: let a failed ACK terminate an independently pending
completion stage even when the ACK wait already timed out. Both agree on the objective;
no conflict.

**Live authorization:** the user's execution request (`/execute-plan 17 ... 25 these were
from a post audit`) explicitly authorized executing chunks 17-25 now, including this one.

**Delivered:** `TransactionCore._route_ack` in
`src/foundation_tools/socket_transaction/transaction_core.py` no longer unconditionally
drops a late ACK once `pending.ack_status` is already settled. It now branches: a first ACK
settles as before; a failed ACK arriving after `AckStatus.TIMED_OUT` calls a new
`_settle_completion_from_failed_ack` helper (factored out of the original inline logic,
diagnostic text unchanged via a new `_failed_ack_error_text` static helper) that sets
`CompletionStatus.ERROR` and signals `done_event` only while completion is still
unresolved; every other late/duplicate ACK (including a late successful one after timeout)
falls through to the original debug-log-and-drop path, so `AckStatus.TIMED_OUT` is never
overwritten and `acked`/`completion_status` stay untouched for that case.

Added tests, all confirmed failing against the pre-fix code before implementing:
- `tests/test_transaction_core.py::TestLateFailedAckAfterAckTimeout` (7 cases: settles
  unresolved completion; never overwrites `TIMED_OUT`; late successful ACK stays
  non-terminal; and four losing-race guards — result, protocol error, completion timeout,
  and connection-closed already settled first).
- `tests/test_transaction_core.py::TestLateFailedAckWakesBlockedCompletionWait` (barrier-
  controlled: a completion wait blocked on `done_event` wakes immediately when the late
  failed ACK arrives).
- `tests/test_transacting_socket_handler.py::TestSequentialAckAndResultWaits` (facade-level:
  one `send_transaction(wait_ack=True, wait_result=True)` call, with the failed ACK held
  back by a `_AckSettledCore` test double until strictly after the internal `wait_ack` call
  has settled to `TIMED_OUT`, still resolves the outcome's `completion_status` to `ERROR`
  instead of a second `TIMED_OUT`).

`make fullCheck` passes: 919 tests, including 9 new test cases added by this chunk.

**Gap:** none identified against this chunk's scope. Touched only the three files listed
above; timeout durations, wait ordering, `TransactionOutcome` fields, and ID-reuse policy
are unchanged.
