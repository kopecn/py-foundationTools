---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Provide deterministic reusable test support for threaded sockets without timing sleeps.
last_updated: 2026-09-12
semver: 0.0.1
author: Nicholas Bergantz
status: completed
---

# 01 — Deterministic threaded socket test support

Scope: [summary goal](00-overview.md#summary-goal) · [original ask](00-original-ask.md) · Contract: [threading model](../../../specs/threadedSocketTransaction.md#concurrency-model)

## Deliverable

Create the shared test harness future transport and integration chunks use to coordinate loopback sockets, worker completion, and captured thread failures without sleeps or random timing.

## Depends on

None.

## Files

- Create `tests/threaded_socket_helpers.py`.
- Create `tests/test_threaded_socket_helpers.py`.

## Design constraints

- Provide a context-managed IPv4 listener bound to `127.0.0.1:0` that exposes its actual address and uses `threading.Event` gates for ready, accepted, release, and stopped states.
- Provide a `socket.socketpair()` context helper for base-handler tests that do not need IPv4 connect/listen behavior.
- Capture worker exceptions and re-raise them from fixture teardown after closing sockets.
- Every helper-owned join has an explicit timeout and asserts the worker is dead; diagnostic failure includes the worker name and captured exception.
- Do not alter or remove `tests/asyncio_server.py`; non-socket packages and the old suite still need it until chunk 15.

## Race recipe

```python
ready = threading.Event()
release = threading.Event()

def worker() -> None:
    ready.set()
    if not release.wait(TEST_TIMEOUT):
        raise AssertionError("test did not release worker")

thread.start()
assert ready.wait(TEST_TIMEOUT)
# perform assertion at the controlled interleaving
release.set()
thread.join(TEST_TIMEOUT)
assert not thread.is_alive()
```

Use this pattern or `Barrier`; never replace an event gate with `time.sleep`.

## TDD steps

1. Add failing self-tests for address publication, accepted/release ordering, worker-exception propagation, socket cleanup, and bounded join failure.
2. Implement the helpers with named daemon workers and guaranteed `finally` cleanup.
3. Run `pytest tests/test_threaded_socket_helpers.py` and `make fullCheck`.

## Acceptance criteria

- [x] `rg -n "sleep|random" tests/threaded_socket_helpers.py tests/test_threaded_socket_helpers.py` finds no timing-based coordination.
- [x] A deliberate worker exception is surfaced by the owning context manager.
- [x] A helper exits with all sockets closed and no helper-named live thread.
- [x] `make fullCheck` passes.

## Out of scope

- Production socket code.
- Rewriting existing asyncio tests.
- Global thread-leak instrumentation outside socket tests.

## Ask ↔ result

- **Objective (human_ask + goal):** the recorded `human_ask` is the top-level directive to replace the asyncio socket stack in `src/foundation_tools/socket_transaction/` with threading/sockets, broken into bite-sized chunks. This chunk's `goal` narrows that to: provide deterministic reusable test support for threaded sockets without timing sleeps.
- **Live authorization:** `/execute-plan .claude/plans/25-threaded-socket-transaction` — the user explicitly authorized executing chunk 01 now. No conflict between `human_ask`/`goal` and the live command.
- **Delivered:** `tests/threaded_socket_helpers.py` — `WorkerHandle`/`start_worker` (named daemon thread, captured exception, bounded `join`, usable as a context manager), `ThreadedLoopbackListener` (context-managed `127.0.0.1:0` listener with `ready`/`accepted`/`release`/`stopped` `threading.Event` gates), and `socketpair_context` (`socket.socketpair()` context manager). `tests/test_threaded_socket_helpers.py` — 7 self-tests covering address publication, accepted/release/stopped ordering, worker-exception propagation via the owning context manager, socket cleanup after exit, bounded-join timeout diagnostics naming the worker, and the socketpair helper.
- **Verification:** `pytest tests/test_threaded_socket_helpers.py` — 7/7 passed. `rg -n "sleep|random" tests/threaded_socket_helpers.py tests/test_threaded_socket_helpers.py` — no matches (prose was reworded to avoid even docstring mentions of the literal words). `make fullCheck` — flake8, strict mypy (`src` + `tests`), and the full `pytest` suite (627 tests) all passed.
- **Gap:** none against this chunk's scope. `tests/asyncio_server.py` and all existing asyncio tests were left untouched; no production socket code was touched.
