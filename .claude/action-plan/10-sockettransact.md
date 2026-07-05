---
plan: ActionPlan10SocketTransact
scope: project
status: pending
last_updated: 2026-07-03
semver: 0.0.3
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

- [ ] All 11 Compliance Requirements in socketTransact.md have tests (this chunk
      closes the ones chunks 05/08/09 didn't).
- [ ] `request*` proven non-raising across the failure matrix.
- [ ] `make fullCheck` passes.

## Out of scope

- Auth/TLS, server implementations, reconnection policy.
- Sync facade (revisit only if a real consumer needs it).
