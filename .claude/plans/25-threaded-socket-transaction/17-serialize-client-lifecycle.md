---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Serialize client connect and disconnect lifecycle operations so concurrent callers cannot orphan a socket or receive worker.
last_updated: 2026-09-13
semver: 0.1.0
author: Nicholas Bergantz
status: completed
---

# 17 - Serialize client connection lifecycle

Scope: [summary goal](00-overview.md#summary-goal) · [original ask](../../archive/plans/25-threaded-socket-transaction/00-original-ask.md) · Contract: [socket concurrency](../../specs/threadedSocketTransaction.md#concurrency-model) and [client lifecycle](../../specs/threadedSocketTransport.md#client)

## Origin

PA25-01: the post-audit deterministically reproduced two concurrent successful `connect()` calls publishing two receive workers, after which `disconnect()` closed only one socket.

## Deliverable

Make `SocketHandlerClient.connect()` and public `disconnect()` one serialized lifecycle operation while preserving timeout validation, incumbent replacement, and original exception behavior.

## Depends on

None.

## Files

- Edit `src/foundation_tools/socket_transaction/socket_handler_client.py`.
- Edit `tests/test_socket_handler_client.py`.

## Design constraints

- Add one client-lifecycle lock; do not reuse the state or send lock across blocking `connect()`.
- Preserve the constructor signature and validate timeout before waiting for or changing an incumbent connection.
- Hold lifecycle ownership across incumbent teardown, candidate connect, blocking-mode restoration, and attachment.
- Public `disconnect()` must participate in the same serialization; internal use must avoid recursive acquisition unless the chosen lock is intentionally reentrant.
- Every losing or failed candidate closes exactly once and no receive worker survives without an owned socket.

## Race recipe

```python
both_connecting = threading.Barrier(3)

# Gate two candidates after both calls have passed timeout validation.
first.start()
second.start()
both_connecting.wait(TEST_TIMEOUT)
# Release and assert one incumbent is cleanly replaced, not overwritten.
```

Use fake candidates with independently observable close events and bounded receive workers. Assert worker/socket ownership after both calls complete and again after final `disconnect()`.

## TDD steps

1. Add a failing concurrent-connect regression that reproduces PA25-01 without sleeps.
2. Add a connect-versus-disconnect interleaving test.
3. Implement lifecycle serialization without changing serial connect behavior.
4. Run `pytest tests/test_socket_handler_client.py` and `make fullCheck`.

## Acceptance criteria

- [x] Two concurrent successful connects leave exactly one active socket and at most one live receive worker.
- [x] Final `disconnect()` closes every candidate that was ever attached and leaves no client receive worker alive.
- [x] Invalid timeout still leaves an incumbent untouched.
- [x] Connect failure still propagates the original `OSError` and closes its candidate.
- [x] `make fullCheck` passes.

## Out of scope

- Automatic reconnect, cancellation, TLS, UDP, or IPv6.
- Server listener synchronization.
- Transaction facade behavior beyond inherited delegation.

## Ask ↔ result

**Objective (`human_ask` + `goal`):** the human designated the top-level socket spec as the
source to decompose into threading/`socket`-only chunks; this chunk's goal, set by the post-audit
(PA25-01), is to serialize `SocketHandlerClient.connect()`/`disconnect()` into one lifecycle
operation so concurrent callers cannot orphan a socket or receive worker — the post-audit had
deterministically reproduced two concurrent successful `connect()` calls publishing two receive
workers, after which `disconnect()` closed only one socket.

**Live authorization:** the user's `/execute-plan 17 ... 25 these were from a post audit` command
authorized executing this already-planned corrective chunk now.

**Delivered:** `SocketHandlerClient` (`src/foundation_tools/socket_transaction/socket_handler_client.py`)
gained one non-reentrant `_lifecycle_lock`. `connect()` still validates `timeout` before touching
any incumbent or the lock (so an invalid timeout never contends for it), then holds the lock across
incumbent teardown, candidate creation/connect, blocking-mode restoration, and attachment. Public
`disconnect()` now acquires the same lock before tearing down, so it serializes behind an in-flight
`connect()` instead of no-op'ing against a not-yet-attached candidate; both route internal teardown
through `_disconnect_locked` → `SocketHandler.disconnect` (not `self.disconnect`) to avoid recursive
acquisition of the non-reentrant lock. `tests/test_socket_handler_client.py` gained two deterministic,
sleep-free regression tests (`TestConcurrentConnectLifecycleSerialization`,
`TestConnectDisconnectInterleaving`), each verified to fail against the pre-fix code (2 live receive
workers / a leaked candidate; `disconnect()` racing to a no-op leaving the client connected) and pass
after the fix. `make fullCheck` (flake8 + strict mypy over `src/`+`tests/` + the full 897-test pytest
suite) passes.

**Gap:** none identified against this chunk's stated deliverable and acceptance criteria. Returned
for human review per the execution instructions (status left `active`, not `completed`).
