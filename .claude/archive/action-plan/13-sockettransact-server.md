---
plan: ActionPlan13SocketTransactServer
scope: project
status: complete
last_updated: 2026-07-05
semver: 0.1.0
author: Nicholas Bergantz
---

# 13 — SocketTransactServer

## Goal

Implement the server role: accept connections, service plural inbound requests
simultaneously, reply tagged with each request's tx_id, push uncorrelated
broadcasts. This chunk also delivers the stack's **end-to-end proof**: our client
(`SocketTransact`) talking to our server over real sockets.

Contract: Layer 4b of [socketTransact.md](../specs/socketTransact.md).

## Depends on

08 (codecs — direct dependency), 10 (client facade — needed for the end-to-end
tests and the API-symmetry review).

## Files

- `src/foundation_tools/socket_transaction/socketTransactServer.py`
- `src/foundation_tools/socket_transaction/__init__.py` (add export)
- `tests/test_socket_transact_server.py`

## Design constraints

- `asyncio.start_server` wrapper; async context manager + `serve_forever()`;
  lifecycle operations raise (infrastructure semantics).
- `codec_factory` (not a codec instance) — reassembly buffers are per-connection
  state; every accepted connection gets a fresh codec.
- Handler contract: `handler: Callable[[bytes], Awaitable[bytes | None]]` —
  `bytes` → reply sent with the **request's own tx_id** injected; `None` → no
  reply. The server never strips or interprets payload beyond the injector/extractor
  pair (shared with the client stack).
- **Injector overwrite:** the shared `tx_id_injector` MUST overwrite any tx_id
  already embedded in the handler's reply (idempotent re-stamp). This is what
  makes a naive echo handler correct: the echoed request already carries the
  tx_id, and re-injection replaces rather than duplicates it.
- Concurrent dispatch: one task per inbound frame; optional
  `max_concurrent: int | None` semaphore (default unbounded). Replies complete out
  of order by design.
- Handler containment: exceptions never kill the per-connection reader loop —
  default drop + structured log; optional
  `error_reply_factory: Callable[[bytes, Exception], bytes | None]`.
- `broadcast(payload)` → uncorrelated frame to all connections (lands on client
  unsolicited streams).
- Teardown: stop accepting, cancel in-flight handler tasks, close all connections.

## Steps (TDD)

1. Tests first, unit level (fake streams): per-connection codec isolation
   (fragmented frames on two connections don't cross-contaminate); handler
   exception → loop survives, next request still served; `None` return → no reply;
   error_reply_factory path; `max_concurrent` honored; teardown cancels in-flight
   handlers; echo handler's reply carries the request's tx_id exactly once
   (injector overwrite, no duplication).
2. **End-to-end tests** (real sockets, `SocketTransact` client ↔
   `SocketTransactServer`):
   - `asyncio.gather` of N client requests against a handler with randomized
     per-request delay → every result matches its request despite out-of-order
     replies (the headline scenario)
   - two concurrent client connections served simultaneously
   - `broadcast` arrives on each client's `unsolicited()` stream
   - model round trip through both facades via `to_wire`/`from_wire`
3. Implement the server.
4. API-symmetry review against `SocketTransact` (naming, keyword-only style,
   containment table in the spec).
5. `make fullCheck`.

## Acceptance criteria

- [x] All 8 Server Compliance Requirements in socketTransact.md have tests.
- [x] End-to-end concurrent out-of-order scenario passes with our client.
- [x] Handler exception proven non-fatal to the connection.
- [x] `make uv-fullCheck` passes (`make fullCheck` no longer exists).

## Out of scope

- TLS, auth, connection limits/rate limiting.
- Targeted per-connection push (broadcast only until a consumer needs it).
- Request routing/multiplexing by message type (a single handler; dispatch tables
  are the application's concern).

## Implementation notes

- `asyncio.start_server(...)` already serves immediately on return
  (`start_serving=True` by default) — confirmed empirically before
  implementing: calling `Server.close()` cancels an in-progress
  `serve_forever()` await, so `start()`/`__aenter__` alone is sufficient to
  accept connections, and `serve_forever()` is purely the optional
  script-blocking convenience the spec's construction example shows. No
  `start_serving`/serve_forever coordination bug to design around.
- `_on_connect` (and the internals it drives — `_dispatch`, `_spawn_dispatch`,
  `_close_writer`) depend only on a structural `_StreamReaderLike`/
  `_StreamWriterLike` protocol (`read`/`write`/`drain`/`close`/
  `wait_closed`/`is_closing`), not concrete `asyncio.StreamReader`/`StreamWriter`
  — this is what let the unit tests drive the connection loop with plain fake
  objects (`FakeStreamReader`/`FakeStreamWriter` in the test file) instead of
  real sockets, mirroring the fake-transport convention from chunks 09/10.
- Two task registries: a per-connection `connection_tasks` set (local to
  `_on_connect`, cancelled/awaited in its `finally` so one connection's
  teardown doesn't touch another's in-flight handlers) and a server-wide
  `self._request_tasks` set (so `stop()` can cancel every in-flight handler
  across all connections). A task's `add_done_callback` removes it from both.
- `max_concurrent` is enforced with a plain `asyncio.Semaphore` wrapping
  `_dispatch_unbounded`; `None` (default) skips the semaphore entirely rather
  than using an unbounded one, avoiding a needless async context manager on
  the hot path.
- `broadcast` is deliberately non-raising per connection (loop over
  `self._connections`, catch `ConnectionError`/`RuntimeError`/`OSError` per
  writer and continue) — the spec doesn't classify `broadcast` in the
  Error-Handling Summary table, but a fan-out operation where one dead
  connection kills delivery to every other connected client would be a worse
  default than best-effort delivery with a structured log per failure.
- The `address` property (not in the spec) exposes the actually-bound
  `(host, port)` — needed because every test constructs the server with
  `port=0` (OS-assigned ephemeral port), matching the existing convention in
  the chunk-05/09 socket test fixtures.
- End-to-end tests are the chunk's headline proof: `SocketTransact` (chunk 10)
  against `SocketTransactServer` over real `asyncio.start_server` sockets —
  concurrent randomized-delay out-of-order replies, two simultaneous client
  connections, `broadcast` landing on a client's `unsolicited()` stream, and a
  full `to_wire`/`from_wire` model round trip through both facades (JSON-field
  tx_id scheme, same reasoning as chunk 10's model test: a raw string-prefix
  tx_id scheme would corrupt the wire string for JSON parsing).
