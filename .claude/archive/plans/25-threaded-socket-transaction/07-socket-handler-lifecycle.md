---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Implement socket composition, connection epochs, epoch-safe sending, and bounded teardown.
last_updated: 2026-09-12
semver: 0.0.1
author: Nicholas Bergantz
status: completed
---

# 07 — Socket handler epochs, teardown, and sends

Scope: [summary goal](00-overview.md#summary-goal) · [original ask](00-original-ask.md) · Contract: [common handler and detachment](../../specs/threadedSocketTransport.md#common-handler)

## Deliverable

Create `SocketHandler` and its internal connection-observer/send-status contracts with socket attachment, monotonically increasing epochs, serialized `sendall`, idempotent epoch-conditional teardown, and bounded cleanup. Receive dispatch beyond thread start/stop belongs to chunk 08.

## Depends on

01 deterministic threaded socket test support.

## Files

- Create `src/foundation_tools/socket_transaction/socket_handler.py`.
- Create `tests/test_socket_handler.py`.

## Design constraints

- Type the injected logger as `logging.Logger`; no internal logger creation.
- Own `socket.socket` by composition and keep state, send, callback, and observer synchronization distinct.
- Public disconnected send logs, drops, and returns `False`; internal `send_for_epoch` distinguishes `SENT`, `NOT_ACTIVE`, and `IO_FAILED`.
- Snapshot socket/epoch under the state lock, release it before blocking `sendall`, and conditionally detach only the captured epoch after releasing the send lock.
- Teardown removes active state before shutdown/close, never joins itself or while holding a lock, and logs a worker still alive after `join_timeout`.
- Register best-effort `atexit` and finalizer cleanup without allowing either to raise.

## Epoch-safe teardown recipe

```python
with self._state_lock:
    if self._epoch != expected_epoch:
        return False
    sock, thread, stop = self._socket, self._receive_thread, self._stop_event
    self._socket = None
    self._epoch = None
stop.set()
try:
    sock.shutdown(socket.SHUT_RDWR)
finally:
    sock.close()
if thread is not threading.current_thread():
    thread.join(self._join_timeout)
```

Notification and buffer cleanup must remain once-only even when send failure, EOF, and explicit disconnect race.

## TDD steps

1. Add failing constructor/delimiter/join-timeout and initial-state tests.
2. Through a small harness subclass, test attach, epoch monotonicity, duplicate detach, stale detach, self-detach, and bounded join.
3. Gate concurrent sends with Events and assert whole-message non-interleaving; race stale send failure against replacement.
4. Implement lifecycle/send behavior and best-effort cleanup registration.
5. Run `pytest tests/test_socket_handler.py -k "lifecycle or send or epoch"` and `make fullCheck`.

## Acceptance criteria

- [x] Concurrent `send` calls produce complete, non-interleaved buffers.
- [x] An old send/worker cannot close or write through a newer epoch.
- [x] Repeated disconnect/cleanup closes each socket at most once and never self-joins.
- [x] `rg -n "asyncio|async def" src/foundation_tools/socket_transaction/socket_handler.py` is empty.
- [x] `make fullCheck` passes.

## Out of scope

- Client connect and server listen.
- Text tokenization and binary frames.
- Transaction state or changes to `PeripheralByteTransport`.

## Ask ↔ result

- **Objective (human_ask + goal):** the recorded `human_ask` is the top-level directive to replace the asyncio socket stack in `src/foundation_tools/socket_transaction/` with threading/sockets. This chunk's `goal` narrows that to: implement socket composition, connection epochs, epoch-safe sending, and bounded teardown. No conflict between `human_ask` and `goal`.
- **Live authorization:** `/execute-plan .claude/plans/25-threaded-socket-transaction` — the user explicitly authorized executing chunk 07 now.
- **Delivered:** `src/foundation_tools/socket_transaction/socket_handler.py` — `SocketHandler(logger, *, string_delimiter="\n", join_timeout=1.0)` with the full common-handler public surface (`is_connected`, `string_delimiter`, `send`, `send_string`, `set_data_message_handler`, `set_string_message_handler`, `disconnect`) and internal contracts (`EpochSendStatus` enum, `ConnectionObserver` protocol, `snapshot_active_epoch`, `send_for_epoch`, `set_connection_observer`, protected `_attach`/`_detach`/`_receive_loop`/`_process_received_chunk`). Four distinct locks (state/send/callback/observer). Epoch-safe `send_for_epoch` snapshots socket+epoch under the state lock, releases it before the blocking `sendall`, serializes `sendall` under the send lock, and conditionally detaches only the captured epoch after releasing the send lock. `_detach` is idempotent and epoch-conditional, signals the stop event, notifies the close observer once, shuts down/closes the socket, and joins the receive thread bounded by `join_timeout` (skipped when the caller is the receive thread itself). The receive thread (`_receive_loop`) starts on attach, calls `recv(4096)` in a loop, and detaches its own epoch on EOF/`OSError`/stop; `_process_received_chunk` is left as a documented no-op stub for chunk 08. Best-effort `atexit` (bound method, calls `disconnect()`) and `weakref.finalize` (module-level `_finalize_socket`, holding no reference to the handler, re-registered on every attach) cleanup are both registered and never raise.
- `tests/test_socket_handler.py` — 24 tests: constructor/delimiter/join-timeout/initial-state validation; attach/epoch-monotonicity/duplicate-detach/stale-detach/self-detach/bounded-join-timeout-logging via a `_HarnessSocketHandler` subclass exposing the protected primitives; epoch-safe send (`NOT_ACTIVE`, success, UTF-8 `send_string`, `IO_FAILED` via a send-always-fails socket wrapper); Event-gated concurrent-send non-interleaving and a stale-send-vs-replacement-epoch race, both via a `_GatedSocket` test double that pauses `sendall` mid-call; finalizer registration/replacement on reattach.
- **Verification:** `pytest tests/test_socket_handler.py -v` — 24/24 passed. `rg -n "asyncio|async def" src/foundation_tools/socket_transaction/socket_handler.py` — no matches. `make fullCheck` — flake8, strict mypy (`src` + `tests`), and the full pytest suite (855 tests, up from 627 before this chunk) all passed.
- **Interpretation note (not a spec change):** the transport spec's Detachment section says finalization "SHALL make the same best-effort detachment" as normal teardown. This chunk's finalizer intentionally omits the connection-observer notification that normal `_detach` performs — running arbitrary observer callback code during GC finalization or interpreter shutdown is a well-known unsafe pattern, and keeping a bound-method reference to the handler on the finalizer would defeat prompt GC-triggered cleanup (a self-reference cycle). The finalizer still performs the socket shutdown/close/join. `atexit` cleanup (a bound method, acceptable there since atexit is expected to keep the object alive until process exit anyway) does call the full `disconnect()` path including observer notification. No spec was edited; this is flagged as an implementation judgment call for review.
- **Gap:** none against this chunk's in-scope deliverable. No package export was added (matches "Do NOT add package exports"); no client connect, server listen, text tokenization, binary frames, transaction state, or `PeripheralByteTransport` change was made.
