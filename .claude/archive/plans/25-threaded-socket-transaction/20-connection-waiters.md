---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Make connection-state waiting level-triggered and safe for multiple concurrent callers.
last_updated: 2026-09-13
semver: 0.1.0
author: Nicholas Bergantz
status: completed
---

# 20 - Broadcast connection-state changes

Scope: [summary goal](00-corrective-overview.md#summary-goal) · [original ask](00-original-ask.md) · Contract: [server connection waiting](../../../specs/threadedSocketTransport.md#single-client-server)

## Origin

PA25-04: the post-audit controlled two indefinite waiters so one cleared the shared Event before the second entered `wait()`, leaving the second blocked while `is_connected` was true.

## Deliverable

Replace the clearable shared-edge wait with state-locked broadcast notification so every waiter rechecks the current connection state without losing publication or detachment changes.

## Depends on

None.

## Files

- Edit `src/foundation_tools/socket_transaction/socket_handler_server.py`.
- Edit `tests/test_socket_handler_server.py`.

## Design constraints

- Use a `threading.Condition` associated with connection state, or an equivalent generation-based broadcast primitive; one waiter must never consume another waiter's wake.
- Evaluate connected state and enter the wait atomically under the condition's lock.
- Notify all waiters on matching-epoch client publication and detachment/rollback.
- Preserve timeout validation, immediate zero-timeout checks, and deadline-based spurious-wake handling.
- Do not hold the condition lock while joining, invoking callbacks, accepting, or performing socket I/O.

## Wait recipe

```python
with connection_condition:
    while active_socket_is_none:
        if not connection_condition.wait(remaining_to_deadline):
            return False
    return True
```

Publication and matching-epoch teardown call `notify_all()` while holding the same state lock.

## TDD steps

1. Add a deterministic two-waiter regression that fails against Event clear semantics.
2. Add a disconnect/reconnect wake test and preserve timeout tests.
3. Implement condition-based level-triggered waiting.
4. Run `pytest tests/test_socket_handler_server.py` and `make fullCheck`.

## Acceptance criteria

- [x] Two indefinite waiters both return `True` for one active connection.
- [x] No waiter remains blocked while a client epoch is active.
- [x] Detach/reconnect wakes waiters without allowing a stale epoch to report connected.
- [x] Zero, finite, and `None` timeout behavior remains correct.
- [x] `make fullCheck` passes.

## Out of scope

- Queuing connection history or returning peer metadata from the wait.
- Multiple active clients.
- Transaction completion events.

## Ask ↔ result

**Objective (`human_ask` + `goal`):** the human designated the top-level socket spec as the
source to decompose into threading/`socket`-only chunks; this chunk's goal, set by the post-audit
(PA25-04), is to make connection-state waiting level-triggered and safe for multiple concurrent
callers. The post-audit deterministically reproduced two indefinite waiters where one cleared the
shared `Event` before the second entered `wait()`, leaving the second blocked while `is_connected`
was true.

**Live authorization:** the user's `/execute-plan 17 ... 25 these were from a post audit` command
authorized executing this already-planned corrective chunk now. Executed directly by the
supervising model because the Sonnet execution agent hit a session rate limit mid-chunk (before
making any change); the clean, no-partial-changes state was verified first.

**Delivered:** `SocketHandlerServer.wait_for_connection` no longer uses a single clearable
`threading.Event`. It now uses the chunk's explicitly-permitted **generation-based broadcast**: a
`threading.Condition` plus a monotonic `_connection_generation`. Every matching-epoch publication
(`_publish_client_locked`), detachment (`_detach`), and rollback (`_rollback_unstarted_worker`)
now calls `_broadcast_connection_change()`, which bumps the generation and `notify_all()`s under
`_connection_condition`. Each waiter snapshots the generation under the condition lock, evaluates
`is_connected` *outside* that lock, and blocks only if the generation has not advanced since the
snapshot — so a state change that races the check advances the generation and is observed on the
next loop rather than lost, and `notify_all` wakes every waiter (no single edge one peer can
consume). The condition lock is never nested inside `_state_lock` and never held across
`is_connected`, a join, a callback, or socket I/O, satisfying the no-I/O-under-lock constraint.
Timeout validation, the immediate zero-timeout check, and deadline-based re-checking are preserved.

Two deterministic, sleep-free regressions were added to `tests/test_socket_handler_server.py`
(class `TestConnectionWaitBroadcast`): the two-waiter PA25-04 reproduction (verified to fail
against the pre-fix code with `waiter-B` blocking past the bounded join, and to pass after the fix,
re-run 5× with no flakiness) and a detach-then-reconnect wake test that also asserts a stale epoch
never reports connected. `make fullCheck` passes: flake8 clean, strict mypy clean (67 source + 43
test files), pytest **903 passed**.

**Gap:** none against this chunk's deliverable and acceptance criteria. Note on design constraint
"evaluate connected state and enter the wait atomically under the condition's lock": the first
listed design constraint explicitly offers "an equivalent generation-based broadcast primitive" as
an alternative to a bare `Condition` predicate loop. The generation snapshot + no-advance guard is
that alternative; it provides the same no-lost-wakeup guarantee while keeping `is_connected`
(which takes `_state_lock`) out of the condition lock, which is what makes the deterministic
two-waiter regression possible without a lock-order inversion.
