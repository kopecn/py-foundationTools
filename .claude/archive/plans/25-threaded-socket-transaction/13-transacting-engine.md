---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Implement the shared synchronous transaction engine over an epoch-aware socket handler.
last_updated: 2026-09-12
semver: 0.0.1
author: Nicholas Bergantz
status: completed
---

# 13 — Shared transacting engine

Scope: [summary goal](00-overview.md#summary-goal) · [original ask](00-original-ask.md) · Contract: [transaction composition and operation](../../../specs/transactingSocketHandlers.md#composition-and-roles)

## Deliverable

Create the internal shared transacting engine that observes epoch-tagged tokens/closure, serializes codec access, routes frames, exposes callbacks/broadcast, performs synchronous transactions, and creates epoch-bound `InboundTransaction` responders. Role-specific client/server lifecycle stays in chunks 14–15.

## Depends on

03 JSON transaction codec, 06 completed transaction core, and 08 receive dispatch.

## Files

- Create `src/foundation_tools/socket_transaction/transacting_socket_handler.py`.
- Create `tests/test_transacting_socket_handler.py`.

## Design constraints

- The internal engine receives an already-constructed `SocketHandler`, codec, and role-configured core; it never owns another socket.
- One codec lock serializes each individual encode/decode call. Release it before routing or invoking callbacks so responder encoding cannot deadlock.
- Decode and route before invoking raw string passthrough. A `ValueError` decode failure still reaches passthrough.
- Validate transaction timeout before allocating an ID. Every valid call consumes an ID; disconnected calls return a directly constructed `NOT_CONNECTED` outcome without registration.
- Active calls snapshot epoch, register before encode/send, use `send_for_epoch`, independently wait ACK/result, then atomically finalize/remove. Exception paths discard.
- `InboundTransaction.reply` is bound to the inbound epoch and reserved response/event types. `send_broadcast` uses `tx_id=-1`, `evt`, and the current epoch.
- Close observation calls `fail_epoch` only for the closing epoch.

## Transaction recipe

```python
validate_timeout(timeout)
tx_id = core.next_tx_id()
epoch = transport.snapshot_active_epoch()
if epoch is None:
    return not_connected_outcome(tx_id, wait_ack, wait_result)
core.register(epoch, tx_id)
try:
    wire = encode_under_codec_lock(tx_id, msg_type, code, payload)
    send_status = transport.send_for_epoch(epoch, wire)
    settle_requested_waits(send_status, tx_id, timeout)
    return core.finalize_outcome(...)
except BaseException:
    core.discard(tx_id)
    raise
```

Do not hold codec, socket, or transaction locks across send, waits, or callbacks.

## TDD steps

1. Add a fake epoch-aware handler and failing tests for disconnected/fire-and-forget/send-failure outcomes.
2. Add register-before-immediate-reply, encode/send rollback, independent timeout, mixed-stage, event retention, and close-wakeup tests.
3. Add malformed token passthrough, callback isolation, codec serialization, broadcast, and retained-responder-after-replacement tests.
4. Implement the engine and `InboundTransaction`.
5. Run `pytest tests/test_transacting_socket_handler.py` and `make fullCheck`.

## Acceptance criteria

- [x] Every registered path uses atomic finalization or exception discard; pending count returns to zero.
- [x] Immediate response cannot beat registration.
- [x] A retained old responder returns `False` and emits no bytes after replacement.
- [x] Mixed ACK/result outcomes and transaction events survive immutable outcome construction.
- [x] `make fullCheck` passes.

## Out of scope

- Connect/listen delegation and role ID defaults.
- Model parsing beyond codec-specified `DataModelHelper` serialization.
- Callback executors, retry, or automatic reconnect.

## Ask ↔ result

- **Objective (`human_ask` + `goal`):** the top-level `human_ask` directs reducing the asyncio socket stack in `src/foundation_tools/socket_transaction/` to threading/sockets, decomposed into bite-sized tasks. This chunk's recorded `goal` narrows that to implementing the shared synchronous transaction engine over an epoch-aware socket handler. The two agree; no conflict found.
- **Live request:** `/execute-plan .claude/plans/25-threaded-socket-transaction`, explicitly authorizing execution of this chunk now.
- **Delivered:** `src/foundation_tools/socket_transaction/transacting_socket_handler.py` — `TransactingSocketHandler(logger, transport, codec, core)`, the internal shared engine, plus `InboundTransaction`. The engine takes an already-constructed transport (typed against a narrow internal `TransactionTransport` structural protocol — `snapshot_active_epoch`/`send_for_epoch`/`send`/`set_connection_observer` — that any `SocketHandler` or role subclass satisfies without changes to that module), registers itself as the transport's connection observer and as the core's inbound-frame adapter at construction, and owns one `threading.Lock` codec lock plus one callback lock. `send_transaction` follows the chunk's recipe exactly: validates timeout before allocating an id, returns a directly constructed, unregistered `NOT_CONNECTED` outcome (mapping each requested stage to `CONNECTION_CLOSED` with a non-empty diagnostic, per the accepted spec's status-mapping rules) when disconnected, otherwise registers under the snapshotted epoch before encoding/sending, sends only for that epoch, and on any exception discards the pending entry before re-raising. On a non-`SENT` send outcome it calls `core.fail_epoch` for that epoch (idempotent, and necessary — not merely redundant with the transport's own close notification — for the narrow race where the epoch died between snapshot and registration) rather than waiting, then finalizes through `TransactionCore.finalize_outcome` on every path. `send_broadcast` encodes `tx_id=-1`/`msg_type="evt"` under the codec lock and reuses the transport's own current-epoch `send`. The receive pipeline (`on_string_token`) decodes under the codec lock only for the call itself, routes a decoded frame through the core for that epoch, and always still invokes the optional application string handler with the original token — logging and continuing past a `ValueError` decode failure or a callback exception. `on_epoch_closed` calls `fail_epoch` only for the closing epoch. `InboundTransaction.reply` raises `ValueError` before encoding for a non-`ack`/`res`/`err`/`evt` type, otherwise encodes with the inbound tx_id and uses `send_for_epoch` bound to the epoch captured at construction, returning `False` with no bytes sent once that epoch is superseded.
- `tests/test_transacting_socket_handler.py` (28 tests) uses a fake, non-socket `FakeTransport` satisfying the engine's own transport protocol (per this chunk's TDD step of adding "a fake epoch-aware handler") plus the real `JsonTransactionCodec` for realistic wire round-trips, and two purpose-built fake codecs (`_RaisingEncodeCodec`, `_BlockingCodec`) for the encode-failure and lock-serialization tests. Covers: disconnected/fire-and-forget/send-failure outcomes; timeout validation ordered before id allocation; register-before-immediate-synchronous-reply correlation; encode-failure rollback (pending discarded, exception propagates); independent ACK/result timeouts; mixed ack-then-timeout and rejected-ack-settles-completion-as-error outcomes; event retention across to the finalized outcome; a real-thread epoch-close wakeup of a blocked ACK wait (via `tests/threaded_socket_helpers.start_worker`, no sleeps); malformed-token passthrough to the string handler with routing skipped; decode-before-string-handler ordering; string/inbound callback exception containment; broadcast delegation to the core; broadcast encoding/epoch targeting and disconnected no-op; a retained `InboundTransaction` responder returning `False`/sending nothing after epoch replacement, a successful same-epoch reply, and `reply`'s reserved-type `ValueError`; and codec-lock serialization of two concurrent `send_broadcast` calls via a blocking fake codec that asserts non-reentrancy.
- **Verification:** confirmed TDD honesty by moving the new source file aside and re-running the test file — collection failed with `ModuleNotFoundError` (all 28 tests unable to run), then restored the source and reran to 28/28 passing. `make fullCheck`: flake8 clean, strict mypy clean (71 `src` files + 47 `tests` files), pytest 987 passed. `git status`/`git diff --stat` confirm only `src/foundation_tools/socket_transaction/transacting_socket_handler.py` and `tests/test_transacting_socket_handler.py` were added; no existing module was edited and no package export was added.
- **Gap:** none identified against this chunk's scope. Two points were resolved by inference beyond the chunk file's literal text, both narrow and internally consistent with the accepted specs rather than new requirements: (1) the engine calls `core.fail_epoch` on every non-`SENT` send status (not only `IO_FAILED`) to correctly settle the `NOT_ACTIVE`-before-registration race as `CONNECTION_CLOSED` per `transactingSocketHandlers.md`'s status-mapping rules, since `TransactionCore.finalize_outcome` (chunk 06, out of this chunk's edit scope) otherwise falls back an untouched requested stage to `NOT_REQUESTED`; (2) the engine's own `_validate_timeout` deliberately mirrors `TransactionCore`'s existing (non-bool-rejecting) timeout validation rather than inventing a stricter check, since neither accepted spec text calls for rejecting a boolean timeout the way both codecs explicitly reject boolean `tx_id`/`code` values. Neither is asserted as a new spec requirement; both are flagged here for a contract decision if a later chunk's facade or test exercises them differently.
