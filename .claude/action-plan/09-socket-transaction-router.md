---
plan: ActionPlan09SocketTransactionRouter
scope: project
status: pending
last_updated: 2026-07-03
semver: 0.0.3
author: Nicholas Bergantz
---

# 09 — Socket Transaction Router

## Goal

Implement the correlation layer: one reader task per connection, tx_id → future
resolution, unsolicited stream, clean teardown.

Contract: Layer 3 of [socketTransact.md](../specs/socketTransact.md).

## Depends on

08 (codecs), 05 (transport).

## Files

- `src/foundation_tools/socket_transaction/transaction_router.py`
- `src/foundation_tools/socket_transaction/__init__.py` (add export)
- `tests/test_transaction_router.py`

## Design constraints

- Composes a `PeripheralByteTransport` + a `FramingCodec` (dependency injection —
  tests use an in-memory fake transport, no real sockets needed).
- One background reader task: `receive → feed → dispatch`. Started on `start()`,
  cancelled on `stop()`.
- **Reader loop contract:** the loop calls
  `transport.receive(read_size, timeout=poll_timeout)` with constructor parameters
  `read_size` (default 4096) and `poll_timeout` (default 1.0 s). `TimeoutError` is
  an **idle tick** — loop continues, never tears down. An empty read (`b""`) or a
  transport error (`ConnectionError` / `RuntimeError` / `OSError`) means the
  connection is gone → teardown: fail all pending futures with a
  connection-closed error, end the unsolicited stream.
- Correlation contract is a **pair required at construction — no default exists**
  (the wire format is protocol-specific, so a silent default would mis-correlate):
  `tx_id_injector: Callable[[bytes, str], bytes]` (outbound stamping; MUST
  overwrite an already-embedded tx_id) +
  `tx_id_extractor: Callable[[bytes], str | None]` (inbound readback); default
  tx_id generator is a monotonic counter rendered as `str`.
- Request path order: generate tx_id → **register future** → inject → encode →
  send (a fast endpoint must never reply before the future exists). Explicit
  `tx_id=...` skips the injector (payload already embeds it) and sends verbatim.
- Dispatch: matching pending future → resolve; no match or `None` tx_id → bounded
  queue exposed as an async iterator. On overflow the **oldest frame is dropped**
  (with a structured log) — the reader task never awaits queue capacity.
- Per-request timeout via `asyncio.wait_for`; timed-out entries are removed so late
  replies become unsolicited frames.
- Reusing an in-flight tx_id raises immediately at request time.
- `stop()`/connection loss: reader task cancelled, all pending futures fail with a
  connection-closed error, unsolicited stream ends.

## Steps (TDD)

1. Build the in-memory fake transport fixture (scriptable inbound frames).
2. Tests first: request/reply correlation; **N concurrent requests answered
   out-of-order all resolve to the right callers** (the core concurrent-endpoint
   scenario); injector round trip (injected tx_id survives echo and extracts back);
   explicit `tx_id=` path skips the injector; future-registered-before-send race
   test (fake transport replies synchronously on send); unsolicited frame reaches
   the stream; late reply after timeout → unsolicited; duplicate in-flight tx_id
   raises; teardown cancels pending futures; reader never leaks (no pending-task
   warnings); unsolicited-queue overflow drops the oldest frame without stalling
   correlated replies; receive `TimeoutError` (idle tick) does not kill the
   reader; empty read (`b""`) tears down and fails pending futures with a
   connection-closed error.
3. Implement the router.
4. Integration test over the real `SocketByteTransport` + `DelimiterCodec` against
   the chunk-05 asyncio server fixture.
5. `make fullCheck`.

## Acceptance criteria

- [ ] All invariants in the spec's router section have tests.
- [ ] No thread usage; exactly one reader task, structurally cancelled.
- [ ] `make fullCheck` passes (pytest-asyncio, no event-loop warnings).

## Out of scope

- Result-object containment and model parsing (chunk 10 — the facade).
- Reconnect/resubscribe logic.
