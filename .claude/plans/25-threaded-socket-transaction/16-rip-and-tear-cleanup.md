---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Atomically remove the asyncio socket stack, publish the threaded API, and eliminate documentation/example drift.
last_updated: 2026-09-13
semver: 0.3.0
author: Nicholas Bergantz
status: completed
---

# 16 - Rip-and-tear cleanup

Scope: [summary goal](00-overview.md#summary-goal) · [original ask](00-original-ask.md) · Contract: [public surface](../../specs/threadedSocketTransaction.md#public-surface)

## Deliverable

Rip out the pre-release asyncio implementation and tests, remove dead supporting code, export only the threaded surface, make client and server usage clear, supersede the old asyncio spec, and prove the package contains no socket-family asyncio dependency.

## Depends on

04 angle codec, 12 binary-framed client, and 15 transacting server/E2E. All earlier dependencies must be completed.

## Files

- Edit `src/foundation_tools/socket_transaction/__init__.py`.
- Delete `src/foundation_tools/socket_transaction/_lifecycle.py` if no new module imports it.
- Delete `src/foundation_tools/socket_transaction/socket_byte_transport.py`.
- Delete `src/foundation_tools/socket_transaction/framing_codecs.py`.
- Delete `src/foundation_tools/socket_transaction/transaction_router.py`.
- Delete `src/foundation_tools/socket_transaction/socketTransact.py`.
- Delete `src/foundation_tools/socket_transaction/socketTransactServer.py`.
- Delete `tests/test_socket_byte_transport.py`, `tests/test_framing_codecs.py`, `tests/test_transaction_router.py`, `tests/test_socket_transact.py`, `tests/test_socket_transact_server.py`, and `tests/test_socket_lifecycle_primitives.py` after their threaded replacements are green.
- Delete `tests/asyncio_server.py` after confirming no remaining import.
- Edit `tests/test_package_restructure.py` and any type/import tests that enumerate socket exports.
- Edit `examples/exampleSocketClientServer.py`, `examples/exampleBenchmarkPerformance.py`, and `examples/readme.md`.
- Edit `docs/foundation_tools.md` and `docs/foundation_abc.md`.
- Edit `.claude/CLAUDE.md`, `.claude/specs/socketTransact.md`, and `.claude/specs/transport_transaction_architecture.md`.
- Edit `.claude/plans/25-threaded-socket-transaction.md` to point future readers to this executed chunk set.

## Design constraints

- Export exactly the accepted types, including `InboundTransaction` and the three status enums; do not retain old aliases or deprecation wrappers.
- This is rip-and-tear work on pre-release code, not a user migration. Remove the legacy implementation outright with no compatibility layer.
- Do not change `foundation_abc.PeripheralByteTransport`; remove only the claim that this socket family implements it.
- Mark the old asyncio `socketTransact.md` contract superseded and link the accepted threaded umbrella. Update only the socket sections of the broader architecture spec.
- Rewrite examples as synchronous threaded usage. Keep benchmark intent but remove coroutine/event-loop/socket-async concurrency claims.
- Preserve `pytest-asyncio` and asyncio tooling used by non-socket packages.
- Delete old files only after resolving exact targets and confirming new replacements/tests exist.

## Cutover recipe

```text
verify every new module/test exists and is green
→ replace package exports
→ migrate import smoke tests/examples/docs/spec references
→ remove old tests and their private asyncio fixture
→ remove old production modules
→ grep for forbidden socket-family names/asyncio
→ run focused threaded suite and make fullCheck
```

## TDD and verification steps

1. Update import-surface tests first so they fail against the old `__init__.py` and assert every accepted export plus absence of old names.
2. Switch exports and migrate examples/docs/spec references.
3. Use `rg` to confirm the old test fixture has no non-deleted consumer, then remove the listed old tests and implementation files.
4. Run all `tests/test_*socket*`, `tests/test_transaction_*`, example import/compile checks, then `make fullCheck`.
5. Perform a final cleanup pass: delete any remaining legacy asyncio socket code, dead support code, tests, imports, exports, and aliases; make client and server usage clear in the examples and documentation; then rerun `make fullCheck`.

## Acceptance criteria

- [x] `rg -n "asyncio|async def|async with|await " src/foundation_tools/socket_transaction` is empty.
- [x] `rg -n "SocketByteTransport|TransactionRouter|SocketTransactResult|SocketTransactServer|DelimiterCodec|LengthPrefixedCodec" src/foundation_tools/socket_transaction docs examples .claude/CLAUDE.md .claude/specs/transport_transaction_architecture.md` is empty except deliberate historical/supersession text.
- [x] Fresh-process import tests expose every accepted public name and none of the removed names.
- [x] Both examples compile and use synchronous threaded APIs.
- [x] `[project].dependencies` remains empty and non-socket asyncio tests/tooling remain intact.
- [x] `make fullCheck` passes.

## Out of scope

- Compatibility shims, deprecation period, or import aliases.
- Editing archived plans or completed fix records.
- Removing asyncio from CLI/SSH/rsync or the asynchronous peripheral ABC.
- Performance tuning beyond keeping the benchmark runnable.

## Ask ↔ result

- **Objective (human_ask + goal):** the top-level `human_ask` explicitly wants the asyncio socket stack "ripped and teared" out of `src/foundation_tools/socket_transaction/` and reduced to threading + sockets; this chunk's `goal` is the atomic removal of the asyncio stack, publication of the threaded API, and elimination of doc/example drift.
- **Live authorization:** `/execute-plan .claude/plans/25-threaded-socket-transaction` — breaking changes explicitly authorized. This canon chunk file (`16-rip-and-tear-cleanup.md`) supersedes the earlier draft `16-public-cutover.md`, per the human's direct instruction that this file is canon.
- **Delivered:** `__init__.py` now exports exactly the accepted threaded surface (handlers, codecs, status enums, `InboundTransaction`, `TransactingSocketHandlerClient`/`Server`) with no old aliases; the six asyncio production modules and their six test files plus `tests/asyncio_server.py` were deleted; `tests/test_package_restructure.py` asserts every accepted export and the absence of every removed name; both examples were rewritten as synchronous threaded usage and compile/run; `docs/foundation_tools.md`, `docs/foundation_abc.md` (removed the `PeripheralByteTransport`-implements claim), `.claude/CLAUDE.md` (socket sentence only), `.claude/specs/socketTransact.md` (supersession notice), and `.claude/specs/transport_transaction_architecture.md` (socket sections only) were updated.
- **Verification (supervisor, firsthand):** both acceptance greps empty; all listed files deleted; examples `py_compile` clean; `[project].dependencies == []`; `pytest-asyncio` and non-socket asyncio tests intact; `make fullCheck` → 895 passed (down from 1026: the six deleted asyncio test files).
- **Gap:** none against the canon chunk. Note: the executing agent worked from this canon file after the human confirmed it supersedes the draft `16-public-cutover.md`; `PeripheralByteTransport` itself was left unchanged (only the "this family implements it" claim was removed), consistent with the async ABC being structurally incompatible with the synchronous threaded design.
