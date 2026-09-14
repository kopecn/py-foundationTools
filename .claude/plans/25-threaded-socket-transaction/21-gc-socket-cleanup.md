---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Allow an unreachable active handler to be collected and close its socket through best-effort finalization.
last_updated: 2026-09-13
semver: 0.1.0
author: Nicholas Bergantz
status: completed
---

# 21 - Make garbage-collection cleanup reachable

Scope: [summary goal](00-overview.md#summary-goal) · [original ask](../../archive/plans/25-threaded-socket-transaction/00-original-ask.md) · Contract: [cleanup](../../specs/threadedSocketTransport.md#detachment-and-cleanup)

## Origin

PA25-05: after deleting the last application reference and forcing collection, the post-audit observed the active handler and socket remain alive because both a bound atexit callback and the bound receive-thread target retained the handler.

## Deliverable

Remove internal strong-reference paths that prevent collection of an otherwise unreachable active handler, while retaining best-effort process-exit cleanup and normal explicit-disconnect behavior.

## Depends on

None.

## Files

- Edit `src/foundation_tools/socket_transaction/socket_handler.py`.
- Edit `src/foundation_tools/socket_transaction/socket_handler_server.py` only if receive-worker construction must use a shared weak-target helper.
- Edit `tests/test_socket_handler.py`.
- Edit `tests/test_socket_handler_server.py` only if server worker construction changes.

## Design constraints

- Do not register a bound method that retains the handler until process exit; `weakref.finalize` may provide its own process-exit invocation.
- A receive worker must not hold a strong handler reference across blocking `recv()`.
- The worker may receive on captured epoch resources, then resolve a weak handler reference only when dispatch or conditional detach is needed.
- Finalization closes the captured socket and signals its stop event without raising; explicit disconnect remains the path that notifies observers while the handler is alive.
- A finalized old epoch must have no route to a newer handler or socket.

## Worker recipe

```python
def receive_worker(owner_ref, epoch, sock, stop_event):
    data = sock.recv(4096)  # no strong owner reference while blocked
    owner = owner_ref()
    if owner is None:
        return
    owner._process_received_chunk(epoch, data)
```

Do not keep `owner` alive across the next blocking receive iteration.

## TDD steps

1. Add a failing GC regression using `weakref.ref`, `gc.collect()`, and a socketpair; prove the peer observes EOF without explicit disconnect.
2. Add a process-exit/finalizer exception-containment test around the resource callback.
3. Refactor worker and exit cleanup ownership minimally.
4. Run `pytest tests/test_socket_handler.py tests/test_socket_handler_server.py` and `make fullCheck`.

## Acceptance criteria

- [x] An active handler with no application references becomes unreachable under bounded polling after `gc.collect()`.
- [x] Its peer observes socket closure without explicit `disconnect()`.
- [x] Explicit disconnect still invokes the close observer exactly once.
- [x] Process-exit and finalizer cleanup remain best-effort and non-raising.
- [x] `make fullCheck` passes.

## Out of scope

- Running application observer callbacks during garbage collection.
- Forcing termination of a blocked application callback.
- Changing public lifecycle APIs or adding context-manager methods.

## Ask ↔ result

**Objective (`goal`/`human_ask`, PA25-05).** Allow an unreachable active handler to be collected and close its socket through best-effort finalization. The recorded `human_ask` is the plan-25 decomposition request; it does not conflict with executing this chunk now.

**Live authorization.** The user's live `/execute-plan 17 ... 25 these were from a post audit` command explicitly authorized executing corrective chunks 17-25, including this one (21).

**What was delivered.** Two strong-reference paths kept an active `SocketHandler` (and `SocketHandlerServer`, which shares the same defect) reachable independent of application references, per PA25-05's confirmed evidence:

1. `atexit.register(self._atexit_cleanup)` in `__init__` registered a bound method that the `atexit` module retains for the process's lifetime. Removed; `weakref.finalize` (already registered per-attach) makes its own best-effort process-exit invocation of the same `_finalize_socket` callback GC finalization uses, so process-exit and finalization are now literally the same code path, not two behaviors that happened to agree.
2. The receive-thread target was the bound method `self._receive_loop`. A running `Thread` blocked in `recv()` is kept alive by the interpreter's own thread bookkeeping, so this pinned the handler alive for as long as the connection stayed open. Replaced with a module-level `_receive_worker(owner_ref, epoch, sock, stop_event)` that resolves `owner_ref()` fresh only when dispatch or a conditional detach is actually needed, and drops the local reference before the next blocking `recv`. Both `SocketHandler._attach` and `SocketHandlerServer._start_receive_worker` (the latter had the identical defect and shares no override of the removed method) now construct the thread with `weakref.ref(self)` and this shared target.

`socket_handler_server.py` needed the matching change because its receive-worker construction reused the now-removed `self._receive_loop`; no other file in the chunk's list required changes.

**Verification.** Added `tests/test_socket_handler.py::TestGarbageCollectionCleanup::test_unreachable_handler_is_collected_and_peer_observes_closure` (`weakref.ref` + bounded `gc.collect()` polling + `socket.socketpair()`); confirmed it fails against the pre-fix code (stashed only the two source files, kept the new test, ran it — failed with the expected assertion) before implementing the fix. Added `TestCleanupRegistration::test_finalizer_callback_never_raises_on_unexpected_error` to cover finalizer/process-exit exception containment for an error class (`RuntimeError`) the inline `except OSError` guards do not catch. "Explicit disconnect still invokes the close observer exactly once" was already covered by pre-existing tests (e.g. `TestReceiveRaces::test_disconnect_called_from_a_string_callback_does_not_deadlock`) and re-verified green under the refactor. `make fullCheck` (flake8 + mypy + pytest, 905 tests) passes.

**Gap.** None identified against the chunk as written.
