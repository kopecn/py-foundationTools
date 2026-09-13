---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Implement the binary-frame decoder specialization over the threaded client.
last_updated: 2026-09-12
semver: 0.0.1
author: Nicholas Bergantz
status: completed
---

# 12 — Binary-framed socket client

Scope: [summary goal](00-overview.md#summary-goal) · [original ask](00-original-ask.md) · Contract: [binary-framed client](../../specs/threadedSocketTransport.md#binary-framed-client)

## Deliverable

Create `BinaryFramedSocketHandlerClient`, extending each epoch's receive pipeline with accumulated binary decoding and isolated frame callbacks while preserving inherited raw/text channels.

## Depends on

08 receive dispatch and 09 threaded socket client.

## Files

- Create `src/foundation_tools/socket_transaction/binary_framed_socket_handler_client.py`.
- Create `tests/test_binary_framed_socket_handler_client.py`.

## Design constraints

- Constructor injects `frame_decoder`; outbound binary data continues through inherited raw `send`.
- Override `_process_received_chunk(epoch, data)`, call `super()` once, then process the epoch-owned binary buffer.
- A valid remainder must be a byte suffix of input. A frame must strictly shorten input. `(None, identical_input)` is the only incomplete-frame stop result.
- Any decoder exception/invalid progress clears the complete binary buffer for that epoch and returns without killing receive.
- Snapshot frame handler under lock, invoke outside locks, and contain/log handler exceptions.
- Reset binary state on every epoch detach/replacement.

## Decoder loop recipe

```python
while buffer:
    frame, remainder = decoder(buffer)
    if frame is None and remainder == buffer:
        break
    if not isinstance(remainder, bytes) or not buffer.endswith(remainder):
        raise ValueError("decoder remainder is not an input suffix")
    if frame is None or len(remainder) >= len(buffer):
        raise ValueError("decoder made no valid progress")
    buffer = remainder
    dispatch_frame(frame)
```

## TDD steps

1. Add failing fragmented and multi-frame decoding tests over socketpair.
2. Add every invalid progress/remainder case and decoder exception recovery.
3. Add frame-handler failure/continuation and reconnect-buffer-reset tests.
4. Implement the specialization and run `pytest tests/test_binary_framed_socket_handler_client.py` plus `make fullCheck`.

## Acceptance criteria

- [x] Byte-at-a-time input yields each frame exactly once and in order.
- [x] No decoder output can create an infinite loop.
- [x] Decoder failure clears binary state but a later valid frame is delivered by the same receive worker.
- [x] Raw and text callbacks still observe the same received chunks.
- [x] `make fullCheck` passes.

## Out of scope

- An outbound frame encoder or binary transaction codec.
- Server binary specialization.
- Buffer-size limits not present in the accepted contract.

## Ask ↔ result

- **Objective (human_ask + goal):** the recorded `human_ask` is the top-level directive to replace the asyncio socket stack in `src/foundation_tools/socket_transaction/` with threading/sockets. This chunk's `goal` narrows that to: implement the binary-frame decoder specialization over the threaded client. No conflict between `human_ask` and `goal`.
- **Live authorization:** `/execute-plan .claude/plans/25-threaded-socket-transaction` — the user explicitly authorized executing chunk 12 now.
- **Delivered:** `src/foundation_tools/socket_transaction/binary_framed_socket_handler_client.py` — `BinaryFramedSocketHandlerClient(logger, frame_decoder, *, string_delimiter="\n", join_timeout=1.0)` extends `SocketHandlerClient` with no other constructor changes. Adds `set_frame_handler(Callable[[object], None] | None)` and overrides `_process_received_chunk(epoch, data)`: calls `super()._process_received_chunk(epoch, data)` exactly once (preserving raw/text dispatch unchanged), then decodes frames via `_decode_frames_for_epoch`, and invokes each in order via `_invoke_frame_handler`. `_decode_frames_for_epoch` holds a dedicated `_binary_lock` for the whole decode: re-checks epoch currency with the inherited `_epoch_is_current` (dropping stale-epoch chunks entirely, mirroring the base class's own `_tokenize_for_epoch` pattern), resets the per-epoch buffer the first time a chunk is seen for a not-yet-tracked epoch (covers both a fresh connection and any reconnect), then runs the exact decoder-loop recipe from the chunk file: `(None, identical_input)` is the only incomplete-frame stop, a non-bytes or non-suffix remainder is invalid progress, and a `None` frame or a remainder not strictly shorter than the buffer is also invalid progress — each raises internally and is caught by one `except Exception`, which logs, clears the epoch's buffer entirely, and returns no frames without propagating (so the receive loop is never killed). Decoded frames are collected into a list and only invoked (via `_invoke_frame_handler`, itself lock-guarded for the handler snapshot only) after the `_binary_lock` is released, satisfying "invoke outside locks." Frame-handler exceptions are logged and contained per frame, so a failing handler does not block later frames. Outbound binary continues through the inherited raw `send`/`send_string`; no encoder, codec, server specialization, buffer-size limit, or package export was added. Not built on `foundation_abc.PeripheralByteTransport` — no import, no inheritance.
- `tests/test_binary_framed_socket_handler_client.py` — 12 tests, all using a length-prefixed test decoder (one length byte + that many payload bytes) over `tests/threaded_socket_helpers.socketpair_context` via the protected `_attach`/`_detach` primitives (mirroring `tests/test_socket_handler.py`'s white-box pattern), plus one real-loopback reconnect test via `ThreadedLoopbackListener`. No sleeps or randomness; all synchronization is bounded `queue.Queue.get(timeout=...)` or `threading.Event`.
  - `TestFragmentedAndMultiFrameDecoding` (4): byte-at-a-time delivery yields one frame exactly once; three frames in one chunk arrive in order; an incomplete frame is retained until a later chunk completes it; raw/text/frame callbacks all observe the same underlying raw chunk (the frame's length-prefix byte is itself valid single-byte UTF-8, so it legitimately appears in the delimited text token too — asserted explicitly with a comment, not hidden).
  - `TestInvalidProgressAndDecoderExceptionRecovery` (5): a decoder that raises `RuntimeError` on its first call clears the buffer but a later valid frame on the same connection still arrives; a non-`bytes` remainder; a remainder that is not a suffix of the input; a returned frame paired with a remainder no shorter than the input; and a `None` frame paired with a changed (but still suffix) remainder — each is invalid progress and yields zero frames.
  - `TestFrameHandlerFailureAndReconnectBufferReset` (3): a frame handler that raises on its first call is logged (`caplog`) and a subsequent frame is still delivered; replacing the frame handler mid-connection only affects frames decoded afterward; a real-loopback reconnect test that leaves an incomplete one-byte length header buffered on the first connection, reconnects to a second listener, and confirms a fresh short frame on the new connection decodes correctly rather than being misread as a continuation of the old epoch's partial header — proving the per-epoch buffer reset.
- **Verification:** confirmed TDD honesty by moving the implementation file out of the tree and re-running the test file — collection failed with `ModuleNotFoundError` for the new module (all 12 tests genuinely failing pre-implementation), then restored it. `pytest tests/test_binary_framed_socket_handler_client.py -v` — 12/12 passed. `make fullCheck` — flake8 (`src tests`), strict mypy (`src` and `tests` separately), and the full pytest suite (959 tests, up from 947 before this chunk) all passed. `git status --short` confirms only `src/foundation_tools/socket_transaction/binary_framed_socket_handler_client.py` and `tests/test_binary_framed_socket_handler_client.py` were added by this chunk; `socket_handler.py`, `socket_handler_client.py`, and `socket_handler_server.py` (and its test file, mid-edit by a concurrent agent per the live instructions) were not touched.
- **Gap:** none against this chunk's in-scope deliverable. No outbound frame encoder/binary transaction codec, server binary specialization, buffer-size limit, or package export was added; `foundation_abc.PeripheralByteTransport` was not referenced.
