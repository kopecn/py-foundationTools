---
plan: ActionPlan17ServerStopLifecycle
scope: project
status: pending
last_updated: 2026-07-06
semver: 0.1.0
author: Nicholas Bergantz
---

# 17 — SocketTransactServer stop() Connection Lifecycle (corrective)

## Goal

Fully realize Server Compliance Requirement 7 of
[socketTransact.md](../specs/socketTransact.md) ("cancel in-flight handler tasks
and close connections on teardown"). `SocketTransactServer.stop()` currently
cancels handler-dispatch tasks and closes writers, but the per-connection
`_on_connect` reader loops (coroutines spawned by `asyncio.start_server`) are
untracked — they linger until socket EOF. If `stop()` is called while a client is
still connected, the reader loop outlives the teardown; on a fake-stream unit
path it would never terminate.

## Origin

Chunk 13 audit finding (corrective follow-up to plans 00–13).

## Depends on

None — independent.

## Files

- `src/foundation_tools/socket_transaction/socketTransactServer.py`
- `tests/test_socket_transact_server.py`

## Design constraints

- Track per-connection reader tasks: record `asyncio.current_task()` on
  `_on_connect` entry (discard on exit), or wrap the connection body in an
  explicitly created, tracked task. `stop()` cancels and awaits them after
  cancelling handler tasks, alongside closing writers.
- Teardown must be bounded: awaiting cancelled reader tasks uses
  `asyncio.gather(..., return_exceptions=True)` — no hang if a task is already
  finishing.
- Existing teardown behavior preserved: handler tasks still cancelled first,
  writers still closed, `stop()` stays idempotent.
- Graceful path unchanged: client-initiated close still ends the reader loop via
  EOF exactly as today.

## Steps (TDD)

1. Failing tests first: (a) `stop()` while a client is still connected returns
   promptly (test-bounded via `asyncio.wait_for`); (b) no lingering tasks after
   `stop()` — `asyncio.all_tasks()` delta assertion, same pattern as
   `tests/test_transaction_router.py` uses for the router's reader task.
2. Implement reader-task tracking + cancellation in `stop()`.
3. `make uv-fullCheck` (all existing e2e server tests must pass unchanged).

## Acceptance criteria

- [ ] `stop()` with live client connections terminates all per-connection reader
      loops promptly; no task leak (`all_tasks()` delta empty).
- [ ] `stop()` remains idempotent; graceful client-close path unchanged.
- [ ] All existing server unit + e2e tests pass unchanged.
- [ ] `make uv-fullCheck` passes.

## Out of scope

- Reconnect/keepalive, drain semantics, or a configurable shutdown grace period.
- `broadcast` semantics (best-effort fan-out stays as documented in chunk 13).
- Client-side (`SocketTransact`) lifecycle changes.
