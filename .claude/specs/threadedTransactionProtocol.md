---
version: 1.0
type: behavioral-specification
name: threaded-transaction-protocol
purpose: Define transaction frames, wire codecs, pending state, synchronization, and routing.
scope: project
status: accepted
applies_to: src/foundation_tools/socket_transaction/
last_updated: 2026-09-12
semver: 1.0.0
author: Nicholas Bergantz
---

# Threaded Transaction Protocol

This specification refines the transaction protocol layer in [threadedSocketTransaction.md](threadedSocketTransaction.md). It has no socket dependency.

## Transaction frame

`TransactionFrame` SHALL contain:

```python
tx_id: int
msg_type: str
code: int
payload: bytes | str | dict[str, object] | None = None
```

Positive identifiers represent peer-correlated transactions. `-1` is the defined broadcast identifier; any negative identifier on an `evt` frame SHALL be treated as unsolicited broadcast traffic. `msg_type` SHALL be a non-empty string. The protocol reserves `ack`, `res`, `evt`, and `err` for control and response routing; other non-empty message types identify application-defined requests.

## Codec protocol

`TransactionCodec` SHALL be a structural typing protocol:

```python
@property
def delimiter(self) -> str: ...

def encode(
    self,
    tx_id: int,
    msg_type: str,
    code: int,
    payload: DataModelHelper | bytes | str | None = None,
) -> bytes: ...

def decode(self, raw: bytes | str) -> TransactionFrame: ...
```

`delimiter` SHALL be non-empty. `encode` SHALL emit one complete delimiter-terminated wire message. `decode` SHALL accept that message with or without its trailing delimiter and raise `ValueError` for malformed syntax or identifier/code values that `int` cannot convert. Boolean values SHALL be rejected as identifiers and codes.

## JSON codec

`JsonTransactionCodec.delimiter` SHALL be `"\n"`. It SHALL encode a UTF-8 JSON object followed by `b"\n"`. `tx_id`, `msg_type`, and `code` are required. `payload` SHALL be omitted for `None`, shall be a model's `to_dict()` result for `DataModelHelper`, shall be a UTF-8 string decoded with replacement for bytes, and shall be unchanged for strings. This bytes conversion is intentionally textual and lossy; arbitrary binary data belongs on the raw or binary-framed transport APIs.

Decoding SHALL require an object containing all three required fields, require a non-empty string `msg_type`, convert `tx_id` and `code` with `int`, copy an optional string, object, or null payload, and raise `ValueError` for malformed JSON, the wrong top-level or payload shape, missing required fields, or failed field validation.

## Angle-bracket codec

`AngleBracketTransactionCodec.delimiter` SHALL be `"\n"`. It SHALL encode UTF-8 text as `<tx_id,msg_type,code[,payload]>\n`. `None` omits the fourth field. `DataModelHelper` SHALL use its `to_bytes()` value decoded as UTF-8 with replacement; bytes use the same decoding; strings pass unchanged. An encoded message type containing comma, carriage return, or newline, or a textual payload containing carriage return or newline, SHALL raise `ValueError` rather than produce an ambiguous or additional wire message. Its bytes conversion is intentionally textual and lossy.

Decoding SHALL strip surrounding whitespace, require `<` and `>`, split the inner text at no more than the first three commas, require at least three fields, require a non-empty second field, convert the first and third fields with `int`, and preserve the entire fourth field as a string so payload commas survive. Invalid structure or field validation SHALL raise `ValueError`.

## Pending transaction

`PendingTransaction` is internal mutable state. It SHALL contain its connection epoch, `tx_id`, independent `threading.Event` instances named `ack_event` and `done_event`, current ACK and completion statuses, `acked: bool`, `result: TransactionFrame | None`, separate ACK and completion diagnostics, and an arrival-ordered list of transaction-specific `events`. It SHALL NOT be a package export.

`SendStatus` SHALL define `SENT`, `NOT_CONNECTED`, and `FAILED`. `AckStatus` SHALL define `NOT_REQUESTED`, `ACKNOWLEDGED`, `REJECTED`, `TIMED_OUT`, and `CONNECTION_CLOSED`. `CompletionStatus` SHALL define `NOT_REQUESTED`, `RESULT`, `ERROR`, `TIMED_OUT`, and `CONNECTION_CLOSED`.

`TransactionOutcome` SHALL be immutable and contain `tx_id`, `send_status`, `ack_status`, `completion_status`, `result: TransactionFrame | None`, `ack_error: str | None`, `completion_error: str | None`, and an immutable arrival-ordered tuple of transaction events. Its derived `success` property SHALL be true exactly when the send is `SENT` and every requested stage has its success status; an unrequested stage is neutral. This is the public transaction truth.

## Transaction core

`TransactionCore(logger, *, first_tx_id=1, tx_id_step=1)` is internal, non-exported transaction state. Both numeric parameters SHALL be positive integers. The first generated identifier SHALL equal `first_tx_id`; subsequent identifiers SHALL increase by `tx_id_step` under the transaction lock.

The internal state operations SHALL be:

```python
def next_tx_id(self) -> int: ...
def register(self, epoch: int, tx_id: int) -> PendingTransaction: ...
def discard(self, tx_id: int) -> None: ...
def wait_ack(self, tx_id: int, timeout: float | None = None) -> AckStatus | None: ...
def wait_completion(self, tx_id: int, timeout: float | None = None) -> CompletionStatus | None: ...
def finalize_outcome(
    self,
    tx_id: int,
    send_status: SendStatus,
    *,
    ack_requested: bool,
    completion_requested: bool,
) -> TransactionOutcome | None: ...
def route(self, epoch: int, frame: TransactionFrame) -> None: ...
def fail_epoch(self, epoch: int, error: str) -> None: ...
def set_broadcast_event_handler(
    self, handler: Callable[[TransactionFrame], None] | None
) -> None: ...
def set_inbound_transaction_handler(
    self, handler: Callable[[int, TransactionFrame], None] | None
) -> None: ...
```

`register` SHALL reject an existing identifier with `RuntimeError`; it SHALL never replace a waiter. `discard` SHALL be idempotent. Each wait SHALL accept `None` or a finite non-negative timeout and raise `ValueError` otherwise; zero performs an immediate check. Each wait SHALL return `None` for an unknown identifier. After its event wait returns, the operation SHALL acquire the transaction lock and atomically return an already-settled stage or settle an unresolved stage as `TIMED_OUT`. A frame racing the deadline therefore linearizes wholly before or after timeout settlement, and a later frame SHALL NOT overwrite `TIMED_OUT`.

`finalize_outcome` SHALL acquire the transaction lock once, snapshot stage statuses, diagnostics, result, and events into an immutable `TransactionOutcome`, map unrequested stages to `NOT_REQUESTED`, remove the pending entry, and return the outcome. It SHALL return `None` for an unknown identifier. No facade SHALL read mutable pending fields directly. Once finalization removes the entry, a later control frame follows orphan-frame routing.

## Routing

Routing SHALL select exactly one outcome:

| condition | outcome |
| --- | --- |
| `msg_type == "evt"` and `tx_id < 0` | invoke the broadcast handler, if present; do not consult pending state |
| `msg_type` is `ack`, `res`, `err`, or non-broadcast `evt` and no pending entry exists for `(epoch, tx_id)` | log and discard the orphan control frame |
| no pending entry exists for `(epoch, tx_id)` | invoke the inbound transaction handler, if present, with epoch and frame |
| `msg_type == "ack"` and `code == 0` | set `acked=True`; signal `ack_event` |
| `msg_type == "ack"` and `code != 0` | store `ack code <code>: <payload>` when payload exists, otherwise `ack code <code>`; signal both events |
| `msg_type == "res"` | store the frame as `result`; signal `done_event` |
| `msg_type == "evt"` | append the frame to `events`; do not signal completion |
| `msg_type == "err"` | store `str(payload)` when present, otherwise `error code <code>`; signal `done_event` |
| any other type | invoke the inbound transaction handler, if present, with epoch and frame |

State mutation SHALL finish under the transaction lock before any callback is invoked. Broadcast and inbound-handler exceptions SHALL be logged and contained.

ACK and completion SHALL settle independently. The first ACK, ACK timeout, or `fail_epoch` SHALL settle ACK status. The first failed ACK, `res`, `err`, completion timeout, or `fail_epoch` SHALL settle completion status. A failed ACK SHALL settle completion as `ERROR` only while completion remains unresolved. `fail_epoch` SHALL settle each still-unresolved stage as `CONNECTION_CLOSED` without overwriting a stage already settled by another event. Transaction events SHALL be appended only while completion is unresolved. Every losing ACK, terminal frame, or late event SHALL be logged and ignored. Failure settlement SHALL signal the corresponding event, and connection closure SHALL wake both waits. Entries remain registered until their owning sender discards them.

## Identifier-space rule

Peers that may initiate transactions simultaneously SHALL use disjoint positive identifier sequences. The standard client SHALL allocate odd identifiers beginning at 1; the standard server SHALL allocate even identifiers beginning at 2. Custom peers that do not honor this rule cannot safely initiate simultaneously on the same connection. This preserves integer IDs and makes replies unambiguous without adding endpoint identity to either wire codec.

## Conformance outcomes

- Both codecs preserve their declared textual payload behavior and reject malformed structure or fields consistently.
- ID allocation, registration, discard, routing, event ordering, terminal precedence, and epoch failure remain coherent under concurrent callers.
- Simultaneous standard client/server initiation cannot allocate the same transaction identifier.
