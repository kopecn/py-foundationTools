---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Complete server admission, one-client replacement, connection waiting, kick, and peer cleanup.
last_updated: 2026-09-12
semver: 0.0.1
author: Nicholas Bergantz
status: completed
---

# 11 — Server admission and client replacement

Scope: [summary goal](00-overview.md#summary-goal) · [original ask](00-original-ask.md) · Contract: [server admission and connection state](../../specs/threadedSocketTransport.md#single-client-server)

## Deliverable

Complete `SocketHandlerServer` as a one-active-client endpoint with admission callback isolation, atomic peer/socket publication, level-triggered wait, incumbent replacement, kick/disconnect, and matching-epoch peer closure.

## Depends on

10 server listener lifecycle.

## Files

- Edit `src/foundation_tools/socket_transaction/socket_handler_server.py`.
- Edit `tests/test_socket_handler_server.py`.

## Design constraints

- Snapshot the admission callback under its lock and invoke it on the accept thread outside every lock. Missing callback admits; false/exception rejects and closes without touching the incumbent.
- Detach an incumbent before challenger publication. Because detach may block, revalidate the listener epoch afterward.
- Perform final listener-epoch validation and challenger socket/connection-epoch/peer/availability publication in the same critical section used by `stop` to retire the listener.
- Start the receive worker only after all connected state is published. Roll back the same epoch if worker start fails.
- Implement `wait_for_connection` as a deadline loop over current state, not as a bare edge-triggered Event result.
- `disconnect` and `kick` clear the active peer but leave the listener; `stop` retires listener then kicks.

## Replacement race recipe

```python
self._detach_current_client()
with self._listener_state_lock:
    if self._listener_epoch != captured_listener_epoch:
        challenger.close()
        return
    connection_epoch = self._publish_client_locked(challenger, peer)
self._start_receive_worker(connection_epoch)
```

Tests must pause immediately before the final critical section, call `stop()`/`listen()` on another thread, then release the old worker and prove it closes the challenger.

## TDD steps

1. Add failing admission allow/deny/exception tests with an incumbent present.
2. Add active-peer, immediate/timeout wait, rapid connect-close, kick, and inherited disconnect tests.
3. Add deterministic admitted-replacement, stale-listener, and challenger-immediate-EOF races.
4. Implement admission and active-client behavior.
5. Run `pytest tests/test_socket_handler_server.py` and `make fullCheck`.

## Acceptance criteria

- [x] A rejected or callback-failing challenger never disconnects the incumbent.
- [x] An admitted challenger replaces and closes exactly one incumbent.
- [x] `wait_for_connection` returns `True` only while an active epoch exists at return.
- [x] Old peer EOF/kick cannot clear a replacement peer.
- [x] `make fullCheck` passes.

## Out of scope

- Multiple active clients, fan-out broadcast, per-request worker pools.
- Transaction decoding.
- Authentication, rate limiting, or backlog policy.

## Ask ↔ result

- **Objective (human_ask + goal):** the recorded `human_ask` is the top-level directive to replace the asyncio socket stack in `src/foundation_tools/socket_transaction/` with threading/sockets. This chunk's `goal` narrows that to: complete server admission, one-client replacement, connection waiting, kick, and peer cleanup. No conflict between `human_ask` and `goal`.
- **Live authorization:** `/execute-plan .claude/plans/25-threaded-socket-transaction` — the user explicitly authorized executing chunk 11 now.
- **Delivered:** `src/foundation_tools/socket_transaction/socket_handler_server.py` — extended chunk 10's listener-only `SocketHandlerServer` with the active-client half of the single-client server contract. Constructor gained `connection_admission_handler: Callable[[tuple[str, int]], bool] | None = None` (constructor-only, no public setter), read via a dedicated `_admission_lock` and invoked outside every lock in `_is_admitted`; no handler admits, a falsy return or a raised exception (logged) rejects. `_handle_accepted_candidate` now: rejects by closing the challenger without touching any incumbent; on admission, calls `_detach_current_client()` (a potentially blocking detach of any incumbent) *before* entering the listener-lock critical section; inside `with self._listener_lock:` it performs one final listener-epoch revalidation and, only if still current, calls `_publish_client_locked` (allocates a new connection epoch and publishes socket/epoch/`active_peer` together under the inherited `_state_lock`, mirroring but not reusing `SocketHandler._attach`, and deliberately not starting the receive thread yet); after the lock is released, `_start_receive_worker` re-validates the epoch (a concurrent kick/stop could have raced in the gap) and only then creates and starts the receive thread, registering the same best-effort GC finalizer as the base class and rolling the epoch back via `_rollback_unstarted_worker` (state clear + close-observer notify, but no `Thread.join` — the thread never started) if `thread.start()` raises. `active_peer` (new property) and connection availability are always cleared together for the exact epoch that closed via a `_detach` override: it pre-clears `active_peer`/`_active_peer_epoch` *before* delegating to `super()._detach`, because the base class fires its epoch-closed observer notification partway through its own critical section — clearing afterward left a window (caught by a failing test) where an observer-woken caller could see `is_connected is False` but a stale `active_peer`. Every teardown path (peer EOF, send failure, `disconnect`, `kick`, incumbent replacement) routes through this one override, so a stale epoch's late `_detach` call is a no-op against a newer epoch's peer (`would_detach = self._epoch == expected_epoch`, checked before touching `active_peer`). `kick()` detaches the active connection via `self._detach(epoch, cause="kicked")` and leaves the listener running; inherited `disconnect()` gets the identical effect for free since it also routes through the overridden `_detach`. `wait_for_connection(timeout)` validates `None` or finite non-negative timeout (raises `ValueError` otherwise), then runs a deadline loop that re-checks `self.is_connected` after every wake of a `_connection_state_changed` `threading.Event` (set on every publish and every successful detach) — level-triggered per the chunk's explicit constraint, never a bare `Event.wait(timeout)` result; `timeout=0` degenerates to one immediate check with no blocking. `stop()` now retires the listener (unchanged ordering: clear listener state, signal, close, bounded join, warn if still alive) and then unconditionally calls `self.kick()`, so a stopped server has no listener and no active connection; this is a no-op-safe addition (`kick()` is itself idempotent) that does not change any chunk-10 listener-only test's outcome.
- `tests/test_socket_handler_server.py` — grew from 31 to 53 tests (946 total in the suite, up from 924 after chunk 10). Two chunk-10 tests that asserted the placeholder "close every candidate unconditionally" behavior were rewritten in place (`TestAcceptedCandidateHookAdmitsByDefault`, replacing `TestAcceptedCandidateHookClosesEveryCandidate`) to assert the new default-admit behavior instead, per chunk 10's own file, which explicitly flagged that behavior as temporary "while chunk 11 is absent"; `test_real_client_connection_is_accepted_then_closed` was similarly rewritten to `test_real_client_connection_is_admitted_and_stays_open`. Every other chunk-10 test (constructor validation, listen options/address, bind/listen failures and incumbent-untouched, repeated-listen no-op, stop ordering, the stale-accept-worker recipe, and the remaining real `port=0` lifecycle tests) is unchanged and still passes. New coverage: `TestAdmissionDecisions` (no-handler admits, allowing handler receives the correct peer, denying handler closes the challenger and leaves an established incumbent's `active_peer`/`is_connected` untouched, raising handler is logged and rejects without disturbing the incumbent); `TestActivePeerWaitKickDisconnect` (`active_peer` `None` before any connection; `wait_for_connection(0)` as an immediate check both false and true; invalid timeouts — negative, `inf`, `-inf`, `nan` — raise `ValueError`; `wait_for_connection` woken from another thread once a connection is admitted; timeout expiry via a real 0.2s bound; a real rapid connect-then-immediate-close clears `active_peer`, observed deterministically via an installed `ConnectionObserver.on_epoch_closed` event rather than a sleep; `kick` detaches and leaves the listener running with the peer's socket observing EOF; `kick` on a disconnected server is a no-op; `disconnect` has the same active-client effect as `kick`); `TestReplacementAndStaleRaces` (an admitted challenger replaces and closes exactly one incumbent, observed as the incumbent's remote end seeing EOF; a stale `_detach` call for an already-replaced epoch is a no-op and cannot clear the replacement's `active_peer`; the chunk's stale-listener replacement race — gating a test subclass's `_detach_current_client` override immediately before the final critical section, then calling `stop()`/`listen()` on another thread before releasing — proves the challenger is closed, `active_peer` stays `None`, and the replacement listener's epoch is untouched; a challenger whose remote end sends immediate EOF right after publish is detached cleanly with no active peer left dangling). Admission/active-client tests use a real `socket.socketpair()` (built before any `socket.socket` monkeypatch, since `socketpair()` wraps its file descriptors through that same class) invoked via `handle_accepted_candidate` directly, so the real receive thread and real shutdown/close/detach paths run deterministically without needing a live remote peer for every case. No test uses a sleep or random delay; all blocking points are gated by `threading.Event`, an installed `ConnectionObserver`, or bounded joins.
- **Verification:** confirmed TDD honesty by temporarily reverting `_handle_accepted_candidate` to the chunk-10 unconditional-close stub and re-running the file — 16 of 53 tests failed against the stub (all of `TestAdmissionDecisions`, all of `TestActivePeerWaitKickDisconnect` except the two that assert pre-connection/invalid-timeout state, all of `TestReplacementAndStaleRaces`, plus the two rewritten hook/real-lifecycle tests), confirming they exercise real chunk-11 behavior rather than passing vacuously; the file was then restored to the real implementation and re-confirmed 53/53 passing (diff against the pre-revert copy is empty). `git status --porcelain` and `git diff --stat` confirm only `src/foundation_tools/socket_transaction/socket_handler_server.py` and `tests/test_socket_handler_server.py` changed. `rg -n "asyncio|async def" src/foundation_tools/socket_transaction/socket_handler_server.py` — no matches; the only `PeripheralByteTransport` occurrence is the pre-existing explanatory docstring line, not a base class. `make fullCheck` — flake8, strict mypy (`src` + `tests`), and the full pytest suite (946 tests) all passed.
- **Gap closed (post-verification follow-up):** added `TestReceiveWorkerStartFailureRollback::test_receive_worker_start_failure_rolls_back_the_connection_epoch` to `tests/test_socket_handler_server.py` (53 → 54 tests; suite total 946 → 959). It monkeypatches `threading.Thread.start` scoped by thread name (`"-receive-" in thread_self.name`) so only the receive-worker thread fails with a `RuntimeError`, leaving the listener's own accept thread and any other thread untouched — deterministic, no sleeps or randomness. After an admitted challenger's publish succeeds but its receive-worker `Thread.start()` raises, it asserts: `active_peer is None`, `is_connected is False`, the challenger socket is closed (`fileno() == -1`), the "failed to start" error is logged, the listener is still `is_listening` on the same epoch, and — as direct proof the listener keeps accepting — a second, real admission immediately afterward succeeds (`is_connected is True`, correct `active_peer`). No production seam was needed: `_rollback_unstarted_worker` already worked exactly as designed against this real `Thread.start()` failure, so this test passes against the existing implementation with zero changes to `socket_handler_server.py` (confirmed identical via diff against the pre-follow-up copy). Re-ran `pytest tests/test_socket_handler_server.py` (54/54 passed) and `make fullCheck` (flake8 clean; mypy "no issues found" for 70 `src` files and 46 `tests` files; pytest 959/959 passed). No remaining gap against this chunk's in-scope deliverable. Everything in "Out of scope" (multiple active clients, fan-out, transaction decoding, authentication/rate limiting/backlog policy) remains untouched.
