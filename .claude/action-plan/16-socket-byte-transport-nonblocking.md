---
plan: ActionPlan16SocketByteTransportNonblocking
scope: project
status: pending
last_updated: 2026-07-06
semver: 0.1.0
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

- [ ] `receive(size, timeout=0)` returns buffered bytes when available.
- [ ] `receive(size, timeout=0)` raises `TimeoutError` when none available, and
      returns `b""` at EOF.
- [ ] All existing positive-timeout tests pass unchanged.
- [ ] `make uv-fullCheck` passes.

## Out of scope

- Changing the ABC contract or its docstrings.
- Router/facade changes (they use positive timeouts and are unaffected).
- Negative-timeout semantics beyond treating them as zero.
