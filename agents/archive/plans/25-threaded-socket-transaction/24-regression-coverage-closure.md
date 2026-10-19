---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Close the remaining source-authorized regression gaps without asserting unsupported contract decisions.
last_updated: 2026-09-13
semver: 0.1.0
author: Nicholas Bergantz
status: completed
---

# 24 - Close regression coverage gaps

Scope: [summary goal](00-corrective-overview.md#summary-goal) · [original ask](00-original-ask.md) · Contracts: [threaded architecture](../../../specs/threadedSocketTransaction.md), [transport](../../../specs/threadedSocketTransport.md), and [transaction facade](../../../specs/transactingSocketHandlers.md)

## Origin

PA25-08: the audit confirmed implemented source-authorized behaviors whose existing tests do not establish the claimed boundary, plus chunk 16's missing fresh-process cutover verification.

## Deliverable

Add deterministic regression coverage for the remaining authorized behavior gaps after chunks 17-23, without changing production code unless a new test exposes a separate defect that must be returned for a contract decision.

## Depends on

17-23.

## Files

- Edit `tests/test_socket_handler.py`.
- Edit `tests/test_socket_handler_server.py`.
- Edit `tests/test_binary_framed_socket_handler_client.py`.
- Edit `tests/test_transaction_core.py`.
- Edit `tests/test_threaded_socket_transaction_integration.py`.
- Edit `tests/test_package_restructure.py`.

## Design constraints

- Use only Events, Barriers, Conditions, bounded queues, and bounded joins; no sleeps or randomized correctness timing.
- Assert malformed UTF-8 replacement, incomplete text discard on epoch change, close-observer exception containment, and raw-callback failure not blocking text delivery from the same chunk.
- Assert accept-worker daemon/name and effective polling timeout, plus binary invalid-progress logging, buffer clearing, and later same-epoch recovery.
- Exercise `None` ACK and completion waits by waking them through deterministic routing or epoch failure; never leave an unbounded test worker.
- Strengthen simultaneous bidirectional E2E to assert every requested ACK/result stage and observe controlled reverse completion order.
- Run cutover verification in a fresh interpreter: exact `__all__`, every accepted import, removed submodule import failures, no old aliases, and `[project].dependencies == []`.
- Do not add exhaustive typed-outcome or encode-validation assertions for claims listed as recorded/no-action in the overview.

## Fresh-process recipe

```python
completed = subprocess.run(
    [sys.executable, "-c", "import foundation_tools.socket_transaction as package; ..."],
    check=False,
    capture_output=True,
    text=True,
)
assert completed.returncode == 0, completed.stderr
```

Use explicit environment setup matching the package test convention; do not trust the already-imported pytest process.

## TDD steps

1. Add each named test and verify it fails if its protected behavior is deliberately removed or bypassed.
2. Keep the changes test-only; if a new production defect appears, stop and report it rather than folding a fix into this chunk.
3. Run all six focused files.
4. Run `make fullCheck`.

## Acceptance criteria

- [x] Every behavior named in Design constraints has a direct assertion.
- [x] Simultaneous E2E proves ACK success, result success, distinct IDs, and controlled reverse completion.
- [x] Fresh-process cutover verification covers exact exports, removed modules, old aliases, and zero runtime dependencies.
- [x] No new correctness test uses sleeps, randomness, or an unbounded worker join.
- [x] `make fullCheck` passes.

## Out of scope

- Unsupported outcome-invariant and encode-validation decisions.
- Performance or flake benchmarking.
- New production behavior not exposed by an authorized contract.

## Ask ↔ result

**Objective.** The chunk's recorded `human_ask` is the plan-25 planning-phase ask (decompose the top-level threaded-socket spec into bite-sized chunks; no asyncio). The chunk's own `goal` narrows that to: close the source-authorized regression-coverage gaps confirmed by the PA25-08 audit, without asserting any of the "Recorded, no action" contract decisions in `00-overview.md`. These do not disagree about the objective itself.

**Authorization for this run.** The live user command explicitly invoked `/execute-plan 17 ... 25` and confirmed chunks 17-23 are already completed and committed; this chunk (24) was executed on that explicit instruction, building on the current committed state.

**Delivered.** Added regression coverage, test-only, across the six files named in Design constraints:

- `tests/test_socket_handler.py`: malformed-UTF-8 replacement (`TestMalformedUtf8Replacement`), incomplete-text discard across an epoch change (`TestIncompleteTextDiscardOnEpochChange`), close-observer (`on_epoch_closed`) exception containment (`TestCloseObserverExceptionContainment`), and raw-handler failure not blocking a text token decoded from the *same* chunk (`TestRawCallbackFailureDoesNotBlockSameChunkTextDelivery`).
- `tests/test_socket_handler_server.py`: accept-worker daemon/name (`test_accept_worker_is_a_named_daemon_thread`) and the configured `accept_poll_interval` actually reaching `listener.settimeout` (`test_listener_socket_receives_the_configured_accept_poll_interval_as_its_timeout`), both in `TestAcceptWorkerDaemonNameAndEffectivePollTimeout`.
- `tests/test_binary_framed_socket_handler_client.py`: `TestInvalidProgressLoggingAndSameEpochRecovery` stages a genuinely persisted partial-frame buffer, forces invalid progress, asserts both log messages, and proves a later frame on the same epoch decodes cleanly (not corrupted by a stale, uncleared buffer).
- `tests/test_transaction_core.py`: `TestNoneTimeoutWaitsWokenDeterministically` exercises `wait_ack`/`wait_completion` called with `timeout=None` (the unbounded public wait), woken deterministically via the real `route()`/`fail_epoch()` production paths rather than the file's private `_settle_*` test-only shortcuts, each with a single bounded `WorkerHandle.join`.
- `tests/test_threaded_socket_transaction_integration.py`: strengthened `TestSimultaneousBidirectionalTransactions` to assert every requested ACK/result stage (`ack_status`/`completion_status`/`result`) for both transactions, distinct tx_ids, and a deterministic reverse reply-issuance order (gated on a local "reply sent" event rather than on full round-trip completion, which this scenario's single-receive-thread-per-side design cannot order without first releasing both sides).
- `tests/test_package_restructure.py`: `TestFreshProcessCutoverVerification` runs four `subprocess`-isolated, fresh-interpreter checks (exact `__all__` + every accepted name importable; every removed submodule fails to import; no old asyncio alias remains; `[project].dependencies == []`), each with an explicit `PYTHONPATH=<repo>/src` rather than trusting the already-imported pytest process.

Every new test was verified to fail when its protected behavior was deliberately removed or bypassed (see TDD step 1), then to pass against current code. `make fullCheck` passes: flake8 clean, mypy clean, 934/934 tests pass (up from 895), stable across repeated runs.

**Gap.** None against the chunk as written. No new production defect was found; no production file was touched.
