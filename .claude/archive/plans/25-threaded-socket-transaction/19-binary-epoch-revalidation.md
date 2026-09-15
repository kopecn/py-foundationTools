---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Prevent a frame decoded from a closed connection epoch from reaching the application after replacement.
last_updated: 2026-09-13
semver: 0.1.0
author: Nicholas Bergantz
status: completed
---

# 19 - Suppress stale binary frames

Scope: [summary goal](00-corrective-overview.md#summary-goal) · [original ask](00-original-ask.md) · Contract: [stream epoch isolation](../../../specs/threadedSocketTransaction.md#stream-and-protocol-invariants) and [binary client](../../../specs/threadedSocketTransport.md#binary-framed-client)

## Origin

PA25-03: the post-audit blocked the decoder on epoch 1, replaced the connection with epoch 2, released the decoder, and observed the epoch-1 frame callback fire while epoch 2 was active.

## Deliverable

Revalidate connection epoch after decoder calls and immediately before application frame delivery so replacement makes every in-flight old-epoch frame inert.

## Depends on

None.

## Files

- Edit `src/foundation_tools/socket_transaction/binary_framed_socket_handler_client.py`.
- Edit `tests/test_binary_framed_socket_handler_client.py`.

## Design constraints

- Never hold the base socket state lock while invoking the caller-supplied decoder or frame handler.
- After every decoder return, stop and discard collected output if the originating epoch is no longer active.
- Recheck epoch before each frame callback because replacement may occur after decoding but before delivery.
- Never clear or mutate a newer epoch's binary buffer from a stale worker.
- Preserve raw and text dispatch ordering and all decoder progress validation.

## Race recipe

```python
decoder_entered = threading.Event()
release_decoder = threading.Event()

# Decoder for epoch 1 blocks after receiving a complete frame.
assert decoder_entered.wait(TEST_TIMEOUT)
client.disconnect()
attach_epoch_2()
release_decoder.set()
```

Assert no frame callback receives epoch-1 output and a valid epoch-2 frame is still delivered.

## TDD steps

1. Add the failing blocked-decoder replacement regression.
2. Add a callback-boundary replacement regression.
3. Implement epoch revalidation without moving callbacks under locks.
4. Run `pytest tests/test_binary_framed_socket_handler_client.py` and `make fullCheck`.

## Acceptance criteria

- [x] No frame decoded from a detached epoch is delivered after replacement.
- [x] Epoch-2 decoding remains usable after stale epoch-1 work returns.
- [x] Decoder and frame-handler callbacks execute without socket or binary locks held.
- [x] Existing fragmented, multi-frame, and recovery tests remain green.
- [x] `make fullCheck` passes.

## Out of scope

- Decoder cancellation or a callback executor.
- Outbound binary encoding.
- Server binary specialization or buffer-size limits.

## Ask ↔ result

**Objective (`human_ask` + `goal`):** `human_ask` is the plan-level ask that
authorized decomposing the top-level socket spec into bite-sized chunks; it
does not itself describe this chunk's behavior. This chunk's `goal` — "Prevent
a frame decoded from a closed connection epoch from reaching the application
after replacement" — is the operative objective for this execution, and does
not conflict with `human_ask` (no objective-level disagreement to stop on).

**Live authorization:** the user's explicit `/execute-plan 17 ... 25` request
to execute the already-decomposed corrective chunks, including 19.

**Delivered:** `_decode_frames_for_epoch` (which held `_binary_lock` across
the entire decoder loop, including the caller-supplied decoder call itself)
was replaced with `_decode_and_dispatch_frames` plus two small epoch-gated
helpers (`_commit_binary_buffer`, `_clear_binary_buffer`). The decoder and the
frame handler are now invoked with no internal lock held; the epoch is
revalidated (a) immediately after every decoder return, before that decode's
progress is committed to the shared buffer, and (b) again immediately before
each frame-handler call, so a replacement that lands either while the decoder
is still blocked or during an earlier frame's callback (same chunk) discards
the stale output instead of committing or delivering it. All existing
decoder-progress validation (suffix check, strict-shortening, single valid
incomplete-stop shape) and channel ordering (raw/text dispatch, then binary)
are unchanged.

Two failing regressions were added first and confirmed to fail against the
pre-fix code (`tests/test_binary_framed_socket_handler_client.py`,
`TestEpochRevalidationAfterReplacement`): a blocked-decoder replacement test
matching the plan's race recipe exactly, and a callback-boundary test where
the frame handler for one frame in a chunk synchronously replaces the
connection, and the chunk's next already-decoded frame must be suppressed.
Both pass after the fix, deterministically across repeated runs (Events only,
no sleeps, no unbounded joins), and all 14 tests in the file plus the full
901-test suite pass under `make fullCheck`.

**Gap:** none identified against this chunk's scope and design constraints.
