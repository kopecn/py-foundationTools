---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Implement the public synchronous transacting client with odd transaction IDs.
last_updated: 2026-09-12
semver: 0.0.1
author: Nicholas Bergantz
status: completed
---

# 14 — Transacting client role

Scope: [summary goal](00-overview.md#summary-goal) · [original ask](00-original-ask.md) · Contract: [client facade](../../specs/transactingSocketHandlers.md#composition-and-roles)

## Deliverable

Create `TransactingSocketHandlerClient` as the thin public composition of `SocketHandlerClient`, the shared engine, injected codec/logger, and odd transaction-ID core.

## Depends on

09 threaded socket client and 13 shared transacting engine.

## Files

- Create `src/foundation_tools/socket_transaction/transacting_socket_handler_client.py`.
- Create `tests/test_transacting_socket_handler_client.py`.

## Design constraints

- Constructor is exactly `TransactingSocketHandlerClient(logger, codec, *, join_timeout=1.0)`.
- Build one `SocketHandlerClient` configured from `codec.delimiter`, one core with `first_tx_id=1, tx_id_step=2`, and one shared engine.
- Delegate `is_connected`, `connect(host, port, timeout=1.0)`, `disconnect`, transaction methods, and callback setters without changing their errors/returns.
- Logger identity must reach transport, core, and engine unchanged.
- No inheritance from `SocketHandlerClient` is required; socket ownership remains singular through composition.

## TDD steps

1. Add failing construction/delegation tests using spies for logger/codec and real loopback where useful.
2. Prove IDs are odd across disconnect/reconnect and disconnected calls still consume an ID.
3. Prove connect/reconnect close observation wakes the correct pending client operations.
4. Implement the thin client role and run its focused test plus `make fullCheck`.

## Acceptance criteria

- [x] The client has one socket owner, one core, and one codec lock.
- [x] IDs are `1, 3, 5...` and do not reset on reconnect.
- [x] Every delegated method exactly preserves the accepted engine/transport contract.
- [x] No coroutine or async context-manager method exists.
- [x] `make fullCheck` passes.

## Out of scope

- Server behavior and bidirectional role integration.
- Package-root exports.
- Compatibility with `SocketTransact`.

## Ask ↔ result

- **Objective (`human_ask` + `goal`):** the recorded top-level `human_ask` directs replacing the asyncio socket stack in `src/foundation_tools/socket_transaction/` with threading/sockets, decomposed into bite-sized tasks. This chunk's recorded `goal` narrows that to implementing the public synchronous transacting client with odd transaction IDs. The two agree; no conflict found.
- **Live authorization:** `/execute-plan .claude/plans/25-threaded-socket-transaction`, explicitly authorizing execution of chunk 14 now.
- **Delivered:** `src/foundation_tools/socket_transaction/transacting_socket_handler_client.py` — `TransactingSocketHandlerClient(logger, codec, *, join_timeout=1.0)`, the thin public composition specified by the chunk and by `.claude/specs/transactingSocketHandlers.md#composition-and-roles`. The constructor builds exactly one `SocketHandlerClient` (configured from `codec.delimiter` and the given `join_timeout`), one `TransactionCore(logger, first_tx_id=1, tx_id_step=2)`, and one `TransactingSocketHandler(logger, socket, codec, core)` engine over them, passing the same `logger` instance to all three unchanged. It exposes `is_connected`, `connect(host, port, timeout=1.0)`, and `disconnect()` delegated verbatim to the contained `SocketHandlerClient`, and `send_transaction`, `send_broadcast`, `set_string_message_handler`, `set_broadcast_event_handler`, and `set_inbound_transaction_handler` delegated verbatim to the shared `TransactingSocketHandler` engine — no error/return behavior is altered on any path. No inheritance from `SocketHandlerClient`; composition keeps socket ownership singular (one `_socket`, one `_core`, one `_engine`, and the engine's own `_codec_lock` is the only codec lock — the facade holds no lock of its own). Not a `foundation_abc.PeripheralByteTransport`; `rg -n "asyncio|PeripheralByteTransport|async def"` against the new file matches only an explanatory docstring line, and no coroutine or async context-manager method exists on the class.
- `tests/test_transacting_socket_handler_client.py` — 13 tests, all synchronized with `threading.Event`/`start_worker`/real loopback accept, no sleeps or randomness:
  - `TestConstructionAndWiring` (6): the contained `SocketHandlerClient`'s `string_delimiter` comes from a distinctive spy codec's `delimiter` (not a hardcoded default); the same `logger` instance reaches `_socket._logger`, `_core._logger`, and `_engine._logger`; `_core` is built with `first_tx_id=1, tx_id_step=2`; `_engine._transport is client._socket` and `_engine._core is client._core`; `join_timeout` forwards to the contained socket handler; and no attribute on the class is a coroutine function, with no `__aenter__`/`__aexit__`.
  - `TestConnectionLifecycleDelegation` (3): `is_connected` reflects real loopback connect/disconnect; an invalid `connect` timeout raises the same `ValueError` as `SocketHandlerClient` and leaves the client disconnected, while the default `timeout=1.0` still connects; `disconnect()` is idempotent.
  - `TestOddTransactionIdSequence` (2): three consecutive disconnected `send_transaction` calls consume ids `1, 3, 5` and each returns `NOT_CONNECTED`/`CONNECTION_CLOSED`/`NOT_REQUESTED`; a disconnected call, a connected fire-and-forget send, a disconnect, a second disconnected call, and a reconnected fire-and-forget send produce ids `1, 3, 5, 7` in order — proving the sequence never resets across disconnect/reconnect.
  - `TestCloseWakesPendingClientOperations` (2): a `send_transaction(wait_ack=True)` blocked in a worker thread (synchronized via a test-only wrapper around `core.wait_ack` that signals a `threading.Event` at the instant the wait begins, i.e. strictly after registration and the send) is woken by `client.disconnect()` and settles as `send_status=SENT, ack_status=CONNECTION_CLOSED`, with the core's pending map empty afterward; and the same blocked pending op is woken by a *reconnect* (`client.connect` to a second listener, which disconnects the incumbent epoch first) while a subsequent call on the new epoch succeeds independently with the next odd id.
- **Verification:** confirmed TDD honesty by moving the new source file aside and re-running the test file — collection failed with `ModuleNotFoundError` (all 13 tests unable to run), then restored the source and reran to 13/13 passing. `make fullCheck`: flake8 clean, strict mypy clean (72 `src` files + 48 `tests` files), pytest 1000 passed (up from 987 before this chunk). `rg -n "asyncio|PeripheralByteTransport|async def" src/foundation_tools/socket_transaction/transacting_socket_handler_client.py` — only the explanatory docstring line matches. `git status --short` confirms only `src/foundation_tools/socket_transaction/transacting_socket_handler_client.py` and `tests/test_transacting_socket_handler_client.py` were added; no existing module was edited, no package export was added, and the pre-existing dirty worktree state (unrelated plan/spec edits) was left untouched.
- **Gap:** none identified against this chunk's in-scope deliverable or its design constraints.
