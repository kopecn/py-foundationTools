---
plan: ActionPlan10SocketTransact
scope: project
status: complete
last_updated: 2026-07-05
semver: 0.1.0
author: Nicholas Bergantz
---

# 10 — SocketTransact Facade

## Goal

Implement the public socket surface: `SocketTransact`, `SocketTransactResult`, and
`SocketTransactResultModel[T]`. This is the only class socket end users touch.

Contract: Layer 4 of [socketTransact.md](../specs/socketTransact.md).

## Depends on

09 (router).

## Files

- `src/foundation_tools/socket_transaction/socketTransact.py`
- `src/foundation_tools/socket_transaction/__init__.py` (add exports)
- `tests/test_socket_transact.py`

## Design constraints

- Construction wires the default stack (`SocketByteTransport` → codec → router);
  an alternative `PeripheralByteTransport` is injectable. The correlation pair
  (`tx_id_injector` / `tx_id_extractor`) is **required at construction — no
  default exists** (forwarded to the router per chunk 09). Async context manager
  entry connects and starts the router; exit tears down.
- API: `request(payload, *, tx_id=None, timeout=None)`, `request_with_model(...)`,
  `send(payload)`, `unsolicited()`. All async; `tx_id`/`timeout` keyword-only.
  `tx_id=None` → router generates + injects; explicit `tx_id` → payload already
  embeds it. Concurrent `request*` calls on one instance are safe (out-of-order
  reply resolution per the router contract).
- Containment mirrors `CLITransact`: `request*` never raises — timeout, connection
  loss, and codec errors land in the result (`success=False`, diagnostic `error`).
  Model parsing only on success + non-empty payload; parser failure appends to
  `error` and never flips `success`. `send` and lifecycle methods raise
  (transport-level ops).
- `request_with_model` uses `to_wire` outbound (when given a model) and
  `Model.from_wire` inbound — the wire bridge, no bespoke serialization.
- Result dataclasses are dumb containers built only by internal factories
  (same rule as chunk 02).

## Steps (TDD)

1. Tests first, against the chunk-05 server fixture and the fake transport:
   request success; **`asyncio.gather` of several concurrent requests against a
   server that replies out of order** — each result matches its request; request
   timeout → result not exception; connection drop mid-request → result; model
   round trip with a generated model; parser failure advisory; unsolicited
   iteration; context-manager lifecycle.
2. Implement facade + result types.
3. API review against the north star: count the calls a new user needs for
   "connect, ask, get a model back" — target is the `async with` + one `request*`.
4. `make fullCheck`.

## Acceptance criteria

- [x] All 11 Compliance Requirements in socketTransact.md have tests (this chunk
      closes the ones chunks 05/08/09 didn't).
- [x] `request*` proven non-raising across the failure matrix.
- [x] `make uv-fullCheck` passes (`make fullCheck` no longer exists).

## Out of scope

- Auth/TLS, server implementations, reconnection policy.
- Sync facade (revisit only if a real consumer needs it).

## Implementation notes

- `SocketTransact.__init__` wires the default stack (`SocketByteTransport` ->
  `codec` (default `DelimiterCodec()`) -> `TransactionRouter`); both `codec` and
  `transport` are injectable for testing (a `FramingCodec`/`PeripheralByteTransport`
  substitute, mirroring the router's own dependency injection).
- `request`/`request_with_model` wrap the router call in a single broad
  `except Exception` — this contains not just timeout/connection-loss/codec
  errors but also the router's immediate `RuntimeError` on a reused in-flight
  tx_id, satisfying compliance requirement 9's unconditional "never raise from
  those methods" (mirrors `CLITransact`'s own total-containment style, which
  deliberately lets `BaseException`/cancellation propagate).
- `request_with_model` accepts `DataModelHelper | bytes`; a model is serialized
  via `to_wire()` before the send, and outbound serialization failures are
  contained the same way as the request itself (never raises).
- The reply frame delivered to `SocketTransactResult.payload` is the router's
  raw frame, which still carries whatever the `tx_id_injector` stamped into it
  — the facade does not attempt to strip it (tx_id placement is protocol-
  specific, per the router's contract). The model round-trip test therefore
  uses a JSON-field tx_id scheme (`{"tx_id": ..., **model_fields}`) rather than
  a raw string prefix, since the generated `GeoCoordinate.from_dict` already
  ignores unknown keys — a raw prefix scheme (as used in the router's own
  tests) would corrupt the wire string for JSON parsing. Real protocols make
  the same choice: keep tx_id out of band from the serialized body, or embed it
  as a field the model's own decoder tolerates.
- `tests/test_socket_transact.py` reuses the chunk-09 `FakeTransport`/injector
  pattern (duplicated locally, matching this repo's existing one-fixture-set-
  per-test-file convention — no test file currently imports fixtures from
  another) plus one real integration test (`SocketByteTransport` +
  `DelimiterCodec` + a local asyncio server) proving concurrent out-of-order
  replies resolve to the correct caller through the full facade.
- API review (step 3): the north-star "connect, ask, get a model back" path is
  exactly `async with SocketTransact(...) as st: result = await
  st.request_with_model(model, ModelType)` — two calls, matching `CLITransact`'s
  one-call ethos at the facade layer.
