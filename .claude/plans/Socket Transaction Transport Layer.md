---
plan: SocketTransactionTransportLayer
scope: project
status: aligned
last_updated: 2026-07-03
semver: 0.1.1
author: Nicholas Bergantz
---

# Concept Plan: Socket Transaction Transport Layer

> **Alignment note (2026-07-03).** This plan's original draft was truncated and
> described a **thread-driven** recv model. It has been rewritten **asyncio-native**
> to match the repo's `foundation_abc.PeripheralByteTransport` constraint (fully
> async, never block the event loop). The binding contract is
> [.claude/specs/socketTransact.md](../specs/socketTransact.md); the execution
> breakdown is in `.claude/action-plan/` (chunks 05, 08, 09, 10). This file is the
> concept narrative only.

## Overview

The socket subsystem provides a **bidirectional, pluggable stream-transport stack**
that supports:

- raw byte transport (asyncio TCP)
- string tokenization (delimiter-based framing)
- binary framing (length-prefixed codec)
- transactional routing (tx_id correlation)

It is designed to be:

- transport-agnostic at upper layers
- codec-pluggable at the protocol layer
- fully asynchronous at runtime — one reader task per connection, no threads

---

## Core Design Philosophy

### 1. Composition over inheritance

All socket behavior is composed:

- `SocketByteTransport` owns the connection (implements `PeripheralByteTransport`)
- codecs own framing; the router owns correlation; `SocketTransact` owns the
  public surface
- behavior extends via layering, not subclassing sockets

### 2. Dual-channel receive model

Every connection yields **two independent inbound channels**:

- correlated replies → resolve the awaiting request's `asyncio.Future`
- unsolicited frames → an async-iterator stream (bounded queue, backpressure)

These operate simultaneously and do not interfere. (The original draft's
`data_handler`/`string_handler` callback pair, recast as awaitables and streams.)

### 3. Layered protocol stacking

The architecture is explicitly layered:

```text
SocketTransact            # public facade — result objects, never raises
      │
Transaction Router        # tx_id ↔ future correlation, unsolicited stream
      │
Framing Codec             # DelimiterCodec / LengthPrefixedCodec
      │
SocketByteTransport       # PeripheralByteTransport over asyncio TCP
      │
asyncio streams
```

Each layer owns exactly one concern; framing never leaks into the transport, and
correlation never leaks into codecs.

### 4. Serialization is the wire bridge

Outbound models encode via `DataModelHelper.to_wire`; inbound frames decode via
`from_wire`. The socket stack defines **no serialization format of its own** — it
composes the same bridge the CLI stack uses for `run_*_with_model` (see the
umbrella spec
[transport_transaction_architecture.md](../specs/transport_transaction_architecture.md)).

### 5. Result objects on the transaction surface

`SocketTransact.request*` mirrors `CLITransact`: timeouts, connection loss, and
codec failures come back as `SocketTransactResult` (`success=False`, diagnostic in
`error`) — never as exceptions. Raw transport methods keep ABC raising semantics.

---

## Relationship to the process-transaction family

| process family | stream family |
| --- | --- |
| CLITransact (kernel) | SocketByteTransport (raw bytes) |
| Command Builders | Framing Codecs |
| Execution Policies | Router policies (timeout, correlation) |
| SSHTransact / RsyncTransact | SocketTransact |
| `CLITransactResult` | `SocketTransactResult` |

One design ethos, two connection lifetimes: one-shot subprocess vs long-lived
stream.

---

## Execution

Implementation is decomposed in `.claude/action-plan/`:

- **05-socket-byte-transport.md** — `SocketByteTransport`
- **08-socket-framing-codecs.md** — codec protocol + two codecs
- **09-socket-transaction-router.md** — reader task, futures, unsolicited stream
- **10-sockettransact.md** — client facade + result types
- **13-sockettransact-server.md** — server facade (concurrent inbound dispatch,
  tx_id-tagged replies, broadcast) + client↔server end-to-end proof
