---
plan: ActionPlan16SocketByteTransportNonblocking
scope: project
status: complete
last_updated: 2026-07-06
semver: 0.2.0
author: Nicholas Bergantz
---

# 16 — SocketByteTransport Non-blocking Receive (corrective)

## Goal

Make `SocketByteTransport.receive(timeout=0)` honor the ABC contract. The ABC
([peripheralByteTransport.py](../../src/foundation_abc/peripheralByteTransport.py))
states "A ``timeout`` of zero is non-blocking" — i.e. return already-buffered
bytes immediately, else time out. The current implementation
(`socket_byte_transport.py`, `asyncio.wait_for(self._reader.read(size), timeout=0)`)
cancels the read task before it is ever scheduled, so a non-blocking read can
**never** return data even when bytes are buffered. Only the no-data case is
tested today.

## Origin

Chunk 05 audit finding (corrective follow-up to plans 00–13). Not currently hit
in the stack (the router polls with `poll_timeout=1.0`), but it is an ABC
compliance drift and a trap for any direct consumer.

## Depends on

None — independent.

## Files

- `src/foundation_tools/socket_transaction/socket_byte_transport.py`
- `tests/test_socket_byte_transport.py`

## Design constraints

- ABC contract unchanged — it is shared with external serial implementations, so
  the fix has no blast radius outward.
- Fast-path shape for `timeout <= 0`: schedule the read
  (`asyncio.ensure_future(self._reader.read(size))`), yield exactly once
  (`await asyncio.sleep(0)`) so the task can consume buffered data, then:
  done → return its result; not done → cancel, await the cancellation, raise
  `TimeoutError`. No busy-wait, no private `StreamReader` attribute access.
- Positive-timeout behavior byte-for-byte unchanged (existing tests must pass
  untouched).
- EOF semantics unchanged: peer-closed-no-data still returns `b""`, including on
  the zero-timeout path.

## Steps (TDD)

1. Failing tests first: `timeout=0` with data already buffered returns it;
   `timeout=0` with no data raises `TimeoutError`; `timeout=0` after peer close
   returns `b""`.
2. Implement the zero-timeout fast path in `receive()`; update the docstring to
   state the non-blocking rule.
3. `make uv-fullCheck`.

## Acceptance criteria

- [x] `receive(size, timeout=0)` returns buffered bytes when available.
- [x] `receive(size, timeout=0)` raises `TimeoutError` when none available, and
      returns `b""` at EOF.
- [x] All existing positive-timeout tests pass unchanged.
- [x] `make uv-fullCheck` passes.

## Out of scope

- Changing the ABC contract or its docstrings.
- Router/facade changes (they use positive timeouts and are unaffected).
- Negative-timeout semantics beyond treating them as zero.

## Resolution notes

- Added three tests to `tests/test_socket_byte_transport.py`:
  `test_receive_timeout_zero_returns_buffered_data` (echo server + a short
  `asyncio.sleep(0.05)` after `send()` to let the event loop deliver bytes into
  the `StreamReader` buffer before the non-blocking `receive`) and
  `test_receive_timeout_zero_at_eof_returns_empty_bytes` (peer closes
  immediately, zero-timeout `receive` must return `b""`, not raise). The
  pre-existing `test_receive_timeout_zero_non_blocking` (no data, silent
  handler) continues to cover the "no data buffered → `TimeoutError`" case.
  Ran against the pre-fix implementation first to confirm both new tests failed
  (`asyncio.wait_for(..., timeout=0)` never let the read task get scheduled).
- Implemented the fast path in `receive()` exactly per the chunk's design
  constraint: for `timeout <= 0`, `asyncio.ensure_future(self._reader.read(size))`,
  one `await asyncio.sleep(0)`, then done → `task.result()`; not done →
  `task.cancel()` + `await task` under `contextlib.suppress(asyncio.CancelledError)`
  + raise `TimeoutError`. No busy-wait loop, no reach into `StreamReader`
  internals. Docstring updated to state the one-tick non-blocking rule.
- Positive-timeout branch (`asyncio.wait_for(self._reader.read(size), timeout=timeout)`)
  left untouched; all pre-existing tests pass unchanged.
- No surprises — the fix was a direct, mechanical application of the chunk's
  prescribed shape. `make uv-fullCheck` (`uv-lint` + `uv-typecheck` (mypy) +
  `uv-test`, 300 tests) passes; note `ty` is intentionally excluded from
  `uv-fullCheck` per the Makefile's own comment (pre-release, decision D1),
  unrelated to this chunk.
