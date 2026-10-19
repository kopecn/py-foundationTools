---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Complete transaction routing, epoch failure, callback isolation, and atomic outcome finalization.
last_updated: 2026-09-12
semver: 0.0.1
author: Nicholas Bergantz
status: completed
---

# 06 — Transaction core routing and finalization

Scope: [summary goal](00-overview.md#summary-goal) · [original ask](00-original-ask.md) · Contract: [routing and identifier rules](../../../specs/threadedTransactionProtocol.md#routing)

## Deliverable

Complete `TransactionCore` with every routing row, per-stage first-settlement rules, epoch-specific failure, isolated callbacks, orphan handling, and atomic outcome snapshot/removal.

## Depends on

05 transaction core registration and waits.

## Files

- Edit `src/foundation_tools/socket_transaction/transaction_core.py`.
- Edit `tests/test_transaction_core.py`.

## Design constraints

- Route by `(epoch, tx_id)`; an old epoch can never resolve a new epoch's waiter.
- Broadcast `evt` with negative ID bypasses pending state. Orphan `ack`/`res`/`err`/positive `evt` is logged and dropped. Application request types invoke the inbound callback.
- Invoke callbacks after releasing the transaction lock; callback exceptions are logged and contained.
- ACK and completion settle independently. Failed ACK settles ACK as `REJECTED` and unresolved completion as `ERROR`; result-before-ACK leaves ACK unresolved.
- `fail_epoch` settles only unresolved stages belonging to its epoch and signals both Events without removing entries.
- `finalize_outcome` snapshots immutable values and removes the entry in one lock acquisition. Exception cleanup uses idempotent `discard`.

## Terminal race recipe

```python
with self._lock:
    pending = self._pending.get(frame.tx_id)
    if pending is None or pending.epoch != epoch:
        action = orphan_or_inbound(frame)
    elif frame.msg_type == "res" and pending.completion_is_unresolved:
        pending.result = frame
        pending.completion_status = CompletionStatus.RESULT
        pending.done_event.set()
# invoke any selected callback only here, outside the lock
```

Use paired Barriers to race failed-ACK/RES, ERR/RES, and close/RES; assert one coherent first-settled result.

## TDD steps

1. Add one failing test per routing-table row, including exact ACK/error diagnostic text.
2. Add epoch mismatch, orphan, duplicate/late frame, callback failure, and event ordering tests.
3. Add barrier-controlled terminal race tests and atomic-finalization-versus-late-frame tests.
4. Implement routing, failure, callbacks, and finalization.
5. Run `pytest tests/test_transaction_core.py` and `make fullCheck`.

## Acceptance criteria

- [x] Every routing row in the accepted protocol spec has a named test.
- [x] All terminal race tests produce one of the allowed whole states and never overwrite it.
- [x] `finalize_outcome` removes the entry atomically and returns tuple-backed events.
- [x] Callback exceptions leave routing usable for a later frame.
- [x] `make fullCheck` passes.

## Out of scope

- Socket I/O and codec calls.
- User-facing inbound responder construction.
- Transaction facade lifecycle.

## Ask ↔ result

- **Objective (`human_ask` + `goal`):** the top-level ask directed reducing the asyncio socket stack to threading/sockets via bite-sized tasks; this chunk's recorded goal was to complete transaction routing, epoch failure, callback isolation, and atomic outcome finalization. No conflict between `human_ask` and `goal`.
- **Live request:** `/execute-plan .claude/plans/25-threaded-socket-transaction`, explicitly authorizing execution of this chunk now.
- **Delivered:** `src/foundation_tools/socket_transaction/transaction_core.py` now completes `TransactionCore` with `route(epoch, frame)`, `fail_epoch(epoch, error)`, `set_broadcast_event_handler`/`set_inbound_transaction_handler`, and `finalize_outcome`. `route` selects exactly one routing-table outcome under `self._lock`, invoking any selected broadcast/inbound callback only after the lock is released, with callback exceptions logged (`self._logger.exception`) and contained. Terminal stages settle on a strict first-settlement basis (ack success/failure, res, err, and — for completion only — a failed ack), with every losing/late/duplicate control frame logged at debug and dropped without mutating already-settled state; events accumulate only while completion is unresolved. `fail_epoch` settles only still-unresolved ack/completion stages belonging to its epoch to `CONNECTION_CLOSED`, signals both events unconditionally, and never removes entries. `finalize_outcome` pops the pending entry and builds the immutable `TransactionOutcome` (tuple-backed `events`, unrequested stages mapped to `NOT_REQUESTED`) in one lock acquisition, returning `None` for an unknown id; once removed, a later frame for that id is orphan-routed. A `_payload_text` helper decodes a `bytes` payload (UTF-8, replacement) before embedding it in the ack/err diagnostic text, so a payload of any of the frame's declared types renders as text rather than a `bytes` `repr` — driven by mypy's `str-bytes-safe` check, not a spec requirement, and confined to diagnostic-string rendering.
- `tests/test_transaction_core.py` grew from 57 to 104 tests (all pre-existing chunk-05 tests still pass unchanged). Added: one test per routing-table row (broadcast evt, orphan ack/res/err/evt, no-pending-entry application type, ack success, ack failure with/without payload and its exact diagnostic text, res, evt, err with its exact diagnostic text), epoch-mismatch tests (control frame and application-type against a stale-epoch pending), late/duplicate-frame tests (second ack, second res, err-after-res), callback-failure tests for both broadcast and inbound handlers (each asserting routing/state stays usable afterward) plus a reentrant-callback deadlock guard run on a bounded worker thread, `fail_epoch` tests (settles unresolved stages, does not overwrite already-settled ack or completion, only affects its own epoch, does not remove entries), `finalize_outcome` tests (unknown id, snapshot + `NOT_REQUESTED` mapping, immutable arrival-ordered `events` tuple, atomic single removal, orphan routing afterward), and three 30-iteration barrier-controlled terminal races (failed-ack-vs-res, err-vs-res, fail_epoch-vs-res) plus a 30-iteration atomic-finalization-vs-late-frame race — each asserting the settled state is always exactly one legal, non-hybrid outcome. Confirmed red-then-green: with the chunk-06 implementation stashed, the added tests failed with `AttributeError` on the not-yet-existing `route`/`fail_epoch`/handler-setters/`finalize_outcome`; restoring the implementation makes all 104 pass.
- `make fullCheck`: flake8 clean, strict mypy clean (66 `src` files + 42 `tests` files), pytest 831 passed.
- **Gap:** the spec and chunk file are silent on two edge cases the implementation had to resolve without direct textual authorization, both confined to internal, untested-by-name corners: (1) a failed ACK's completion-settling `completion_error` reuses the same `"ack code <code>[: <payload>]"` diagnostic text as `ack_error`, since the spec defines only one diagnostic message for that event and does not name a distinct completion-side message; (2) `finalize_outcome` for a stage that is `ack_requested`/`completion_requested` but still unresolved (`None` — a call sequenced before the corresponding wait, which the intended facade call order never does) falls back to `NOT_REQUESTED` rather than raising, since the spec only defines the *unrequested* mapping and this path is not exercised by any acceptance test. Neither choice is asserted as a new spec requirement here; both are flagged for a contract decision if a later chunk's facade exercises them differently.
