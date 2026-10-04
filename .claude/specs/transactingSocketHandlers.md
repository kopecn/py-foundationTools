---
version: 1.0
type: behavioral-specification
name: transacting-socket-handlers
purpose: Define synchronous client and server facades that compose threaded transport with transaction semantics.
scope: project
status: accepted
applies_to: src/foundation_tools/socket_transaction/
last_updated: 2026-09-12
semver: 1.0.0
author: Nicholas Bergantz
---

# Transacting Socket Handlers

This specification composes [threadedSocketTransport.md](threadedSocketTransport.md) and [threadedTransactionProtocol.md](threadedTransactionProtocol.md).

## Composition and roles

`TransactingSocketHandlerClient(logger, codec, *, join_timeout=1.0)` SHALL contain a `SocketHandlerClient` and a `TransactionCore` configured with the standard odd client identifier sequence. It SHALL expose the contained transport's `is_connected`, `connect(host, port, timeout=1.0)`, and `disconnect()` behavior.

`TransactingSocketHandlerServer(logger, codec, *, connection_admission_handler=None, join_timeout=1.0, accept_poll_interval=0.2)` SHALL contain a `SocketHandlerServer` and a core configured with the standard even server identifier sequence. It SHALL expose `is_connected`, `active_peer`, `is_listening`, `listening_address`, `listen(port)`, `wait_for_connection(timeout=None)`, `disconnect()`, `kick()`, and `stop()` with the contained server's behavior.

Each facade SHALL configure its contained socket handler from the injected codec's `delimiter`, serialize every codec `encode` and `decode` call under one facade-owned codec lock, and register as the transport's internal epoch observer. No socket, transaction, observer, or application-callback lock SHALL be held while waiting for the codec lock. The codec lock SHALL be released before routing a decoded frame or invoking any application callback, allowing an inbound responder to encode without reentrancy deadlock. A facade SHALL NOT duplicate socket ownership or require an injected codec to be thread-safe.

Both roles SHALL expose:

```python
def send_transaction(
    self,
    msg_type: str,
    code: int,
    payload: DataModelHelper | bytes | str | None = None,
    wait_ack: bool = True,
    wait_result: bool = False,
    timeout: float | None = None,
) -> TransactionOutcome: ...

def set_string_message_handler(self, handler: Callable[[str], None] | None) -> None: ...
def set_broadcast_event_handler(
    self, handler: Callable[[TransactionFrame], None] | None
) -> None: ...
def set_inbound_transaction_handler(
    self, handler: Callable[[InboundTransaction], None] | None
) -> None: ...

def send_broadcast(
    self, payload: DataModelHelper | bytes | str | None = None, code: int = 0
) -> bool: ...
```

`InboundTransaction` SHALL expose the decoded `frame` and an epoch-bound `reply(msg_type, code, payload=None) -> bool` operation. `reply` SHALL accept `ack`, `res`, `err`, or transaction-scoped `evt`, encode with the inbound identifier, and use `send_for_epoch`; it SHALL return `True` only for `EpochSendStatus.SENT` and `False` rather than send to a replacement connection. The callback MAY retain the value, but its responder becomes inert after the originating epoch closes.

`reply` SHALL raise `ValueError` before encoding when `msg_type` is not one of `ack`, `res`, `err`, or `evt`.

`send_broadcast` SHALL encode `tx_id=-1`, `msg_type="evt"`, and the supplied code/payload without registering pending state. On a single-client server it targets only the active client.

## Receive pipeline

For each epoch-tagged complete string token, the facade SHALL attempt codec decoding and route a decoded frame through `TransactionCore` for that same epoch before invoking the optional application string handler with the original token. If decoding raises `ValueError`, the facade SHALL log the failure, skip transaction routing, and still invoke the application string handler. Decode and user-handler failures SHALL NOT escape the receive thread. On an inbound route, the facade SHALL construct the epoch-bound `InboundTransaction` passed to the user callback.

## Synchronous transaction operation

`send_transaction` SHALL perform this ordering:

1. Allocate an identifier.
2. Atomically snapshot the active connection epoch; if absent, return `NOT_CONNECTED` without registering.
3. Register pending state for that epoch.
4. Encode the complete wire message.
5. Send it only if the registered connection epoch remains active.
6. If requested, wait for ACK for at most `timeout`.
7. If requested, wait independently for final completion for at most `timeout`.
8. Atomically snapshot the immutable outcome and remove the pending entry; use idempotent discard on an exception path.

Every call SHALL consume an identifier, including while disconnected. The facade SHALL snapshot an active epoch, register to that epoch, and use `send_for_epoch`, so replacement cannot move a transaction to another peer. Registration SHALL precede sending so an immediate peer response cannot outrun correlation. Encode exceptions SHALL propagate after cleanup because they are caller or codec errors. Lack of an active epoch SHALL return a directly constructed, unregistered outcome with `send_status=NOT_CONNECTED`; every path that registers pending state SHALL construct its outcome through `TransactionCore.finalize_outcome`. `EpochSendStatus.NOT_ACTIVE` or `IO_FAILED` SHALL return `send_status=FAILED`. A failed send SHALL not wait, and requested ACK/completion stages SHALL be `CONNECTION_CLOSED` while unrequested stages remain `NOT_REQUESTED`. An epoch-close settlement recorded synchronously during the send SHALL remain authoritative.

`timeout` SHALL be `None` or a finite non-negative number; invalid values SHALL raise `ValueError` before allocating an identifier, and zero SHALL perform immediate event checks. An ACK timeout SHALL be logged and SHALL NOT prevent a separately requested result wait. `timeout` applies once to each selected wait, so selecting both may block for no more than approximately twice that duration plus scheduling overhead. `None` means an unbounded public wait, subject to epoch teardown signaling both events.

The returned `TransactionOutcome` SHALL distinguish sent, not-connected, and send-failed states; ACK success, rejection, timeout, and connection loss; final result, protocol error, timeout, and connection loss; and not-requested stages. It SHALL be constructed through the core's atomic finalization operation and retain all transaction events received before cleanup. The result field SHALL be populated only when completion status is `RESULT`. ACK and completion diagnostics SHALL independently explain each failed requested stage.

Status mapping SHALL be:

- An unrequested stage is `NOT_REQUESTED`, regardless of frames the caller did not wait for.
- A requested ACK stage is `ACKNOWLEDGED`, `REJECTED`, `TIMED_OUT`, or `CONNECTION_CLOSED` according to its first decisive condition.
- A requested completion stage is `RESULT`, `ERROR`, `TIMED_OUT`, or `CONNECTION_CLOSED` according to its first terminal condition. A failed ACK is `ERROR` when completion was requested.
- A send status other than `SENT` SHALL supply the same non-empty explanation in each requested stage's diagnostic; both diagnostics MAY remain `None` for a failed fire-and-forget send because `send_status` is independently authoritative.
- `ack_error` SHALL be non-empty exactly when a requested ACK stage is not `ACKNOWLEDGED`.
- `completion_error` SHALL be non-empty exactly when a requested completion stage is not `RESULT`.

## Lifecycle coupling

Client `connect` and server client-attachment SHALL begin receive routing for the new socket epoch. Explicit disconnect, server kick/stop, admitted-client replacement, peer EOF, and socket failure SHALL cause the transport close observer to call `TransactionCore.fail_epoch` for exactly that epoch. No unresolved transaction from an old epoch SHALL survive into a new connection or be failed by a later epoch's teardown. Terminal old-epoch entries MAY remain until their owning senders finalize them, but they cannot route frames or affect another epoch.

The server facade SHALL preserve the single-active-client semantics of `SocketHandlerServer`. It SHALL be able to initiate a transaction only while an active client is attached. The client facade SHALL preserve the reconnect-by-replacement behavior of `SocketHandlerClient`.

## Public error boundary

- Constructor validation, codec encoding, and client connect/server listen failures SHALL raise their original `ValueError` or `OSError` category.
- Established-connection send failures SHALL be logged and represented by `False` for raw/broadcast/reply sends or by `TransactionOutcome` for transactions.
- Decode and application-callback failures on inbound data SHALL be logged and contained.

## Conformance outcomes

- Immediate replies cannot beat transaction registration; connection replacement cannot redirect a transaction or reply; and every operation discards its pending entry.
- ACK, result, error, event, broadcast, malformed-token, timeout, and disconnect behavior is identical for client and server roles.
- A remote-initiated callback can send frames with the inbound identifier, and its responder cannot target a replacement peer.
