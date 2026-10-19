---
human_ask: >
  The goal of this work is to implement a reliable bidirectional IPC
  communication channel using Unix named pipes (FIFOs). The solution will support configurable
  message framing, binary and string payloads, asynchronous message handling, disconnected
  message queuing, and configurable queue-draining strategies. It will include robust lifecycle
  management, error handling, thread safety, and cleanup to ensure dependable communication
  between local and remote processes. The implementation will provide a well-defined interface
  that can be integrated into existing automation and messaging workflows.
goal: >
  The goal of this work is to implement a reliable bidirectional IPC communication channel
  using Unix named pipes (FIFOs). The solution will support configurable message framing,
  binary and string payloads, asynchronous message handling, disconnected message queuing,
  and configurable queue-draining strategies. It will include robust lifecycle management,
  error handling, thread safety, and cleanup to ensure dependable communication between local
  and remote processes. The implementation will provide a well-defined interface that can be
  integrated into existing automation and messaging workflows.
last_updated: 2026-09-23
semver: 0.1.0
author: Nicholas Bergantz
status: parked
---

# Plan 26 - Reliable Bidirectional Named-Pipe IPC

## Archive status

Parked unexecuted during the 2026-09-23 plan cleanup. Preserve this proposal as a future scoping input; it is not part of the active execute-plan queue.

## Goal

The goal of this work is to implement a reliable bidirectional IPC communication channel using Unix named pipes (FIFOs). The solution will support configurable message framing, binary and string payloads, asynchronous message handling, disconnected message queuing, and configurable queue-draining strategies. It will include robust lifecycle management, error handling, thread safety, and cleanup to ensure dependable communication between local and remote processes. The implementation will provide a well-defined interface that can be integrated into existing automation and messaging workflows.

## Body

### Detailed Specification: `NamedPipe`

### 1. Purpose

Implement a bidirectional inter-process communication channel using two Unix named pipes (FIFOs).

The channel must provide:

- Byte-message sending.
- Optional string-message sending using a configurable encoding.
- Optional length-prefixed message framing.
- Background reception and handler dispatch.
- Message queuing while disconnected.
- Configurable queue-draining strategies.
- Local/remote endpoint symmetry.
- Lifecycle management through `open()`, `close()`, and context-manager support.
- Explicit error types for pipe creation, opening, and writing failures.

### 2. External Interface

#### Constructor

```text
NamedPipe(
    name,
    pipe_dir="/tmp",
    remote=False,
    queue_strategy=FIFO,
    framing=True,
    poll_interval=0.01,
    encoding="utf-8",
    blocking_writes=True
)
```

#### Parameters

| Parameter | Type | Default | Requirements |
| --- | --- | --- | --- |
| `name` | string | required | Logical channel identifier and FIFO filename prefix |
| `pipe_dir` | path/string | `/tmp` | Directory containing the FIFOs |
| `remote` | boolean | `False` | Reverses read/write FIFO roles |
| `queue_strategy` | `QueueStrategy` | `FIFO` | Determines ordering of messages queued while disconnected |
| `framing` | boolean | `True` | Enables 4-byte length-prefixed messages |
| `poll_interval` | float | `0.01` | Delay between non-blocking read attempts |
| `encoding` | string | `utf-8` | Encoding used by string messages |
| `blocking_writes` | boolean | `True` | Controls whether the write FD remains blocking |

#### Properties

Expose read-only properties:

- `name`
- `in_path`
- `out_path`
- `connected`
- `framing`
- `queue_strategy`

### 3. FIFO Layout

For channel name `X` and directory `D`, create:

```text
D/X_in
D/X_out
```

From the local endpoint's perspective:

```text
X_in   = read from remote
X_out  = write to remote
```

When `remote=True`, reverse the logical direction:

```text
X_out  = read from local
X_in   = write to local
```

Both endpoints using the same name must therefore communicate through the same two FIFO files.

### 4. FIFO Creation Requirements

`open()` must ensure both FIFO files exist.

For each required path:

- If it does not exist, create it as a Unix FIFO.
- If it already exists:
  - Verify it is actually a FIFO.
  - If it is not a FIFO, raise `PipeCreateError`.
- Handle races where another process creates the FIFO between existence checking and creation.
- Convert unexpected filesystem/creation failures to `PipeCreateError`.
- Existing valid FIFOs must be reusable.

### 5. Opening the Channel

`open()` must:

- Ensure both FIFOs exist.
- Open the input FIFO:
  - Read-only.
  - Non-blocking.
- Open the output FIFO:
  - Write-only.
  - Blocking by default.
  - If `blocking_writes=False`, change the output FD to non-blocking.
- Mark the channel connected.
- Flush messages queued while disconnected.
- Start a daemon background reader thread.
- Give the reader thread a deterministic name such as:

```text
pipe-reader-{name}
```

#### Open failure behavior

##### If opening the input FIFO fails

```text
raise PipeOpenError(...)
```

##### If opening the output FIFO fails

- Close the already-open input FD.
- Reset the input FD state.
- Raise `PipeOpenError`.

The write-side open may block until the remote endpoint opens the corresponding read FIFO. This is intentional IPC behavior.

### 6. Closing the Channel

`close()` must:

- Mark the channel disconnected.
- Signal the reader thread to stop.
- Wait for the reader thread for at most 2 seconds.
- Close the input and output file descriptors.
- Ignore errors encountered while closing individual FDs.
- Reset FD references to `None`.
- Remove both FIFO files if present.
- Log channel closure.

Calling `close()` must be safe even if:

- The channel was never successfully opened.
- An FD is already closed.
- A FIFO has already been removed.

FIFO removal failures should be logged rather than propagated.

### 7. Context Manager

Support:

```text
with NamedPipe(...) as channel:
    ...
```

#### Behavior

- `__enter__()` calls `open()` and returns the channel.
- `__exit__()` always calls `close()`.

### 8. Message Sending

```text
send(data, priority=0, queue_if_disconnected=True)
```

#### Input

- `data`: bytes
- `priority`: integer
- `queue_if_disconnected`: boolean

#### If disconnected

##### If `queue_if_disconnected=True`

- Add the raw message and priority to the internal queue.
- Do not write to the FIFO.

##### If `False`

```text
raise PipeWriteError("Channel is not connected")
```

#### If connected

- Apply framing if enabled.
- Obtain the output FD safely.
- If the FD is unavailable, raise `PipeWriteError`.
- Write the resulting bytes to the FIFO.
- Convert write failures to `PipeWriteError`.

If a non-blocking write encounters:

- `EAGAIN`
- `EWOULDBLOCK`

raise `PipeWriteError` indicating that the pipe buffer is full and the message was dropped.

Other OS errors should also become `PipeWriteError`.

### 9. String Sending

```text
send_string(text, priority=0, queue_if_disconnected=True)
```

The implementation must:

- Encode text using the configured encoding.
- Call `send()` with the resulting bytes.
- Preserve priority and `queue_if_disconnected`.

### 10. Message Framing

When framing is enabled, every outgoing message must use:

```text
[4-byte length][payload]
```

The length is:

- Unsigned 32-bit integer.
- Big-endian.
- Equal to the payload's byte length.

Equivalent wire format:

```text
!I + payload
```

#### Maximum payload

The 32-bit length field defines the theoretical maximum payload size:

```text
0 .. 4,294,967,295 bytes
```

No additional application-level maximum is specified.

#### Encoding helper

`frame_encode(payload)` must return:

```text
4-byte big-endian payload length + payload
```

### 11. Frame Decoding

`frame_decode(data)` must:

- Start at offset zero.
- Require at least 4 bytes for a header.
- Read the next 4-byte big-endian unsigned length.
- Determine the payload boundaries.
- If the complete payload is available, return it.
- Continue parsing subsequent frames.
- Stop when a complete frame is unavailable.
- Return all complete payloads found.
- An incomplete trailing frame must not be returned.
- The decoder itself does not preserve incomplete data; the caller is responsible for buffering it.

### 12. Receive Buffering

When framing is enabled, the reader must maintain a persistent byte buffer.

For every incoming chunk:

- Append the chunk to the buffer.
- Decode all complete frames.
- Dispatch every complete message.
- Remove only the bytes belonging to successfully decoded messages.
- Preserve any incomplete trailing frame for the next read.

This must correctly handle:

- Multiple messages in one read.
- One message split across multiple reads.
- Header split across reads.
- Header and payload split across reads.
- A combination of complete and incomplete frames.

When framing is disabled, each OS read chunk is treated as a message and dispatched directly.

### 13. Reader Thread

A daemon background thread must continuously read from the input FIFO.

#### Read behavior

The loop must:

- Check the stop event.
- Obtain the input FD.
- Exit if no FD exists.
- Attempt a non-blocking read of up to:

```text
65,536 bytes
```

On `EAGAIN` or `EWOULDBLOCK`:

- Sleep for `poll_interval`.
- Retry.

On other read errors:

- Log the error.
- Exit the reader loop.

If zero bytes are returned:

- Sleep for `poll_interval`.
- Continue.

Otherwise process the received chunk.

### 14. Message Dispatch

For every decoded message:

#### Binary handler

If a data handler is registered:

```text
handler(payload: bytes)
```

must be called.

Exceptions from the handler must:

- Be caught.
- Be logged.
- Not terminate the reader thread.

#### String handler

If a string handler is registered:

- Decode the payload using the configured encoding.
- Call:

```text
handler(text: str)
```

Exceptions from either decoding or the handler must:

- Be caught.
- Be logged.
- Not terminate the reader thread.

If both handlers are configured, both should receive the same payload independently.

### 15. Handler Registration

Provide:

```text
set_data_message_handler(handler | None)
set_string_message_handler(handler | None)
```

Passing `None` disables the corresponding handler.

Only one data handler and one string handler are supported at a time.

### 16. Disconnected Message Queue

Messages sent while disconnected may be stored internally.

Each queued item contains:

- `priority`: integer
- `data`: bytes

The priority affects ordering for applicable queue strategies but must not modify the message contents.

Queued messages should retain their original, unframed payload. Framing occurs when the message is eventually sent.

### 17. Queue Strategies

When the channel connects, queued messages must be drained according to the configured strategy.

#### FIFO

Preserve insertion order:

```text
A B C → A B C
```

#### LIFO

Reverse insertion order:

```text
A B C → C B A
```

#### ROUND_ROBIN

- Group messages by priority.
- Process priority groups from highest numeric priority to lowest.
- Take one message from each non-empty priority group per round.
- Continue until all groups are empty.

##### Example

```text
priority 3: A B
priority 2: C D E
priority 1: F

result: A C F B D E
```

Unknown strategies should fall back to FIFO behavior.

### 18. Queue Flushing

After the channel becomes connected:

- Extract and clear the pending queue.
- Order messages according to the configured strategy.
- Send each queued message.

If an individual send fails:

- Log a warning.
- Continue attempting to flush the remaining messages.

Queue flushing must not recursively requeue a failed message simply because `send()` defaults to `queue_if_disconnected=True`.

### 19. Thread Safety

The implementation must protect shared file-descriptor state using a lock.

At minimum, access to:

```text
_in_fd
_out_fd
```

must be synchronized.

The design should tolerate concurrent:

- `send()`
- `close()`
- reader-thread activity

without corrupting FD state.

### 20. State Model

The channel has two externally meaningful states:

```text
DISCONNECTED
     |
     | open()
     v
 CONNECTED
     |
     | close()
     v
DISCONNECTED
```

`connected` must reflect whether the channel has been successfully opened.

A reader-thread failure does not automatically reopen the channel.

### 21. Error Model

The implementation must expose three domain-specific error categories:

- `PipeCreateError`
- `PipeOpenError`
- `PipeWriteError`

#### Expected mapping

| Failure | Error |
| --- | --- |
| FIFO creation/validation failure | `PipeCreateError` |
| FIFO FD opening failure | `PipeOpenError` |
| Message cannot be written | `PipeWriteError` |

Read-side runtime errors are logged and terminate the reader loop rather than being propagated to the caller.

### 22. Cleanup

A helper must remove a FIFO path if it exists.

#### Requirements

- Missing path is ignored.
- Successful removal completes silently.
- Filesystem errors are caught and logged.
- Cleanup must not cause `close()` to fail.

### 23. Logging

Use a module-level logger.

Log at approximately these levels:

- INFO: channel opened/closed.
- WARNING: queued-message flush failure or FIFO cleanup failure.
- ERROR: unrecoverable reader error.
- EXCEPTION: handler or handler-decoding failure, including traceback.

Logs should identify the channel name where practical.

### 24. Constants

The implementation should define:

```text
HEADER_FORMAT = "!I"
HEADER_SIZE = size of HEADER_FORMAT
MAX_READ = 65536
```

The protocol therefore has a fixed 4-byte length header and a maximum individual read size of 64 KiB.

### 25. Behavioral Acceptance Criteria

An implementation conforming to this specification must satisfy at least the following:

- Two channel instances using the same name can communicate bidirectionally.
- `remote=True` reverses the communication direction correctly.
- Existing valid FIFOs are reused.
- Non-FIFO files at expected paths are rejected.
- Opening the read side does not block.
- Blocking write-side opening waits for the peer when necessary.
- Non-blocking writes report a full pipe through `PipeWriteError`.
- Messages sent while disconnected can be queued.
- Queued messages are flushed after connection.
- FIFO, LIFO, and priority round-robin ordering work as specified.
- Framed messages survive arbitrary read fragmentation.
- Multiple framed messages received in one read are dispatched individually.
- Incomplete frames remain buffered.
- Unframed reads are dispatched as individual chunks.
- Binary and string handlers can coexist.
- Handler exceptions do not kill the reader thread.
- `close()` stops the reader and cleans up resources.
- Context-manager usage opens and closes the channel automatically.
- Resource-opening failures clean up partially initialized resources.
- Concurrent FD access does not race with cleanup.
