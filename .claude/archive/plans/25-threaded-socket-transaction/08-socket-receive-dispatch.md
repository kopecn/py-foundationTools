---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Add daemon reception, raw callbacks, incremental UTF-8 tokenization, and close observation.
last_updated: 2026-09-12
semver: 0.0.1
author: Nicholas Bergantz
status: completed
---

# 08 — Raw and delimiter-text receive dispatch

Scope: [summary goal](00-overview.md#summary-goal) · [original ask](00-original-ask.md) · Contract: [receive dispatch](../../../specs/threadedSocketTransport.md#receive-dispatch)

## Deliverable

Complete `SocketHandler` reception: one daemon recv worker per epoch, exact raw-chunk delivery, incremental UTF-8 reconstruction, delimiter tokens, internal epoch observer, callback isolation, and EOF/error teardown.

## Depends on

07 socket handler lifecycle.

## Files

- Edit `src/foundation_tools/socket_transaction/socket_handler.py`.
- Edit `tests/test_socket_handler.py`.

## Design constraints

- `recv(4096)` is the only socket read loop and belongs to the attached epoch.
- Dispatch raw bytes first, then text processing. User callbacks and observer methods execute outside all locks.
- Use a fresh incremental UTF-8 decoder with replacement per epoch; clear decoder and incomplete token on any detach/replacement.
- `send_string` UTF-8 encodes only and does not append the receive delimiter.
- A callback exception is logged and does not prevent the other channel or later messages.
- Empty recv and receive `OSError` share the once-only conditional-detach path; an old worker cannot clear new state.
- `_process_received_chunk(epoch, data)` is the protected specialization hook chunk 12 will extend.

## TDD steps

1. Add failing socketpair tests for exact raw chunks, split delimiter tokens, multiple tokens/chunk, retained suffix, and split multibyte UTF-8.
2. Add raw/string/observer callback replacement and exception-containment tests.
3. Add event-gated EOF, recv-error, disconnect-from-callback, and old-worker-after-reconnect races.
4. Implement the receive worker, incremental decoder, observer, and extension hook.
5. Run `pytest tests/test_socket_handler.py` and `make fullCheck`.

## Acceptance criteria

- [x] The spec example chunks `abc\n12` then `3\nxyz\n` yield exactly `abc`, `123`, `xyz`.
- [x] A UTF-8 code point split at every byte boundary reconstructs once without replacement.
- [x] Each callback failure is logged and a subsequent token is delivered by the same worker.
- [x] EOF/error clears only its epoch and calls the close observer once.
- [x] `make fullCheck` passes.

## Out of scope

- Callback worker pools or blocking receive queues.
- Binary decoding.
- Client/server role behavior.

## Ask ↔ result

- **Objective (human_ask + goal):** the recorded `human_ask` is the top-level directive to replace the asyncio socket stack in `src/foundation_tools/socket_transaction/` with threading/sockets. This chunk's `goal` narrows that to: add daemon reception, raw callbacks, incremental UTF-8 tokenization, and close observation. No conflict between `human_ask` and `goal`.
- **Live authorization:** `/execute-plan .claude/plans/25-threaded-socket-transaction` — the user explicitly authorized executing chunk 08 now.
- **Delivered:** `src/foundation_tools/socket_transaction/socket_handler.py` — filled in the chunk-07 `_process_received_chunk(epoch, data)` stub. Added per-epoch state (`_text_decoder`: a fresh `codecs.getincrementaldecoder("utf-8")(errors="replace")` instance, `_pending_text`), reset under the state lock in `_attach` and discarded (not flushed) under the state lock in `_detach`. `_process_received_chunk` first re-validates the epoch is still current (`_epoch_is_current`) and drops the chunk entirely otherwise; then dispatches the raw chunk unchanged to the raw-data handler (`_invoke_raw_handler`); then decodes+splits into delimiter-terminated tokens under a second, independent epoch recheck inside the state lock (`_tokenize_for_epoch`, guarding against a worker that raced past the first check), delivering each token to the string handler (`_invoke_string_handler`) and then the connection observer's `on_string_token(epoch, token)` (`_notify_string_token`), both outside all locks with per-callback exception containment (logged via `self._logger.exception`, never propagated).
- `tests/test_socket_handler.py` — added 16 tests (24 → 40) plus three test doubles (`_GatedRecvSocket`, `_RecvErrorSocket`, `_RecordingObserver`), all synchronized with `threading.Event`/bounded `queue.Queue.get(timeout=...)`, no sleeps or randomness:
  - `TestRawAndTextDispatch` (5): exact raw chunk bytes; the spec's own `abc\n12` / `3\nxyz\n` → `abc`, `123`, `xyz` example; retained suffix without a delimiter; a UTF-8 code point (`é`) split at every byte boundary reconstructing once with no replacement character; `send_string` not itself introducing a token boundary.
  - `TestCallbackAndObserverIsolation` (7): raw/string/observer replacement affecting only subsequent deliveries; observer receiving epoch-tagged tokens; raw/string/observer callback exceptions each logged and not blocking a later chunk/token on the same worker.
  - `TestReceiveRaces` (4): EOF and receive-`OSError` each detach only their epoch and call the close observer exactly once; `disconnect()` called from inside a string callback (i.e. from the receive thread itself) does not deadlock and the worker exits cleanly; an old worker paused mid-flight (via `_GatedRecvSocket`) after a reconnect delivers nothing (`raw_chunks` and `observer.tokens` both confirmed empty for the stale epoch via bounded `queue.Empty`) and the new epoch's dispatch is uncorrupted.
- **Verification:** confirmed TDD honesty by stashing the source change and re-running the full test file — the 14 new dispatch-dependent tests failed against the chunk-07 no-op stub (the 2 EOF/lifecycle-only new tests and all 24 chunk-07 tests still passed), then restored the implementation. `pytest tests/test_socket_handler.py -v` — 40/40 passed. `rg -n "asyncio|async def" src/foundation_tools/socket_transaction/socket_handler.py` — no matches. `make fullCheck` — flake8, strict mypy (`src` + `tests`), and the full pytest suite (871 tests, up from 855 before this chunk) all passed.
- **Gap:** none against this chunk's in-scope deliverable. No callback worker pool, blocking receive queue, binary decoding, or client/server role behavior was added; no package export was added; `git diff --stat` confirms only `src/foundation_tools/socket_transaction/socket_handler.py` and `tests/test_socket_handler.py` changed.
