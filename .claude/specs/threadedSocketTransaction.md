---
version: 1.0
type: architecture-specification
name: threaded-socket-transaction
purpose: Define the architecture and shared invariants of the synchronous threaded socket transaction family.
scope: project
status: accepted
applies_to: src/foundation_tools/socket_transaction/
last_updated: 2026-09-12
semver: 1.0.0
author: Nicholas Bergantz
---

# Threaded Socket Transaction Architecture

## Purpose

The socket transaction family SHALL provide synchronous IPv4 TCP client and server APIs built directly on `socket` and `threading`. It SHALL NOT use `asyncio`, coroutine public methods, event-loop primitives, async iterators, async context managers, or the asynchronous `PeripheralByteTransport` contract. Standard-library thread synchronization, queues, iterators, and synchronous context managers remain permitted.

The family SHALL support raw-byte callbacks, delimiter-framed text callbacks, pluggable binary framing, pluggable transaction serialization, ACK and result waits, transaction-scoped events, broadcasts, remote-initiated transactions, and concurrent callers.

## Layer ownership

```text
Application
    |
    v
TransactingSocketHandlerClient / TransactingSocketHandlerServer
    |-- TransactionCore
    |-- TransactionCodec
    `-- SocketHandlerClient / SocketHandlerServer
            |
            v
        SocketHandler
            |
            v
        socket.socket
```

- The transport layer owns sockets, connection lifecycle, sending, receive and accept threads, and raw/text stream dispatch. Its contract is [threadedSocketTransport.md](threadedSocketTransport.md).
- The transaction protocol layer owns frames, wire codecs, identifiers, pending state, and routing. Its contract is [threadedTransactionProtocol.md](threadedTransactionProtocol.md).
- The transacting facade owns composition of transport and protocol behavior. Its contract is [transactingSocketHandlers.md](transactingSocketHandlers.md).
- Binary framing is a transport specialization parallel to, not embedded in, the transaction layer.
- No layer SHALL subclass `socket.socket`.

## Public surface

The package SHALL export these public types:

- `SocketHandler`
- `SocketHandlerClient`
- `SocketHandlerServer`
- `BinaryFramedSocketHandlerClient`
- `TransactionFrame`
- `TransactionCodec`
- `JsonTransactionCodec`
- `AngleBracketTransactionCodec`
- `SendStatus`
- `AckStatus`
- `CompletionStatus`
- `TransactionOutcome`
- `InboundTransaction`
- `TransactingSocketHandlerClient`
- `TransactingSocketHandlerServer`

The package SHALL expose no asynchronous socket facade or compatibility adapter. The threaded socket family SHALL remain independent of asynchronous transport ABCs.

## Concurrency model

- Each attached connection SHALL have at most one daemon receive thread.
- A listening server SHALL have at most one daemon accept thread in addition to the active connection's receive thread.
- Socket attachment and detachment SHALL be synchronized independently from outbound sending and transaction state.
- Complete outbound wire messages SHALL be serialized so concurrent callers cannot interleave bytes.
- Transaction mutation SHALL be protected by a transaction lock; blocking socket calls, event waits, and application callbacks SHALL execute without that lock held.
- Application callbacks execute in the background thread that encounters the event, with no internal socket, send, callback, codec, or transaction lock held. Every callback boundary SHALL contain and log `Exception` without terminating its transport thread.
- Callbacks SHALL return cooperatively and SHALL NOT perform a blocking `send_transaction` call on a receive thread. An inbound callback MAY use its epoch-bound non-waiting responder.
- Every internal lifecycle join SHALL be bounded. A worker SHALL never join itself. If application code prevents a daemon worker from returning before the bound, the handler SHALL log the timeout and relinquish ownership; it cannot forcibly terminate that code.

## Stream and protocol invariants

- TCP SHALL be treated as a byte stream; a receive chunk is not a message boundary.
- Text and binary reassembly state belongs to one connection epoch and SHALL be cleared when that socket is detached or replaced.
- Transaction serialization belongs only to the selected `TransactionCodec`.
- ACK receipt and final completion are independent synchronization stages.
- Every attached socket SHALL belong to a unique, monotonically increasing connection epoch. Receive, send, close, peer metadata, transaction registration, and reply operations SHALL affect only the epoch that originated them.
- A transaction registration SHALL exist before its bytes can be sent and SHALL be removed on every exit path.
- Connection loss or explicit detachment SHALL wake all pending transaction waiters with terminal error state.
- A server SHALL maintain at most one active client. An admitted challenger replaces the incumbent; a rejected challenger does not affect it.

## Dependency policy

The implementation SHALL use only the Python standard library and existing project types. Every concrete handler and transaction core SHALL receive a caller-supplied `logging.Logger`-compatible object and SHALL NOT instantiate or fetch a logger internally.

## Conformance outcomes

- The package has no event-loop dependency or asynchronous public socket API.
- Concurrent sends arrive as complete, non-interleaved wire messages.
- Explicit shutdown, peer closure, and connection replacement make the closed epoch inaccessible and release its worker under cooperative callbacks; callback and codec failures are contained without closing the epoch.
- Client-to-server and server-to-client transactions work on one connection, including simultaneous initiation with distinct identifier spaces.
