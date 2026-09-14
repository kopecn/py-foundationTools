---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Implement restartable IPv4 server listener epochs and bounded accept-thread lifecycle.
last_updated: 2026-09-12
semver: 0.0.1
author: Nicholas Bergantz
status: completed
---

# 10 — Server listener lifecycle

Scope: [summary goal](00-overview.md#summary-goal) · [original ask](00-original-ask.md) · Contract: [single-client server](../../specs/threadedSocketTransport.md#single-client-server)

## Deliverable

Create the listener half of `SocketHandlerServer`: bind/listen, actual address publication, listener epochs, daemon accept loop, repeated-listen warning, bounded stop, and safe restart. Chunk 11 owns admission and active-client publication.

## Depends on

08 raw and delimiter-text receive dispatch.

## Files

- Create `src/foundation_tools/socket_transaction/socket_handler_server.py`.
- Create `tests/test_socket_handler_server.py`.

## Design constraints

- Validate finite positive `join_timeout`/`accept_poll_interval` at construction.
- `listen(port)` creates `AF_INET`/`SOCK_STREAM`, sets `SO_REUSEADDR`, binds `("", port)`, listens, publishes `getsockname`, and starts one named daemon accept worker.
- Use a new listener epoch and stop Event per successful listen. The accept timeout is at most `accept_poll_interval`.
- While chunk 11 is absent, the protected accepted-candidate hook closes every candidate; do not partially introduce active-client semantics here.
- Repeated live `listen` warns/no-ops. Bind/listen failure closes the candidate listener and propagates `OSError`.
- `stop` retires the listener epoch before closing/joining; a stale timed-out worker can never alter restarted listener state.

## Stale listener recipe

```python
captured_epoch = listener_epoch
candidate, peer = listener.accept()
if not self._listener_epoch_is_active(captured_epoch):
    candidate.close()
    return
self._handle_accepted_candidate(captured_epoch, candidate, peer)
```

Every worker-finalization mutation is also conditional on `captured_epoch`.

## TDD steps

1. Add failing fake-socket tests for options, bind/listen failures, repeated listen, address, and stop ordering.
2. Add event-gated stale accept/admission-hook tests proving an old worker cannot affect a restarted listener.
3. Add real `port=0` start/stop/restart coverage through `listening_address` and `is_listening`.
4. Implement listener lifecycle and the protected candidate hook.
5. Run `pytest tests/test_socket_handler_server.py -k listener` and `make fullCheck`.

## Acceptance criteria

- [x] Exactly one accept worker belongs to each live listener epoch.
- [x] `listen(0)` publishes a usable nonzero port and stop clears it.
- [x] A stale accept worker closes its candidate and cannot clear/rewrite new state.
- [x] Repeated listen is a warning/no-op; repeated stop is a no-op.
- [x] `make fullCheck` passes.

## Out of scope

- Admission decisions, active peer, wait, kick, or incumbent replacement.
- Multiple-client serving.
- Transaction dispatch.

## Ask ↔ result

- **Objective (human_ask + goal):** the recorded `human_ask` is the top-level directive to replace the asyncio socket stack in `src/foundation_tools/socket_transaction/` with threading/sockets. This chunk's `goal` narrows that to: implement restartable IPv4 server listener epochs and bounded accept-thread lifecycle. No conflict between `human_ask` and `goal`.
- **Live authorization:** `/execute-plan .claude/plans/25-threaded-socket-transaction` — the user explicitly authorized executing chunk 10 now.
- **Delivered:** `src/foundation_tools/socket_transaction/socket_handler_server.py` — new `SocketHandlerServer(SocketHandler)` implementing only the listener half of the single-client server contract. `__init__(logger, *, string_delimiter="\n", join_timeout=1.0, accept_poll_interval=0.2)` validates `accept_poll_interval` is finite and `> 0` (join_timeout/string_delimiter validation is inherited unchanged from `SocketHandler`). Listener state (`epoch`, `socket`, `address`, `stop_event`, `thread`) is grouped into one internal `_ListenerState` dataclass swapped atomically under a dedicated `_listener_lock`, kept fully independent of the inherited connection-epoch lock/state. `listen(port)` creates an `AF_INET`/`SOCK_STREAM` socket, sets `SO_REUSEADDR`, binds `("", port)`, calls `listen()`, publishes the actual `getsockname()` address, allocates a new monotonically increasing listener epoch with a fresh `threading.Event`, and starts one named daemon accept worker (`{ClassName}-accept-{epoch}`); a bind/listen failure closes the candidate and propagates the original `OSError`; calling `listen` while already listening logs a warning and changes nothing (checked before any candidate socket is even created, with a second race-losing check after bind/listen closing a redundant candidate). `stop()` is idempotent: it retires the listener epoch (clears `_listener_state`) before closing the listener socket or joining the accept worker (bounded by `join_timeout`), so a stale, still-running worker can never observe or rewrite a restarted listener's state; a still-alive worker past the bound is logged, not raised. `is_listening` and `listening_address` read `_listener_state` under the lock. The accept loop (`_accept_loop`) wakes at least every `accept_poll_interval` (via `settimeout`), and after every `accept()` revalidates the captured listener epoch (`_listener_epoch_is_active`) before invoking the protected `_handle_accepted_candidate(epoch, candidate, peer)` hook — a stale epoch closes the candidate and exits the worker per the chunk's stale-listener recipe. Per the chunk's explicit constraint, `_handle_accepted_candidate` unconditionally closes every accepted candidate (chunk 11 will replace this with real admission/incumbent-replacement semantics); no admission handler, `active_peer`, `wait_for_connection`, `kick`, multi-client serving, transaction dispatch, or package export was added, and `foundation_abc.PeripheralByteTransport` is neither inherited nor referenced as a base.
- `tests/test_socket_handler_server.py` — 31 tests, all synchronized with `threading.Event`/bounded joins/`tests/threaded_socket_helpers.TEST_TIMEOUT`, no sleeps or randomness: constructor validation (defaults, custom/invalid `accept_poll_interval`, inherited `join_timeout`/`string_delimiter` validation); fake-socket listener options (`AF_INET`/`SOCK_STREAM`, `SO_REUSEADDR`, `bind("", port)`, `listen()` call, published `getsockname()` address); bind/listen failure closing the candidate and propagating the original `OSError`, including one proving an incumbent listener is untouched by a subsequent no-op `listen()`; repeated-listen no-op (no second candidate created) and its warning log; stop ordering (state cleared and candidate closed before/without needing the worker to exit, idempotent repeated `stop()`) and a stale-timed-out-worker case (`join_timeout=0.05`, worker still parked in a gated fake `accept()`) asserting the "still alive after join_timeout" warning is logged and `is_listening` is already `False`; the chunk's Event-gated stale-listener recipe end-to-end — a worker's `accept()` is parked mid-flight, the listener is `stop()`ped and a replacement `listen()`ed (new epoch), and only then is the stale `accept()` released, proving the stale candidate is closed and the replacement listener's epoch/address/close-count are untouched; the accepted-candidate hook closing every candidate both via a direct call and via a full accept-loop pass; and real `port=0` lifecycle tests (nonzero published port, clean `stop()`, restart, idempotent repeated `stop()`, and a real client connect that observes immediate EOF because chunk 10 closes every accepted candidate).
- **Verification:** confirmed TDD honesty by temporarily replacing the implementation with a no-op stub (constructor + always-`False`/`None` properties + no-op `listen`/`stop`) and re-running the file — 22 of 31 tests failed against the stub (9 pure-constructor-validation tests for inherited/independent checks still passed, as expected), then restored the real implementation and re-confirmed 31/31 passing. `rg -n "asyncio|async def" src/foundation_tools/socket_transaction/socket_handler_server.py` — no matches (only a docstring mentions `PeripheralByteTransport` to explain why it is deliberately not used). `git status --porcelain` confirms only `src/foundation_tools/socket_transaction/socket_handler_server.py` and `tests/test_socket_handler_server.py` were created; `src/foundation_tools/socket_transaction/__init__.py` was not touched. `make fullCheck` — flake8, strict mypy (`src` + `tests`), and the full pytest suite (924 tests, up from 871 before this chunk) all passed.
- **Gap:** none against this chunk's in-scope deliverable. Consistent with "Out of scope," no admission decision, `active_peer`, `wait_for_connection`, `kick`, incumbent replacement, multiple-client serving, or transaction dispatch was implemented — every accepted candidate is closed unconditionally, exactly as directed for while chunk 11 is absent.
