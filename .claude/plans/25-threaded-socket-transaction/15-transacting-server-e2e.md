---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Implement the transacting server role and prove both directions over real threaded sockets.
last_updated: 2026-09-12
semver: 0.0.1
author: Nicholas Bergantz
status: completed
---

# 15 — Transacting server role and bidirectional E2E

Scope: [summary goal](00-overview.md#summary-goal) · [original ask](00-original-ask.md) · Contract: [server facade and lifecycle coupling](../../specs/transactingSocketHandlers.md#lifecycle-coupling)

## Deliverable

Create `TransactingSocketHandlerServer` with even IDs and full server lifecycle delegation, then prove client-initiated, server-initiated, simultaneous, event, broadcast, and replacement behavior over real loopback TCP.

## Depends on

11 completed socket server, 13 shared transacting engine, and 14 transacting client.

## Files

- Create `src/foundation_tools/socket_transaction/transacting_socket_handler_server.py`.
- Create `tests/test_transacting_socket_handler_server.py`.
- Create `tests/test_threaded_socket_transaction_integration.py`.

## Design constraints

- Constructor exactly matches the accepted server facade and creates a core with `first_tx_id=2, tx_id_step=2`.
- Delegate listener/client state and lifecycle without adding another socket or worker.
- Server broadcast targets only the active client.
- Inbound callbacks respond only through their epoch-bound responder; callback code must return cooperatively.
- Integration synchronization uses Events/Barriers and the shared helper; no sleep/random timing.
- Simultaneous client/server transactions must use disjoint odd/even IDs and resolve out of wire order.

## E2E coordination recipe

```python
both_registered = threading.Barrier(3)

def initiate(endpoint, payload):
    both_registered.wait(TEST_TIMEOUT)
    outcomes.put(endpoint.send_transaction("request", 0, payload, wait_result=True, timeout=TEST_TIMEOUT))

client_thread.start()
server_thread.start()
both_registered.wait(TEST_TIMEOUT)
# responders release results in the opposite initiation order
```

Use explicit responder-entered/release Events for replacement tests so a reply for client A is attempted only after client B becomes active.

## TDD steps

1. Add failing server construction/delegation and even-ID tests.
2. Add real client request → server ACK/result, server request → client ACK/result, simultaneous bidirectional, transaction event, and broadcast tests.
3. Add admitted replacement while A's responder is retained; assert no A reply reaches B and A's waiter closes.
4. Add malformed message and callback exception recovery in both roles.
5. Implement the server role and run both focused files plus `make fullCheck`.

## Acceptance criteria

- [x] Server IDs are `2, 4, 6...`; simultaneous role IDs never collide.
- [x] Every end-to-end outcome matches its initiating payload and requested stages.
- [x] Old-client responders and receive workers cannot emit to or mutate the replacement client.
- [x] Integration tests contain no sleep or randomized delay.
- [x] `make fullCheck` passes.

## Out of scope

- Multiple active server clients or broadcast fan-out.
- Performance benchmarking or retry policy.
- Public cutover/deletion of asyncio modules.

## Ask ↔ result

- **Objective (`human_ask` + `goal`):** the top-level `human_ask` directs replacing the asyncio socket stack in `src/foundation_tools/socket_transaction/` with threading/sockets, decomposed into bite-sized tasks. This chunk's recorded `goal` narrows that to implementing the transacting server role and proving both directions over real threaded sockets. The two agree; no conflict found.
- **Live authorization:** `/execute-plan .claude/plans/25-threaded-socket-transaction`, explicitly authorizing execution of chunk 15 now.
- **Delivered:** `src/foundation_tools/socket_transaction/transacting_socket_handler_server.py` — `TransactingSocketHandlerServer(logger, codec, *, connection_admission_handler=None, join_timeout=1.0, accept_poll_interval=0.2)`, the thin public composition mirroring chunk 14's client facade for the server role. The constructor builds exactly one `SocketHandlerServer` (configured from `codec.delimiter`, `connection_admission_handler`, `join_timeout`, and `accept_poll_interval`), one `TransactionCore(logger, first_tx_id=2, tx_id_step=2)`, and one `TransactingSocketHandler` engine over both, passing the same `logger` instance to all three. It exposes `is_connected`, `active_peer`, `is_listening`, `listening_address`, `listen(port)`, `wait_for_connection(timeout=None)`, `disconnect()`, `kick()`, and `stop()` delegated verbatim to the contained `SocketHandlerServer`, and `send_transaction`, `send_broadcast`, `set_string_message_handler`, `set_broadcast_event_handler`, and `set_inbound_transaction_handler` delegated verbatim to the shared engine. No inheritance from `SocketHandlerServer`; no additional socket or worker thread is created by this module. Server broadcast targeting only the active client and epoch-bound inbound responders both fall out of the already-implemented `SocketHandlerServer`/`TransactingSocketHandler` behavior with no new logic needed here. Not a `foundation_abc.PeripheralByteTransport`; no coroutine or async context-manager method exists.
- `tests/test_transacting_socket_handler_server.py` (25 tests) — unit-level construction/wiring and delegation tests mirroring `test_transacting_socket_handler_client.py`'s structure: codec-delimiter configuration, logger identity reaching transport/core/engine, the even `first_tx_id=2, tx_id_step=2` sequence, engine-over-same-transport-and-core wiring, `join_timeout`/`accept_poll_interval`/`connection_admission_handler` forwarding, no coroutine/async-context-manager methods, `is_listening`/`listening_address`/`stop` delegation over a real ephemeral-port listener, `active_peer`/`is_connected` reflecting a real admitted client, `wait_for_connection` timeout validation and immediate-check semantics, `kick`/`disconnect` parity (each synchronized by waiting for a real round-tripped token before kicking, to avoid a pre-existing chunk-11 race between connection-state publication and receive-worker thread start that a bare `wait_for_connection` wake does not by itself rule out), and disconnected calls consuming sequential even ids `2, 4, 6`.
- `tests/test_threaded_socket_transaction_integration.py` (9 tests) — real bidirectional loopback-TCP E2E tests using `TransactingSocketHandlerClient` + `TransactingSocketHandlerServer` together: client-initiated request with server ACK/result; server-initiated request with client ACK/result; simultaneous bidirectional transactions using the chunk's `threading.Barrier(3)` recipe with explicit entered/release `Event`s releasing results in the opposite order from initiation, proving disjoint odd/even ids resolve independently out of wire order; a transaction event retained ahead of the final result; a server broadcast reaching the active client's broadcast handler with the correct frame, plus a disconnected-server broadcast returning `False`; admitted replacement while client A's inbound responder is retained — the responder never replies from inside the handler, client B is admitted, client A's own pending transaction is confirmed settled (via a bounded `WorkerHandle.join`, not a bare `wait_for_connection` check, since `is_connected` alone cannot distinguish "A still active" from "B has replaced A") before the retained responder's `reply()` is attempted, and the test asserts that `reply()` returns `False`, client B receives nothing, and A's outcome settled `ack_status`/`completion_status` as `CONNECTION_CLOSED`; and malformed-token-then-recovering-callback-exception coverage in both roles, each using a real raw socket peer (a bare `socket.socket` for the server-role test, a bare listener accepting the client's connection for the client-role test) so the malformed bytes and the exception-raising frame bypass the facade's own codec entirely.
- **Verification:** confirmed TDD honesty by moving the new source file aside and re-running both new test files — collection failed with `ModuleNotFoundError` in each (all 34 tests across the two files unable to run), then restored the source and reran to 25/25 and 9/9 passing, each stable across 8-10 repeated runs with no flakes. `make fullCheck`: flake8 clean; strict mypy clean (73 `src` files, 50 `tests` files); pytest 1025/1025 passed (up from 1000 before this chunk). `git status --short` confirms only the three files this chunk was scoped to create are new; no existing module was edited and no package export was added. Everything in "Out of scope" (multiple active clients/fan-out, benchmarking/retry, public cutover) remains untouched.
- **Gap:** none identified against this chunk's in-scope deliverable. One pre-existing condition outside this chunk's edit scope was worked around rather than fixed: `SocketHandlerServer._handle_accepted_candidate` (chunk 11, already `status: completed`) publishes connection state (waking `wait_for_connection`/`is_connected`) before its receive worker thread is guaranteed to have called `Thread.start()`; a test that calls `kick()`/`disconnect()` immediately after a bare `wait_for_connection` wake can race `SocketHandler._detach`'s `thread.join()` into `RuntimeError: cannot join thread before it is started`. This chunk's tests avoid the race by waiting for a real round-tripped token (proof the receive loop is already running) before any kick/disconnect, and by using a bounded `WorkerHandle.join` rather than a bare `wait_for_connection` check to confirm the replacement test's actual teardown-then-replace ordering. Flagged here as a chunk-11 contract question rather than silently patched, per the instruction not to edit existing modules in this chunk's scope.
