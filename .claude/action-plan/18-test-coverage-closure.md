---
plan: ActionPlan18TestCoverageClosure
scope: project
status: pending
last_updated: 2026-07-06
semver: 0.1.1
author: Nicholas Bergantz
---

# 18 — Test-Coverage Closure (corrective)

## Goal

Add the tests the audit found missing for behaviors that are implemented but
unproven. No production code changes are expected; if a test exposes a real
defect, fix it in this chunk and record it in the resolution notes (spec bump if
contract-visible).

Contracts: [cliTransact.md](../specs/cliTransact.md) Command Input Contract,
[socketTransact.md](../specs/socketTransact.md) containment rules, and the
chunk-09 router implementation notes.

## Origin

Chunk 02/09/10 audit findings (corrective follow-up to plans 00–13).

## Depends on

14 (its import-adjacent tests must load the policy layer cleanly first).

## Files

- `tests/testfoundationCLITransact.py` (async string-command path)
- `tests/test_socket_transact.py` (facade containment branches)
- `tests/test_transaction_router.py` (register-before-send race)

## Coverage to add

1. **CLITransact — async string command.** A positive `run_async("<non-empty
   string>")` test proving the `["bash", "-c", cli_command]` path executes and
   captures output (Command Input Contract row: async `str` → explicit `bash -c`).
   Today only the empty-string case touches this path.
2. **SocketTransact — outbound serialization containment.** A model whose
   `to_wire` raises must yield a contained `success=False` result from
   `request_with_model`, never an exception.
3. **SocketTransact — `send()` success path.** Assert a successful uncorrelated
   frame is encoded by the codec and written to the transport (only the
   raise-on-failure path is covered today).
4. **SocketTransact — empty-payload parse skip.** A `b""` correlated response
   must skip the parser (parser mock never called) and still return
   `success=True` with `model=None`.
5. **TransactionRouter — register-before-send race.** A deterministic regression
   test for the exact `KeyError` bug the chunk-09 notes describe fixing: prove
   the response future is registered **before** `send` completes. The current
   `FakeTransport.send` has no await point, so the race cannot interleave and
   the guard is unproven. Fake shape (subclass/extend the existing
   `FakeTransport`):

   ```python
   class SynchronousReplyTransport(FakeTransport):
       async def send(self, data: bytes) -> None:
           # Queue the correlated reply for the reader, then yield so the
           # reader task delivers it BEFORE this send() returns.
           self.queue_reply_for(data)      # echo back the frame's tx_id
           await asyncio.sleep(0)          # reader runs here
           await asyncio.sleep(0)          # ... and resolves the future
   ```

   The test awaits `router.request(...)` with a generous timeout and asserts the
   reply is received (not `TimeoutError`/`KeyError`) — this only passes when the
   future exists in the pending map at delivery time, i.e. registration happened
   before `send`.

## Design constraints

- Tests validate the spec contract, not implementation details (overview
  convention #1).
- The race test must be deterministic — engineered interleaving via await points,
  not sleeps or timing luck.
- Reuse the existing fakes/fixtures in each test module; extend `FakeTransport`
  rather than adding a parallel fake.

## Steps (TDD)

1. Write each test against the current implementation; expected outcome is pass
   (behavior exists). A failure is a defect: fix minimally in this chunk, record
   in resolution notes.
2. `make uv-fullCheck`.

## Acceptance criteria

- [ ] All five coverage items above have passing, behavior-asserting tests.
- [ ] The race test fails if the future-registration line is moved after `send`
      (verified once by mutation during development, noted in resolution notes).
- [ ] `make uv-fullCheck` passes.

## Out of scope

- Coverage tooling/thresholds.
- New production features; refactors beyond a minimal defect fix if one surfaces.
- Legacy `testfoundation*.py` renames.
