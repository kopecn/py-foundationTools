---
human_ask: >
  the socket handler in src/foundation_tools/socket_transaction was built out with asyncio and this was a break from my expectation.  I was expecting to have this built out from threading and import socket this way we would have much more fidelity to refine the socket handling characteristics.  please author a rip and tear plan to unfuck this code section.  it should cover both client and server socket handling.  be very brief, only put in a few lines to scaffold under goal and I will be authoring the rest.
goal: >
  Replace the asyncio-based socket transaction client and server with threading and the standard socket module.
last_updated: 2026-09-13
semver: 0.0.2
author: Nicholas Bergantz
status: active
---

# Plan 25 - Threaded Socket Transaction

## Goal

Replace the `asyncio`-based client and server in `src/foundation_tools/socket_transaction` with implementations built directly on `threading` and the standard `socket` module, providing explicit control over socket handling characteristics.

## Delegated execution plans

The original build-out was decomposed into numbered chunks `01`–`16`, all completed, tracked in the archived [historical execution overview](00-overview.md). A subsequent post-audit's corrective chunks `17`–`25` are tracked in the active [corrective execution overview](00-corrective-overview.md). The accepted behavioral contracts live in `.claude/specs/threadedSocketTransaction.md` and its linked sibling specs; this file remains the original source scaffold. Chunk `16` ([25-threaded-socket-transaction/16-rip-and-tear-cleanup.md](16-rip-and-tear-cleanup.md)) was the final breaking public-surface cutover: it exported the accepted threaded surface and removed the superseded asyncio implementation described in the Body below. Read the executed chunk set, not this scaffold's Body, for current behavior.

## Body

### Socket & Transaction Framework — Specification

### 1. Purpose

Provide a layered TCP communication framework supporting:

- IPv4 TCP client and server connections.
- Threaded background reception.
- Raw-byte and delimiter-based string messaging.
- Pluggable binary frame decoding.
- Pluggable transaction wire formats.
- Request/response transactions with optional ACKs.
- Asynchronous events and broadcast events.
- Remote-initiated transactions.
- Thread-safe tracking of multiple concurrent transactions.
- Payloads represented as raw bytes, strings, or data-model objects.
- Explicit dependency injection of the logging facility.

The framework is composed in layers so that socket transport, framing, and transaction semantics remain independently replaceable.

### 2. Architectural Layers

The intended layering is:

```text
                    ┌──────────────────────────────┐
                    │ Transaction Protocol Layer   │
                    │                              │
                    │ TransactingSocketHandler     │
                    │ Client / Server              │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │ TCP Socket Layer             │
                    │                              │
                    │ SocketHandlerClient/Server   │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │ Base Socket Layer             │
                    │                              │
                    │ SocketHandler                │
                    └──────────────────────────────┘
```

A separate binary-framing specialization exists alongside the transaction layer:

```text
SocketHandler
     │
     └── SocketHandlerClient
              │
              └── BinaryFramedSocketHandlerClient
```

Transaction framing is delegated to a `TransactionCodec`:

```text
TransactingSocketHandler
          │
          ├── TransactionCore
          │
          └── TransactionCodec
                   ├── JSON codec
                   └── Angle-bracket codec
```

### 3. Core Data Model

#### 3.1 TransactionFrame

A decoded transaction is represented by a transaction frame containing:

| Field | Type | Meaning |
| --- | --- | --- |
| `tx_id` | integer | Transaction identifier |
| `msg_type` | string | Transaction message category |
| `code` | integer | Status/result code |
| `payload` | bytes/string/dictionary/null | Optional decoded payload |

##### Transaction ID

- Positive IDs identify locally initiated transactions.
- `-1` represents a broadcast/unsolicited event.
- An otherwise unknown transaction ID represents a transaction initiated by the remote peer.

##### Message types

The protocol recognizes:

- `ack` — acknowledgement.
- `res` — successful/normal transaction result.
- `evt` — asynchronous event.
- `err` — transaction error.

### 4. TransactionCodec

`TransactionCodec` defines the wire-format abstraction.

Every codec must implement:

#### Encode

```text
encode(tx_id, msg_type, code, payload) → bytes
```

##### Requirements:

- Produce the complete wire representation of one transaction.
- Include whatever delimiter/framing is required by the wire protocol.

Support:

- Data-model payloads.
- Raw bytes.
- Strings.
- No payload.
- `tx_id = -1` is valid for broadcast events.

#### Decode

```text
decode(raw) → TransactionFrame
```

##### Requirements:

- Accept raw bytes or a string as defined by the codec.
- Return a fully populated `TransactionFrame`.
- Reject malformed input with `ValueError`.

The codec is responsible for all wire-format-specific serialization and parsing.

### 5. JSON Transaction Codec

The JSON codec represents each transaction as a JSON object terminated by a newline.

#### 5.1 Wire representation

Required fields:

```text
{
    "tx_id": integer,
    "msg_type": string,
    "code": integer
}
```

The optional payload is represented as:

```text
"payload": <value>
```

The complete JSON object is followed by:

```text
\n
```

UTF-8 encoding is used on the wire.

#### 5.2 Payload encoding

##### Data-model object

Serialized using its dictionary representation.

Conceptually:

```text
DataModelHelper → to_dict() → JSON payload
```

##### Bytes

Decoded as UTF-8 with replacement for invalid byte sequences.

##### String

Passed as a JSON string value.

##### None

The payload field is omitted entirely.

#### 5.3 Decoding

The codec:

- Parses the received content as JSON.
- Extracts `tx_id`.
- Extracts `msg_type`.
- Extracts `code`.
- Extracts optional payload.
- Constructs a `TransactionFrame`.

Defaults currently implied by the implementation are:

```text
tx_id   = -1 if missing
msg_type = "" if missing
code    = 0 if missing
payload = null if missing
```

- Malformed JSON must produce `ValueError`.
- Numeric fields must be convertible to integers.

### 6. Angle-Bracket Transaction Codec

The angle-bracket codec represents transactions as:

```text
<tx_id,msg_type,code[,payload]>
```

followed by a newline.

#### 6.1 No-payload form

```text
<tx_id,msg_type,code>\n
```

#### 6.2 Payload form

```text
<tx_id,msg_type,code,payload>\n
```

The payload is treated as textual UTF-8 content.

#### 6.3 Payload encoding

##### Data-model object

The object's byte representation is decoded as UTF-8 with replacement.

##### Bytes

Decoded as UTF-8 with replacement.

##### String/other supported value

Converted to string representation.

##### None

No payload field is emitted.

#### 6.4 Decoding

The decoder must:

- Remove surrounding whitespace.
- Require the message to begin with `<`.
- Require the message to end with `>`.
- Remove the outer delimiters.
- Split into a maximum of four comma-separated fields.

Parse:

- field 1 → `tx_id`
- field 2 → `msg_type`
- field 3 → `code`
- field 4 → optional payload
- Return a `TransactionFrame`.

- At least three fields are required.
- Invalid transaction ID or status code must produce `ValueError`.

The fourth field is treated as the entire remaining payload, allowing commas within the payload.

### 7. SocketHandler

`SocketHandler` is the common transport abstraction.

It must use composition rather than subclassing `socket.socket`.

The underlying socket is owned internally and may be attached or detached during the handler's lifetime.

#### 7.1 Dependencies

- The handler requires an externally supplied logger.
- The handler must not create its own logger.

Default string delimiter:

```text
\n
```

#### 7.2 State

The handler maintains:

- Current socket, or no socket.
- Socket synchronization lock.
- Receive thread.
- Receive-stop event.
- String accumulation buffer.
- Optional raw-data callback.
- Optional string-token callback.

#### 7.3 Connection state

- `is_connected` is true when a socket is currently attached.
- Access to the socket state is synchronized.

### 8. Raw Send API

#### 8.1 send(bytes)

The handler sends raw bytes over the active connection.

If no connection exists:

- Do not raise an exception.
- Log a warning.
- Drop the data.

If sending fails with an OS-level socket error:

- Log the error.
- Do not propagate the socket exception through the send API.

Successful sends may be debug logged.

#### 8.2 send_string(string)

The string is encoded as UTF-8 and passed to the raw send operation.

### 9. Receive Processing

Reception occurs on a background daemon thread.

The socket is read in chunks with a nominal receive buffer size of:

```text
4096 bytes
```

Each received chunk is passed to the dispatch pipeline.

#### 9.1 Raw-data handler

- If registered, the raw-data handler receives each socket receive chunk exactly as received.
- It is not guaranteed to correspond to a logical protocol message.

Exceptions raised by the handler:

- Must not terminate the receive thread.
- Must be logged.

#### 9.2 String handler

If registered:

- Decode the chunk as UTF-8.
- Append it to the accumulated string buffer.
- Split the accumulated data on the configured delimiter.
- Preserve the final incomplete fragment.
- Invoke the string callback once for every complete token.

Example:

```text
chunk 1: "abc\n12"
chunk 2: "3\nxyz\n"
Results:
token: "abc"
token: "123"
token: "xyz"
```

- The trailing fragment is retained between receive calls.
- String-handler exceptions must not terminate the receive thread.

### 10. Socket Attachment

A subclass obtains a connected socket and attaches it to the handler.

Attachment must:

- Replace the current socket.
- Reset the string receive buffer.
- Clear the receive-stop event.
- Create a daemon receive thread.
- Start the receive thread.

The receive thread operates until:

- The handler is detached.
- The socket disappears.
- The peer closes the connection.
- A receive error occurs.

### 11. Socket Detachment

Detachment must be:

- Idempotent.
- Safe when no socket is connected.

It must:

- Signal the receive thread to stop.
- Atomically remove the active socket reference.
- Shut down the socket.
- Close the socket.
- Wait for the receive thread to finish, with a bounded timeout.
- Clear the stored receive-thread reference.

Socket shutdown/close errors are ignored.

### 12. Peer Closure

When the peer closes its TCP connection:

- The active socket is cleared.
- The peer-close hook is invoked.
- Subclasses may override the hook to update connection-specific state.
- The peer closure must not cause an uncontrolled receive-thread exception.

### 13. Cleanup

The socket handler registers an exit cleanup operation.

At process exit, an active socket is detached and closed.

The object destructor also makes a best-effort attempt to close any remaining socket.

### 14. SocketHandlerClient

Provides IPv4 TCP client behavior on top of `SocketHandler`.

#### 14.1 connect

##### Inputs:

- host
- port
- timeout

##### Default timeout:

1 second

##### Behavior:

- If already connected, disconnect first.
- Create an IPv4 TCP socket.
- Apply the requested connection timeout.
- Connect to the specified host and port.
- Close and discard the socket if connection fails.
- Propagate the connection error.
- Restore the socket to blocking mode after successful connection.
- Attach the socket to the base handler.
- Start background reception.
- `None` timeout means use the operating system's default behavior.

### 15. SocketHandlerServer

Provides an IPv4 TCP listening endpoint.

The server supports one active client connection at a time.

#### 15.1 Construction

##### Inputs:

- Logger.
- Optional connection admission callback.
- Optional string delimiter.

#### 15.2 Connection admission

The optional callback receives:

```text
(host, port)
```

and returns:

```text
True  → accept
False → reject
```

If the callback:

- Is absent → admit all connections.
- Raises an exception → reject the connection and log the error.
- Returns false → close the challenger.

Rejecting a challenger must not disconnect the current active client.

### 16. Server Listen

`listen(port)` must:

- Create an IPv4 TCP socket.
- Enable address reuse.
- Bind to all local interfaces.
- Begin listening.
- Start an accept daemon thread.
- Periodically wake the accept loop so shutdown can be detected.

- Calling `listen` while already listening does nothing except log a warning.
- Failure to bind/listen propagates as an OS-level error.

### 17. Server Accept Behavior

For each incoming connection:

- Accept the connection.
- Normalize the peer address to `(host, port)`.
- Run the admission callback if configured.
- Reject and close the challenger if admission fails.

If an incumbent client exists:

- Log the replacement.
- Disconnect the incumbent.
- Mark the challenger as the active peer.
- Attach the new socket.
- Start receiving.
- Signal that a connection is available.

Thus:

```text
new connection + incumbent
        ↓
admit challenger
        ↓
disconnect incumbent
        ↓
attach challenger
```

The server does not maintain multiple simultaneous client slots.

### 18. Server Connection State

The server exposes:

#### active_peer

Returns:

```text
(host, port)
```

for the active client, or `None`.

#### wait_for_connection(timeout)

Blocks until a client is attached.

Returns:

```text
True  → connection established
False → timeout
```

This provides an event-based alternative to polling `is_connected`.

### 19. Server kick

`kick()` forcibly disconnects the active client while leaving the server listener running.

After kicking:

- Active peer becomes `None`.
- Connection event is cleared.
- Active socket is detached.
- The next admitted client can connect normally.

### 20. Server stop

`stop()` completely stops the server.

It must:

- Stop the accept loop.
- Close the listening socket.
- Wait for the accept thread to terminate, with a bounded timeout.
- Disconnect the active client.
- Clear active-peer state.
- Log server shutdown.

After stopping, no listening socket remains active.

### 21. BinaryFramedSocketHandlerClient

This is a client specialization for protocols whose framing is binary rather than delimiter-based strings.

It adds a pluggable frame decoder.

#### 21.1 Frame decoder contract

The decoder receives:

```text
accumulated byte buffer
```

and returns:

```text
(decoded_frame, remaining_bytes)
```

If insufficient data exists for a complete frame:

```text
(None, unchanged_buffer)
```

A decoder may therefore consume zero or more complete frames from an accumulated TCP stream.

#### 21.2 Receive behavior

Every raw receive chunk is appended to the binary frame buffer.

The handler repeatedly invokes the decoder until:

- No complete frame remains.

Every decoded frame is passed to the registered frame handler.

#### 21.3 Decoder failure

If the decoder raises:

- Log the error.
- Clear the entire accumulated binary buffer.
- Stop processing that receive chunk.

The receive thread itself must remain protected from decoder failures.

#### 21.4 Frame handler failure

If the frame handler raises:

- Log the exception.
- Continue processing subsequent frames.

### 22. TransactionCore

`TransactionCore` is the thread-safe transaction state manager.

It is independent of the socket transport and transaction wire format.

Its responsibilities are:

- Generate transaction IDs.
- Register pending transactions.
- Track ACK state.
- Track final results.
- Track errors.
- Collect transaction events.
- Route incoming frames.
- Dispatch broadcast events.
- Dispatch remote-initiated transactions.

### 23. Transaction ID Generation

Transaction IDs are generated monotonically.

Initial state:

```text
counter = 0
```

First generated ID:

```text
1
```

- Every call increments the counter and returns the new value.
- ID generation is protected by the transaction lock.

### 24. Pending Transaction State

Each registered transaction maintains:

- `tx_id`
- `ack_event`
- `done_event`
- `acked`
- `result`
- `error`
- `events`

#### ACK state

Indicates whether a successful ACK was received.

#### Result state

Contains the received `TransactionFrame` for a `res` message.

#### Error state

Contains a human-readable error representation when applicable.

#### Events

Contains transaction-specific `evt` frames.

#### Synchronization

ACK and completion use independent events:

- `ack_event`
- `done_event`

This allows callers to wait for an ACK, raw-byte delivery, and delimiter-based string delivery. A binary specialization reconstructs arbitrary independently of final transaction completion.

### 25. Transaction Registration

Registering a transaction creates a new pending transaction entry keyed by its ID.

If an existing entry has the same ID, the current implementation replaces it.

Discarding a transaction removes the entry if present.

Discard is idempotent.

### 26. Incoming Transaction Routing

Every decoded `TransactionFrame` is routed according to its type and transaction ID.

#### 26.1 Broadcast event

##### Condition:

```text
msg_type == "evt"
and
tx_id < 0
```

##### Behavior:

- Send the frame to the broadcast handler if one is registered.
- Do not associate it with a pending transaction.
- Handler exceptions are suppressed.
- The intended broadcast identifier is `-1`.

### 27. Unknown Transaction IDs

If the frame does not correspond to a locally registered transaction:

```text
pending[tx_id] does not exist
```

the frame is treated as a remote-initiated transaction.

If an inbound handler exists:

- Invoke it with the frame.
- Suppress exceptions raised by the handler.

This enables both endpoints to initiate transactions over the same TCP connection.

### 28. ACK Routing

For:

```text
msg_type == "ack"
```

#### Successful ACK

If:

```text
code == 0
```

then:

- Mark transaction as acknowledged.
- Signal `ack_event`.

#### Failed ACK

If:

```text
code != 0
```

then:

- Construct an error description containing the ACK code and payload.
- Store it in the transaction error state.
- Signal `ack_event`.
- Signal `done_event`.

A failed ACK therefore terminates the transaction rather than merely indicating that acknowledgement failed.

### 29. Result Routing

For:

```text
msg_type == "res"
```

the frame is stored as the transaction result and `done_event` is signaled.

### 30. Event Routing

For:

```text
msg_type == "evt"
```

with a valid local transaction ID:

- Append the frame to that transaction's event collection.
- The event does not signal the final completion event.

### 31. Error Routing

For:

```text
msg_type == "err"
```

the transaction's error state is populated and `done_event` is signaled.

The error text is:

- The payload converted to string when a payload exists.
- Otherwise a generated "error code <code>" representation.

### 32. Waiting for ACK

```text
wait_ack(tx_id, timeout):
```

- Looks up the pending transaction.
- Returns `False` if it does not exist.
- Otherwise blocks on `ack_event`.
- Returns whether the event was signaled before timeout.
- The method does not itself remove the transaction.

### 33. Waiting for Result

```text
wait_result(tx_id, timeout):
```

- Looks up the pending transaction.
- Returns `None` if it does not exist.
- Waits for `done_event`.
- Returns the stored result frame.

An error completion therefore produces:

```text
None
```

from `wait_result`, because the error is stored separately rather than represented by the returned frame.

A timeout also produces:

```text
None
```

### 34. Transaction Socket Handlers

Two concrete transaction-enabled socket handlers are required:

- `TransactingSocketHandlerClient`
- `TransactingSocketHandlerServer`

They share the same transaction semantics.

The difference is only the underlying TCP role.

Both contain:

- A socket handler.
- A transaction codec.
- A transaction core.
- An optional raw string passthrough callback.

### 35. Transaction Receive Pipeline

Incoming string tokens are processed as:

```text
TCP receive
    ↓
string delimiter accumulation
    ↓
complete raw token
    ↓
TransactionCodec.decode()
    ↓
TransactionFrame
    ↓
TransactionCore.route()
    ↓
transaction state / broadcast / inbound handler
    ↓
optional user string handler
```

The user string handler receives the original raw token, not the decoded frame.

It runs after transaction routing.

### 36. Codec Failure During Routing

If a raw string token cannot be decoded:

- Log a decoding error.
- Do not route the frame.
- Still invoke the user string handler with the raw token.

Thus malformed transaction messages remain visible to the application-level raw string handler.

### 37. send_transaction

The transaction-enabled socket handlers expose:

```text
send_transaction(
    msg_type,
    code,
    payload=None,
    wait_ack=True,
    wait_result=False,
    timeout=None
)
```

#### 37.1 Send sequence

The operation must:

- Allocate a new transaction ID.
- Register the transaction.
- Encode the transaction through the configured codec.
- Send the resulting bytes.
- Optionally wait for ACK.
- Optionally wait for final result.
- Always discard the transaction registration when finished.

### 38. ACK Waiting

When:

```text
wait_ack = True
```

the sender blocks until:

- A successful ACK arrives.
- A failed ACK arrives.
- The timeout expires.

If ACK waiting times out:

- Log an ACK timeout.
- Continue according to the remaining options.

A timeout does not automatically abort the subsequent result wait.

### 39. Result Waiting

When:

```text
wait_result = True
```

the sender waits for a `res` or `err` completion event.

The returned value is:

```text
TransactionFrame | None
```

- A successful result returns its frame.
- An error or timeout returns `None`.

When:

```text
wait_result = False
```

the method returns `None`.

### 40. Timeout Semantics

`timeout` applies independently to each blocking operation.

Therefore, when both are enabled:

```text
wait_ack=True
wait_result=True
timeout=T
```

the theoretical maximum blocking duration can be approximately:

```text
2 × T
```

because ACK waiting and result waiting are separate waits.

`None` means wait indefinitely.

### 41. Transaction Cleanup

Every `send_transaction` invocation must remove its pending transaction entry when the method exits, including when encoding or sending raises an exception.

This cleanup is mandatory.

Therefore, transaction registrations are temporary and exist only for the lifetime of the synchronous transaction operation.

### 42. Broadcast Event Handler

The transaction socket exposes registration for unsolicited broadcast events.

Signature conceptually:

```text
handler(TransactionFrame)
```

Broadcast events are identified by a negative transaction ID, with `-1` as the defined protocol value.

The handler is invoked asynchronously from the receive path.

### 43. Inbound Transaction Handler

The transaction socket exposes registration for remote-initiated transactions.

Signature:

```text
handler(TransactionFrame)
```

The handler is invoked when an incoming frame references a transaction ID that is not currently registered locally.

This enables bidirectional transaction behavior:

```text
Client ── request ──> Server
Client <── response ── Server

Server ── request ──> Client
Server <── response ── Client
```

A single TCP connection can therefore support transactions initiated by either endpoint.

### 44. Concurrency Requirements

The system is explicitly multithreaded.

#### Receive processing

Runs on a daemon thread.

#### Server acceptance

Runs on a separate daemon accept thread.

#### Transaction state

Must be protected against concurrent access.

#### Socket state

Must be protected against concurrent attachment/detachment/access.

#### Event objects

Are used for synchronization between receive threads and callers waiting on transaction completion.

Callbacks execute from the relevant background processing context and therefore must not be assumed to run on the caller's thread.

### 45. Callback Isolation

Application callbacks must not be allowed to kill transport threads.

The following callbacks require exception isolation:

- Raw data handler.
- String handler.
- Binary frame handler.
- Transaction broadcast handler.
- Inbound transaction handler.
- Server connection-admission callback.

Exceptions must be logged where appropriate; transaction routing callbacks currently suppress their exceptions rather than propagating them.

### 46. Dependency Injection

The logger is an explicit dependency throughout the socket hierarchy.

The framework must not instantiate its own logger.

Transaction codecs are also injected:

```text
TransactingSocketHandler(..., codec=...)
```

This permits changing the wire protocol without changing socket or transaction logic.

### 47. Separation of Concerns

The implementation establishes four distinct responsibilities:

#### Transport

Responsible for:

- TCP sockets.
- Connect/listen/accept.
- Send/receive.
- Connection lifecycle.
- Thread management.

#### Stream framing

Responsible for:

- Delimiter-based string tokenization.
- Binary frame accumulation and decoding.

#### Transaction protocol

Responsible for:

- Transaction IDs.
- ACK/RES/ERR/EVT semantics.
- Pending transaction state.
- Synchronous waiting.
- Broadcast and inbound transactions.

#### Wire codec

Responsible for:

- Serializing transaction frames.
- Deserializing transaction frames.
- Payload representation.

None of these responsibilities should be tightly coupled to a particular concrete wire format.

### 48. End-to-End Data Flow

#### Outbound transaction

```text
Application
    │
    │ send_transaction()
    ▼
TransactionCore
    │ allocate/register tx_id
    ▼
TransactionCodec
    │ encode
    ▼
bytes
    │
    ▼
SocketHandler.send()
    │
    ▼
TCP
```

#### Inbound transaction

```text
TCP
    │
    ▼
Socket recv thread
    │
    ▼
string accumulation
    │
    ▼
complete token
    │
    ▼
TransactionCodec.decode()
    │
    ▼
TransactionFrame
    │
    ▼
TransactionCore.route()
    ├── ACK → pending ACK state
    ├── RES → pending result
    ├── ERR → pending error
    ├── EVT → pending event list
    ├── broadcast → broadcast handler
    └── unknown tx → inbound handler
```

### 49. Protocol Invariants

The following are fundamental requirements of the design:

- TCP is treated as a byte stream, not a message protocol.
- String messages require delimiter-based reconstruction.
- Binary protocols require an explicit frame decoder.
- Transaction serialization is delegated entirely to a codec.
- Transaction state is independent of wire format.
- Transaction IDs identify locally pending transactions.
- Unknown transaction IDs are eligible for remote-initiated transaction handling.
- Negative transaction IDs represent unsolicited/broadcast traffic.
- ACK and final completion are separate synchronization stages.
- A failed ACK signals both ACK and completion.
- RES signals completion and supplies the result frame.
- ERR signals completion but is represented through transaction error state.
- EVT does not complete a transaction.
- Socket callbacks cannot terminate transport threads.
- Only one server-side TCP client is active at a time.
- A newly admitted server connection replaces the incumbent.
- A rejected server challenger never displaces the incumbent.
- Transport sockets are composed, not inherited from `socket.socket`.
- Socket lifecycle operations are safe against repeated disconnect/cleanup.
- Transaction registrations are cleaned up after synchronous transaction calls.

### 50. Public API Summary

At the conceptual API level, the system exposes:

```text
SocketHandler
├── is_connected
├── string_delimiter
├── send(bytes)
├── send_string(str)
├── set_data_message_handler(handler)
├── set_string_message_handler(handler)
└── disconnect()

SocketHandlerClient
└── connect(host, port, timeout)

SocketHandlerServer
├── active_peer
├── wait_for_connection(timeout)
├── listen(port)
├── stop()
└── kick()

BinaryFramedSocketHandlerClient
└── set_frame_handler(handler)

TransactingSocketHandlerClient
├── send_transaction(...)
├── set_broadcast_event_handler(handler)
└── set_inbound_transaction_handler(handler)

TransactingSocketHandlerServer
├── send_transaction(...)
├── set_broadcast_event_handler(handler)
└── set_inbound_transaction_handler(handler)

TransactionCodec
├── encode(...)
└── decode(...)

TransactionFrame
├── tx_id
├── msg_type
├── code
└── payload
```

### 51. Minimal Conceptual Contract

If reducing the entire implementation to its essential specification, the system is essentially:

A threaded IPv4 TCP transport with pluggable stream framing and pluggable transaction serialization.

The transport provides connection lifecycle, raw-byte delivery, and delimiter-based string delivery. A binary specialization reconstructs arbitrary frames from the TCP byte stream through a caller-supplied decoder.

The transaction layer assigns unique IDs, serializes transactions through an injected codec, tracks pending transactions, waits independently for ACK and completion, stores transaction
