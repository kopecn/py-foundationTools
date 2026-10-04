---
version: 1.0
type: behavioral-specification
name: threaded-socket-transport
purpose: Define raw, text-framed, binary-framed, client, and single-client server socket behavior.
scope: project
status: accepted
applies_to: src/foundation_tools/socket_transaction/
last_updated: 2026-09-12
semver: 1.0.0
author: Nicholas Bergantz
---

# Threaded Socket Transport

This specification refines the transport layer in [threadedSocketTransaction.md](threadedSocketTransaction.md).

## Common handler

`SocketHandler(logger, *, string_delimiter="\n", join_timeout=1.0)` SHALL own an attached `socket.socket` by composition. `join_timeout` SHALL be finite and positive. Each attachment SHALL receive a monotonically increasing integer connection epoch that is never reused by that handler.

Its public surface SHALL be:

```python
@property
def is_connected(self) -> bool: ...

@property
def string_delimiter(self) -> str: ...

def send(self, data: bytes) -> bool: ...
def send_string(self, data: str) -> bool: ...
def set_data_message_handler(self, handler: Callable[[bytes], None] | None) -> None: ...
def set_string_message_handler(self, handler: Callable[[str], None] | None) -> None: ...
def disconnect(self) -> None: ...
```

The delimiter SHALL be non-empty. `is_connected` SHALL report whether the current connection epoch owns an attached socket, under synchronization. Callback setters SHALL synchronize replacement, snapshot the selected callback, and invoke that snapshot after releasing all internal locks.

`send` SHALL snapshot the active socket and epoch under the state lock, serialize `sendall` calls under a distinct send lock, and return `True` only when all bytes were accepted by that same epoch. When disconnected it SHALL log a warning, drop the bytes, and return `False`. On `OSError` it SHALL log the error, conditionally detach only the captured epoch after releasing the send lock, and return `False`; it SHALL NOT propagate the socket error. `send_string` SHALL UTF-8 encode its argument without appending a delimiter and return the result of `send`.

The transport SHALL provide its composing facade these internal operations:

```python
def snapshot_active_epoch(self) -> int | None: ...
def send_for_epoch(self, epoch: int, data: bytes) -> EpochSendStatus: ...
def set_connection_observer(self, observer: ConnectionObserver | None) -> None: ...
```

`EpochSendStatus` is internal and SHALL distinguish `SENT`, `NOT_ACTIVE`, and `IO_FAILED`. `snapshot_active_epoch` SHALL read socket and epoch state atomically. `send_for_epoch` SHALL return `NOT_ACTIVE` without sending when `epoch` is no longer active; otherwise it and public `send` share serialization and error behavior. `ConnectionObserver` SHALL define synchronous `on_string_token(epoch, token)` and `on_epoch_closed(epoch, cause)` calls. The observer SHALL be installed before a facade exposes lifecycle operations, and its snapshot/replacement semantics SHALL match public callback setters. Observer calls SHALL execute outside all internal locks and MAY overlap a concurrent close; epoch identity makes either ordering safe. Facades SHALL query `snapshot_active_epoch` rather than infer current state from observer delivery.

## Receive dispatch

Attaching a connected socket SHALL atomically publish the socket, epoch, and role-specific peer state; reset per-connection text state; clear the stop signal; and only then start one daemon receive thread. The thread SHALL call `recv(4096)` until stopped, detached, closed by the peer, or failed by `OSError`.

Each non-empty chunk SHALL first be passed unchanged to the raw-data handler, if present. The same bytes SHALL then be decoded as one incremental UTF-8 stream using replacement for malformed sequences. Complete tokens SHALL be split on `string_delimiter`, delivered without the delimiter in arrival order, and the incomplete suffix SHALL remain buffered for the next chunk.

Raw-data and string-handler exceptions SHALL be logged and contained independently. A failing callback SHALL NOT prevent the other channel or later messages from being processed.

An empty `recv` or receive-side `OSError` SHALL conditionally detach only the socket epoch that observed it and invoke the close observer once for that epoch. A stale receive worker SHALL NOT clear or close a newer socket. The transport SHALL provide composing facades an internal observer of epoch-tagged string tokens and epoch closure. The closed event SHALL carry a human-readable cause and occur before that epoch can be forgotten. A token callback racing closure MAY observe either order, but it can mutate only matching-epoch transaction state and any responder it creates is bound to that epoch.

`SocketHandler` SHALL provide a protected `_process_received_chunk(epoch, data)` extension point. The default behavior is raw and text dispatch. A specialization MAY extend it but SHALL preserve the default channels unless its public contract says otherwise.

## Detachment and cleanup

Detachment SHALL be idempotent and conditional on epoch identity. It SHALL signal the epoch's stop event, atomically remove that socket from active state, notify the close observer once, attempt `shutdown(socket.SHUT_RDWR)`, close the socket, and join its receive thread for at most `join_timeout` when invoked from another thread. It SHALL never join while holding the state, send, callback, or transaction lock. Shutdown and close errors SHALL be suppressed. A still-alive daemon worker after the join bound SHALL be logged and SHALL have no route to a newer socket epoch.

After detachment, the stored socket, worker reference, incremental decoder state, and incomplete text token SHALL no longer belong to the handler. An incomplete code point or token SHALL be discarded rather than delivered on detachment. Process-exit cleanup and object finalization SHALL make the same best-effort detachment without raising.

## Client

`SocketHandlerClient(logger, *, string_delimiter="\n", join_timeout=1.0)` SHALL extend `SocketHandler` with:

```python
def connect(self, host: str, port: int, timeout: float | None = 1.0) -> None: ...
```

`connect` SHALL disconnect an incumbent connection before creating a new `AF_INET`, `SOCK_STREAM` socket. It SHALL apply the requested connection timeout, connect to `(host, port)`, restore blocking mode after success, and attach the socket. `None` SHALL select the operating system's default connection behavior. A numeric timeout SHALL be finite and strictly positive; invalid values SHALL raise `ValueError` before disconnecting an incumbent. A connection failure SHALL close the candidate socket and propagate the original `OSError` without disturbing an already completed disconnect.

## Single-client server

`SocketHandlerServer(logger, *, connection_admission_handler=None, string_delimiter="\n", join_timeout=1.0, accept_poll_interval=0.2)` SHALL extend `SocketHandler`. The admission handler, when present, has type `Callable[[tuple[str, int]], bool]`. `accept_poll_interval` SHALL be finite and positive. Every successful `listen` SHALL allocate a monotonically increasing listener epoch with its own stop signal.

Its additional public surface SHALL be:

```python
@property
def active_peer(self) -> tuple[str, int] | None: ...

@property
def is_listening(self) -> bool: ...

@property
def listening_address(self) -> tuple[str, int] | None: ...

def listen(self, port: int) -> None: ...
def wait_for_connection(self, timeout: float | None = None) -> bool: ...
def kick(self) -> None: ...
def stop(self) -> None: ...
```

`listen` SHALL create an `AF_INET`, `SOCK_STREAM` listener, enable `SO_REUSEADDR`, bind all local interfaces, begin listening, publish the actual `(host, port)` from `getsockname`, and start one daemon accept thread. The accept loop SHALL wake at least every `accept_poll_interval` so shutdown is observable. Calling `listen` while already listening SHALL log a warning and change nothing. Bind and listen errors SHALL close the candidate listener and propagate as `OSError`. `is_listening` SHALL reflect listener ownership; `listening_address` SHALL return the bound address while listening and `None` otherwise. A stopped instance SHALL be able to listen again with its retained configuration.

For each accepted connection, the server SHALL normalize the peer to `(host, port)` and invoke the admission handler on the accept thread. No handler means admit. A false return or raised exception means reject and close the challenger; exceptions SHALL be logged. Rejection SHALL NOT alter the incumbent. After accept and after admission, the worker SHALL revalidate its captured listener epoch. A stale worker SHALL close its candidate and SHALL NOT modify a stopped or restarted listener or a newer client epoch.

An admitted challenger SHALL first detach the incumbent. After that potentially blocking operation, final listener-epoch revalidation and publication of the challenger socket, new connection epoch, `active_peer`, and connection availability SHALL occur atomically in the same critical section used to retire a listener epoch. A stale worker SHALL close the challenger instead of publishing it. The receive worker SHALL start only after publication; attachment failure SHALL roll back all published client state. Peer closure and `kick` SHALL clear `active_peer` and connection availability only for the matching epoch. `kick` SHALL detach the active connection without stopping the listener. Inherited `disconnect` SHALL have the same active-client effect as `kick` and SHALL also leave the listener running.

`wait_for_connection` SHALL accept `None` or a finite non-negative timeout; invalid values SHALL raise `ValueError`, and zero SHALL perform an immediate state check. It SHALL implement level-triggered behavior: return `True` only if an active client epoch exists at the instant it returns, otherwise continue waiting until the optional deadline and return `False` on expiry. `stop` SHALL be idempotent, retire the listener epoch, signal its accept loop, close its listener, join its accept thread for at most `join_timeout`, kick the active client, clear peer and bound-address state, and leave no listener active. A still-alive stale daemon accept worker SHALL be logged and rendered unable to affect later epochs.

## Binary-framed client

`BinaryFramedSocketHandlerClient(logger, frame_decoder, *, string_delimiter="\n", join_timeout=1.0)` SHALL extend `SocketHandlerClient`. Its decoder has the contract `Callable[[bytes], tuple[object | None, bytes]]`, where the argument is the complete accumulated buffer and the second return value is the unconsumed suffix.

The specialization SHALL append every receive chunk to its binary buffer and call the decoder repeatedly until it returns `(None, unchanged_buffer)`. Each decoded frame SHALL be passed in order to the handler registered by `set_frame_handler(Callable[[object], None] | None)`.

A decoder exception or invalid result SHALL be treated as decoder failure: log the error, clear the binary buffer, and stop decoding that chunk without terminating reception. A valid remainder SHALL be a byte suffix of the input. Returning a frame SHALL strictly shorten the buffer. Returning no frame SHALL use the identical input as the remainder and terminate the loop; any changed no-frame remainder is invalid. Frame-handler exceptions SHALL be logged and contained; subsequent frames SHALL still be delivered. The binary buffer SHALL reset on every connection epoch.

## Conformance outcomes

- Raw chunks are delivered unchanged; split delimiters and UTF-8 code points reconstruct correctly; callback failures do not prevent later delivery.
- Concurrent sends do not interleave, peer EOF clears only its epoch, and reconnect starts with empty framing state.
- A failed client candidate is closed, and a successful connection uses a blocking socket after its connection timeout completes.
- Server bound address, admission, incumbent preservation on rejection, admitted replacement, level-triggered wait, kick, stop, and restart report state consistently.
- Binary partial and multiple frames preserve order; malformed or non-progressing decoder output resets only binary framing state and does not kill reception.
