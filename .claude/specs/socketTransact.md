---
spec: SocketTransact
scope: project
status: implemented
applies_to: src/foundation_tools/socket_transaction/
last_updated: 2026-07-05
semver: 0.4.0
author: Nicholas Bergantz
---

# Socket Transaction Transport Layer Specification

> **Status — implemented.** All layers described below — the raw transport, the
> framing codecs, the transaction router, and both the client (`SocketTransact`)
> and server (`SocketTransactServer`) facades — are implemented in
> `foundation_tools/socket_transaction/`: an **asyncio-native**, long-lived-connection
> counterpart to the process-transaction family. It supersedes an earlier
> thread-driven draft; the thread/callback model was intentionally replaced by
> asyncio primitives (see [Learned Behaviors](#learned-behaviors)).
>
> This is the stream-transport family of the umbrella
> [transport_transaction_architecture.md](transport_transaction_architecture.md);
> consult it for the layer model, public-surface rule, and package layout.

---

# Overview

The socket subsystem provides a bidirectional, pluggable stream-transport stack that
supports:

- raw byte transport (asyncio TCP)
- string tokenization (delimiter-based framing)
- binary framing (length-prefixed)
- transactional routing (tx_id correlation)
- both roles: client (`SocketTransact`, Layers 1–4) and server
  (`SocketTransactServer`, Layer 4b) — the layers below the facades are shared

It is designed to be:

- transport-agnostic at upper layers
- codec-pluggable at the protocol layer
- fully asynchronous — no thread management, no blocking of the event loop

---

# System Role

```text
Application
      │
      ▼
SocketTransact            # Layer 4 — public facade, result objects
      │
      ▼
Transaction Router        # tx_id correlation via asyncio futures
      │
      ▼
Framing Codec             # delimiter / length-prefixed framing,
      │                   # DataModelHelper to_wire / from_wire
      ▼
SocketByteTransport       # implements foundation_abc.PeripheralByteTransport
      │
      ▼
asyncio streams
```

Each layer owns one responsibility. Lower layers never depend on higher layers.

---

# Design Philosophy

## Composition over inheritance

All socket behavior is composed: the transport owns the connection, codecs own
framing, the router owns correlation, the facade owns the public surface. No layer
subclasses another.

## Asyncio-native concurrency

Every I/O operation is asynchronous. There is exactly one reader task per
connection, owned by the transaction router. No recv threads, no callback
registries — inbound data is delivered through awaitables (futures) and async
iterators (streams).

## Dual-channel receive model

Every connection yields **two independent inbound channels**:

- **Correlated replies** — frames whose tx_id matches a pending request resolve
  that request's future.
- **Unsolicited stream** — frames with no pending correlation (server pushes,
  broadcasts) are exposed as an async iterator.

These operate simultaneously and do not interfere. (This preserves the dual-channel
idea of the original draft, recast from callback threads to async streams.)

---

# Layer 1 — SocketByteTransport

Status: Implemented (`socket_byte_transport.py`)

An asyncio TCP client implementing `foundation_abc.PeripheralByteTransport`
(`connect` / `disconnect` / `send` / `receive` / `is_connected`, plus the async
context manager inherited from the ABC).

Responsibilities:

- own the `asyncio.open_connection` reader/writer pair
- move raw bytes only — no framing knowledge (STX/ETX, delimiters, checksums, and
  length prefixes belong to codecs)
- honor the ABC's raising semantics: `ConnectionError` on failed connect,
  `RuntimeError` when used while disconnected, `TimeoutError` on receive timeout
- signal end-of-stream explicitly: when the peer has closed the connection and no
  buffered data remains, `receive` returns `b""` immediately (never `TimeoutError`)
  — the empty read is the closed-connection signal upper layers consume
- clean teardown: `disconnect()` closes the writer and awaits `wait_closed()`;
  double-disconnect is a no-op

Guarantees:

- never blocks the event loop
- deterministic construction: host/port/connect-timeout supplied at construction,
  no environment inspection
- portable: any other `PeripheralByteTransport` implementation (serial, EtherCAT
  adapter, mock) can be substituted underneath the upper layers unchanged

---

# Layer 2 — Framing Codecs

Status: Implemented (`framing_codecs.py`)

A codec converts between a byte stream and discrete frames. Codecs are pluggable
behind one protocol (structural typing / `typing.Protocol`):

```python
class FramingCodec(Protocol):
    def encode(self, payload: bytes) -> bytes: ...
    def feed(self, data: bytes) -> list[bytes]: ...
```

- `encode` wraps one outbound payload into wire bytes.
- `feed` accepts an arbitrary inbound chunk and returns zero or more **complete**
  frames; partial frames are buffered internally. This is the only stateful part of
  the stack, and its state is limited to the reassembly buffer.

Two codecs SHALL ship:

## DelimiterCodec

- frames are payloads terminated by a configurable delimiter (default `\n`)
- suited to line/token protocols and `DataModelHelper.to_wire` string payloads
  (encoded UTF-8)

## LengthPrefixedCodec

- frames are `<length prefix><payload>` with a configurable prefix width and
  endianness (default: 4-byte big-endian unsigned)
- suited to binary protocols

## Model bridge

Codecs frame **bytes**; model conversion composes on top via `DataModelHelper`:

- outbound: `model.to_wire()` → encode to bytes → `codec.encode(...)`
- inbound: `codec.feed(...)` → decode bytes → `Model.from_wire(...)`

No codec defines its own serialization format — see the **Wire Serialization
Bridge** section of
[transport_transaction_architecture.md](transport_transaction_architecture.md).

---

# Layer 3 — Transaction Router

Status: Implemented (`transaction_router.py`)

The router owns the single reader task and correlates request/response traffic.

Responsibilities:

- run one background reader task:
  `transport.receive(read_size, timeout=poll_timeout)` → `codec.feed(...)` →
  dispatch complete frames. `read_size` (default 4096) and `poll_timeout` (default
  1.0 s) are router construction parameters. A `TimeoutError` from `receive` is an
  **idle tick**, not an error — the loop simply continues
- detect connection loss in the reader loop: an empty read (`b""`, end-of-stream)
  or a `ConnectionError` / `RuntimeError` / `OSError` from the transport triggers
  teardown — all pending futures fail with a connection-closed error and the
  unsolicited stream ends
- extract tx_id from each inbound frame via a caller-supplied
  `tx_id_extractor: Callable[[bytes], str | None]`
- resolve the pending `asyncio.Future` matching the tx_id, if any
- route frames with no matching pending future (or `None` tx_id) to the unsolicited
  stream — a bounded `asyncio.Queue` exposed as an async iterator. On overflow the
  **oldest frame is dropped** (with a structured log) and the new frame enqueued;
  the reader task never awaits queue capacity, so a slow unsolicited consumer can
  never stall correlated replies
- per-request timeout via `asyncio.wait_for`; a timed-out request's pending entry is
  removed so a late reply becomes an unsolicited frame, not a crash
- teardown: cancel the reader task, cancel all pending futures with a
  connection-closed error, close the unsolicited stream

## Correlation contract (both directions)

The tx_id must survive a full round trip through the remote endpoint, so the
correlation contract is a **pair** configured together at router construction:

```python
tx_id_injector: Callable[[bytes, str], bytes]   # outbound: stamp tx_id into frame
tx_id_extractor: Callable[[bytes], str | None]  # inbound: read tx_id back out
```

The pair is **required at router (and facade) construction — no default exists**.
tx_id placement is protocol-specific, and the stack is forbidden from defining a
serialization format of its own (see the Wire Serialization Bridge of the umbrella
spec), so it cannot invent one.

The injector MUST **overwrite**: stamping a tx_id into a payload that already
embeds one replaces the existing id (idempotent re-stamping) — it never duplicates.
This is what lets the server inject a request's tx_id into a handler reply that
echoes the request payload.

The request path is strictly ordered so a fast endpoint can never reply before the
future exists:

```text
generate tx_id → register future → inject tx_id into payload → encode → send
```

Alternatively, a caller whose payload **already embeds** a tx_id passes it
explicitly (`request(payload, *, tx_id=...)`); the injector is skipped and the
router only registers and correlates. Exactly one of the two mechanisms applies per
request: no explicit `tx_id` → injector required; explicit `tx_id` → payload sent
verbatim.

This is what makes the layer safe against endpoints that service **many inbound
requests concurrently** and feed results back in arbitrary order: N in-flight
futures, each keyed by its tx_id, resolve independently of reply order.

Invariants:

- tx_id generation is caller-configurable; the default is a monotonically increasing
  counter rendered as a string
- the future is registered **before** the frame is written to the transport
- exactly one pending future per tx_id; reusing an in-flight tx_id is a programmer
  error and SHALL raise immediately at request time
- the router never interprets payload semantics beyond tx_id injection/extraction

---

# Layer 4 — SocketTransact (public facade)

Status: Implemented (`socketTransact.py`)

`SocketTransact` is the only class end users need. It mirrors the process family's
ethos: minimal surface, result objects, no exceptions on the transaction surface.

## Construction

```python
async with SocketTransact(
    host,
    port,
    codec=DelimiterCodec(),
    tx_id_injector=my_injector,     # required — no default (see router contract)
    tx_id_extractor=my_extractor,   # required — no default
) as st:
    ...
```

Construction wires the default stack (SocketByteTransport → codec → router).
`codec` defaults to `DelimiterCodec()` when omitted. The correlation pair is
**required** — tx_id placement is protocol-specific and the stack defines no
serialization format of its own, so there is no default the facade could supply.
An alternative `PeripheralByteTransport` implementation MAY be injected for
testing or non-TCP streams.

## Public API

| method | returns | notes |
| --- | --- | --- |
| `request(payload, *, tx_id=None, timeout=None)` | `SocketTransactResult` | send one frame, await the correlated reply |
| `request_with_model(model_or_payload, model_type, *, tx_id=None, timeout=None)` | `SocketTransactResultModel[T]` | `to_wire` outbound / `from_wire` inbound |
| `send(payload)` | `None` (raises on transport failure) | fire-and-forget frame (no correlation) |
| `unsolicited()` | `AsyncIterator[bytes]` | server-push / broadcast stream |

All methods are `async`. `timeout` and `tx_id` are keyword-only, mirroring
`CLITransact`'s keyword-only style. `tx_id=None` (the common path) lets the router
generate and inject the id; passing `tx_id` explicitly means the payload already
embeds it. Concurrent `request*` calls on one `SocketTransact` are safe and may
resolve in any order — see the router's correlation contract.

## `SocketTransactResult`

```python
@dataclass
class SocketTransactResult:
    payload: bytes | None = None
    error: str | None = None
    success: bool = False
```

`SocketTransactResultModel[T]` extends it with `model: T | None = None`, `T` bound to
`DataModelHelper` — the exact analogue of `CLITransactResultModel`.

## Containment semantics

- `request*` methods never raise: timeout, connection loss, and codec errors are
  captured into the result (`success=False`, diagnostic in `error`).
- Model parsing follows the `CLITransact` rule: attempted only on success with a
  non-empty payload; a parser failure is appended to `error` and never changes
  `success`.
- The **raw transport** (Layer 1) keeps ABC-level raising semantics; containment is
  a transaction-surface property, not a transport property.

---

# Layer 4b — SocketTransactServer (server role)

Status: Implemented (`socketTransactServer.py`)

`SocketTransactServer` is the server-side counterpart of `SocketTransact`: it
accepts connections, services **plural inbound requests simultaneously**, and feeds
results back tagged with each request's tx_id — the endpoint the client-side router
is built to talk to. It reuses the same codec protocol and the same
injector/extractor correlation pair, mirrored in direction (extract from requests,
inject into replies).

## Construction & lifecycle

```python
async with SocketTransactServer(
    host, port,
    handler=my_handler,
    codec_factory=DelimiterCodec,   # fresh codec per connection
) as server:
    await server.serve_forever()
```

- wraps `asyncio.start_server`; lifecycle operations raise (server is
  infrastructure, like the client's `send`/connect path)
- **codec_factory, not codec instance** — the reassembly buffer is per-connection
  state, so every accepted connection gets its own codec
- teardown: stop accepting, close all connections, cancel in-flight handler tasks

## Handler model

The caller supplies one async handler:

```python
handler: Callable[[bytes], Awaitable[bytes | None]]
```

- input: the request payload (tx_id still embedded — the server does not strip it)
- return `bytes` → reply frame; the server injects the **request's own tx_id** and
  sends it back. Because the injector overwrites (see the correlation contract), a
  handler that echoes the request payload — tx_id and all — still yields a reply
  carrying the request's tx_id exactly once
- return `None` → no reply (one-way message)

## Concurrent dispatch

Each complete inbound frame dispatches as its **own task** — a slow handler never
blocks other requests on the same (or any other) connection. Replies therefore
complete out of order by design; the client router's future-per-tx_id model absorbs
this. Concurrency MAY be bounded via an optional `max_concurrent: int | None`
semaphore (default `None` = unbounded).

## Handler containment

A handler exception MUST NOT kill the connection's reader loop. Default behavior:
drop the reply and log structured failure. Optionally the caller supplies

```python
error_reply_factory: Callable[[bytes, Exception], bytes | None]
```

to convert a handler failure into an error reply (tx_id injected as usual).

## Server push

`broadcast(payload)` sends an **uncorrelated** frame (no tx_id, or a tx_id no
client is awaiting) to all connected clients — arriving on each client's
unsolicited stream. Targeted per-connection push is deliberately out of scope until
a consumer needs it.

## Server Compliance Requirements

A compliant `SocketTransactServer` MUST:

1. be fully asynchronous — no threads, no blocking of the event loop
2. create one codec instance per accepted connection (via `codec_factory`)
3. dispatch each inbound frame as an independent task (plural simultaneous
   requests; optional bounded concurrency)
4. reply with the originating request's tx_id via the shared injector
5. contain every handler exception — the per-connection reader loop never dies
6. support `None` handler returns (no reply) and `broadcast` for uncorrelated push
7. cancel in-flight handler tasks and close connections on teardown
8. add zero external runtime dependencies (stdlib only)

---

# Error Handling Summary

| layer | failure behavior |
| --- | --- |
| SocketByteTransport | raises per `PeripheralByteTransport` contract |
| FramingCodec | raises `ValueError` on malformed frame data |
| Transaction Router | resolves/cancels futures; never raises into user code from the reader task |
| SocketTransact `request*` | returns `SocketTransactResult` — never raises |
| SocketTransact `send` / lifecycle | raises (transport-level operations) |
| SocketTransactServer lifecycle | raises (infrastructure operations) |
| SocketTransactServer handler dispatch | contained — logged, optional error reply, loop survives |

---

# Learned Behaviors

## Asyncio replaces the recv thread

The original draft owned a recv thread per socket with thread-safe socket swap and
`atexit` cleanup. In an asyncio-first codebase that design double-manages
concurrency and violates the `PeripheralByteTransport` "never block the event loop"
constraint. One reader task per connection, owned by the router, provides the same
single-reader guarantee with structured cancellation instead of thread teardown.

## Correlation is futures, not callbacks

Request/response correlation resolves an `asyncio.Future` rather than invoking a
registered handler. Callers `await` their reply; no handler registry, no reentrancy
hazards.

## Unsolicited traffic is a stream, not a handler

The draft's `data_handler`/`string_handler` callbacks become one async iterator of
frames. Consumers pull at their own pace; a bounded queue with drop-oldest overflow
protects memory without ever blocking the reader — a slow unsolicited consumer
loses old push frames but can never stall correlated request/reply traffic.

## Framing is a codec, not a transport feature

The transport moves bytes; tokenization and length-prefix logic live in codecs, so
serial/EtherCAT transports gain framing for free.

## Serialization is the wire bridge

Codecs and the model-aware facade methods compose `DataModelHelper.to_wire` /
`from_wire` — the socket stack defines no serialization format of its own.

## Late replies degrade gracefully

A reply arriving after its request timed out is routed to the unsolicited stream.
Timeouts are results, not control flow — mirroring `CLITransact`.

---

# Compliance Requirements

A compliant socket_transaction implementation MUST:

1. be fully asynchronous — no threads, no blocking I/O on the event loop
2. implement Layer 1 against `foundation_abc.PeripheralByteTransport` exactly
3. keep framing knowledge exclusively in codecs
4. keep serialization exclusively in `DataModelHelper` wire hooks
5. run exactly one reader task per connection, treating receive timeouts as idle
   ticks and an empty read (`b""`) or transport error as connection loss
6. resolve correlated replies via futures keyed by tx_id
7. configure tx_id injection and extraction as a **required** pair at construction
   (no default), with overwrite (re-stamp) injector semantics; register the future
   before writing the frame; support N concurrent in-flight requests with
   out-of-order reply resolution
8. expose unsolicited frames as an async iterator with a bounded, drop-oldest
   queue — the reader task never blocks on queue capacity
9. return `SocketTransactResult` / `SocketTransactResultModel` from every
   `request*` call — never raise from those methods
10. never let model parsing change `success`
11. cancel all pending futures and the reader task on disconnect
12. add zero external runtime dependencies (stdlib only)
