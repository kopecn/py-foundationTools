---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Make listener publication, accept-worker startup, and concurrent stop atomic and failure-safe.
last_updated: 2026-09-13
semver: 0.1.0
author: Nicholas Bergantz
status: completed
---

# 18 - Close listener startup/stop race

Scope: [summary goal](00-overview.md#summary-goal) · [original ask](../../archive/plans/25-threaded-socket-transaction/00-original-ask.md) · Contract: [server listen and stop](../../specs/threadedSocketTransport.md#single-client-server)

## Origin

PA25-02: the post-audit paused `Thread.start()` after listener publication, then reproduced `stop()` raising `RuntimeError: cannot join thread before it is started` and the released accept worker crashing on the closed listener.

## Deliverable

Make a successful listener publication inseparable from accept-worker startup as observed by `stop()`, with complete rollback if worker startup fails.

## Depends on

None.

## Files

- Edit `src/foundation_tools/socket_transaction/socket_handler_server.py`.
- Edit `tests/test_socket_handler_server.py`.

## Design constraints

- `stop()` must never observe a published, unstarted accept thread.
- Start the worker within the listener lifecycle critical section or represent startup explicitly so stop can handle it without joining an unstarted thread.
- If `Thread.start()` raises, retire only that listener epoch, close the candidate, and propagate the original startup exception.
- Protect the accept worker's initial socket configuration with the same containment boundary as its loop.
- Preserve repeated-listen no-op behavior, stale-listener epoch checks, bounded joins, and restartability.

## Race recipe

```python
start_entered = threading.Event()
release_start = threading.Event()

# Gate only the named accept worker's Thread.start().
listen_worker.start()
assert start_entered.wait(TEST_TIMEOUT)
stop_worker.start()
release_start.set()
```

The test must assert both public calls return without lifecycle exceptions, no uncaught worker exception is reported, the old listener is closed, and a new `listen(0)` succeeds.

## TDD steps

1. Add the failing publication-versus-stop regression and a worker-start-failure rollback test.
2. Confirm the regression raises against the current implementation.
3. Implement atomic startup/rollback and contain initial worker setup errors.
4. Run `pytest tests/test_socket_handler_server.py` and `make fullCheck`.

## Acceptance criteria

- [x] Concurrent `listen()`/`stop()` cannot join an unstarted worker.
- [x] A worker released after stop cannot crash on or mutate the retired listener.
- [x] `Thread.start()` failure leaves `is_listening` false and closes the candidate.
- [x] The same server instance can listen successfully afterward.
- [x] `make fullCheck` passes.

## Out of scope

- Admission policy or multiple-client serving.
- Connection receive-worker startup, already guarded separately.
- Retry or automatic listener restart.

## Ask ↔ result

**Objective (`human_ask`/`goal`):** `human_ask` is the planning-phase ask that authorized decomposing the top-level threaded-socket spec into bite-sized, threading-only chunks against `src/foundation_tools/socket_transaction/`. This chunk's `goal` narrows that to: make listener publication, accept-worker startup, and concurrent stop atomic and failure-safe, per the source-authorized PA25-02 finding and the cited contract in `.claude/specs/threadedSocketTransport.md#single-client-server`. The two do not disagree about the objective.

**Live authorization:** the user's `/execute-plan 17 ... 25` command explicitly authorized executing chunk 18 now.

**Delivered:** in `src/foundation_tools/socket_transaction/socket_handler_server.py`, `listen()` now calls `Thread.start()` for the new accept worker inside the same `_listener_lock` critical section that publishes `_listener_state`, so a concurrent `stop()` (which also acquires `_listener_lock` before reading/clearing that state) can never observe a published-but-unstarted thread — publication and startup are now one atomic, lock-serialized step. If `Thread.start()` raises, the epoch is retired (`_listener_state = None`), the candidate socket is closed, and the original exception propagates unchanged. Separately, `_accept_loop`'s initial `listener.settimeout(...)` call was moved inside the loop's existing `try/except Exception` boundary, per the chunk's fourth design constraint, so a failure configuring the accepted listener socket is contained and logged rather than crashing the daemon thread silently.

In `tests/test_socket_handler_server.py`: added `TestListenStopRace` (drives the chunk's exact race recipe — gates only the named accept worker's `Thread.start()`, starts `listen()` and `stop()` concurrently, and asserts both return without lifecycle exceptions, no crash is logged, the old listener is closed, and a fresh `listen()` still succeeds) and `TestListenerStartFailureRollback` (forces `Thread.start()` to raise for the accept worker and asserts the original exception propagates, `is_listening` is false, the candidate is closed, and the instance can still listen afterward). Both regressions were confirmed failing against the pre-fix code first (`RuntimeError: cannot join thread before it is started` for the race test; `close_calls == 0` for the rollback test), then confirmed passing after the fix.

**Verification:** `pytest tests/test_socket_handler_server.py` — 56 passed. `make fullCheck` — flake8 clean, mypy clean (67 src + 43 test files), pytest 899 passed (up from the audit's 895-test baseline by the 4 new test functions added here).

**Gap:** none identified against this chunk's scope. Status is left `active` (not `completed`) per the live execution instruction, for supervisor review.
