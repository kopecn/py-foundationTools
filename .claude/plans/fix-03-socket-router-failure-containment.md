---
plan: Fix03SocketRouterFailureContainment
scope: project
status: pending
last_updated: 2026-08-23
semver: 0.0.1
author: Nicholas Bergantz
---

# Fix 03 — Socket-Router Failure Containment

## Goal

Turn malformed inbound frames and protocol callback failures into deterministic
connection teardown: every pending request fails, the unsolicited stream closes, and
`stop()`/`disconnect()` remain clean.

Contract: [socketTransact.md](../specs/socketTransact.md), Error Handling Summary.

## Depends on

Fix 02, so invalid constructor state is already impossible and this chunk can focus
on runtime wire failures from otherwise-valid codecs.

## Defect

`TransactionRouter._reader_loop` catches transport errors but calls `codec.feed()` and
the tx-id extractor outside that containment boundary. A `ValueError` from a malformed
length prefix currently:

1. terminates the background reader task with an exception;
2. leaves pending request futures unresolved when they have no caller timeout;
3. makes `stop()` re-raise the reader exception before `_teardown()` runs.

This contradicts the documented rule that the router resolves/cancels futures and
never raises into user code from the reader task.

## Files

Edit:

- `src/foundation_tools/socket_transaction/transaction_router.py`
- `tests/test_transaction_router.py`
- `tests/test_socket_transact.py`
- `HISTORY.md`

Update if the final behavior wording changes:

- `.claude/specs/socketTransact.md`

## Design constraints

**One terminal path.** Any ordinary `Exception` raised by `codec.feed`, frame dispatch,
or the tx-id extractor SHALL be wrapped in a diagnostic `ConnectionClosedError`, passed
to `_teardown`, and terminate the reader loop normally.

**Do not swallow cancellation.** `asyncio.CancelledError` remains a cancellation path;
do not catch `BaseException` around frame processing.

**No orphaned futures.** A request with `timeout=None` must complete with
`ConnectionClosedError` after malformed inbound data. Tests must use an outer bounded
`asyncio.wait_for` only as a test-harness deadlock guard.

**Facade containment.** `SocketTransact.request()` must convert that router failure to
`SocketTransactResult(success=False, error=...)`. Lifecycle methods still raise on
infrastructure failures, but this handled protocol failure must not poison a later
`disconnect()`.

**Reader task is observed.** `stop()` must safely await a reader task that already
finished, then clear router state and remain idempotent.

## Steps (TDD)

1. Add a codec test double whose `feed()` raises `ValueError("malformed frame")`.
2. Start one request without a router timeout, deliver an inbound chunk, and assert
   the request fails promptly with `ConnectionClosedError`.
3. Assert the unsolicited iterator terminates and `await router.stop()` does not
   re-raise the codec exception.
4. Add the equivalent `SocketTransact` facade test and assert a failure result plus
   clean disconnect.
5. Add a tx-id extractor failure case so callback exceptions follow the same path.
6. Implement the contained reader-loop path and idempotent task cleanup.
7. Add an `[Unreleased]` `Fixed` bullet.
8. Run the focused socket tests, then `make uv-fullCheck`.

## Acceptance criteria

- [ ] No malformed codec input can leave `_pending` futures unresolved.
- [ ] The background task finishes without an un-retrieved exception.
- [ ] `stop()` and `disconnect()` remain clean and idempotent after the failure.
- [ ] `SocketTransact.request()` returns `success=False` with actionable context.
- [ ] Cancellation semantics are unchanged.
- [ ] Existing real-socket integration tests pass.
- [ ] `make uv-fullCheck` passes.

## Out of scope

- Automatic reconnect or retry.
- Skipping a bad frame and continuing on the same byte stream; framing state may be
  corrupt, so connection teardown is the safe tier-1 behavior.
- Changing server-side handler exception semantics.
- Inventing a protocol-specific error reply.

