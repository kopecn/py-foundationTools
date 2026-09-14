---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Implement immutable transaction frames, stage statuses, and truthful outcomes.
last_updated: 2026-09-12
semver: 0.0.1
author: Nicholas Bergantz
status: completed
---

# 02 — Transaction values and outcomes

Scope: [summary goal](00-overview.md#summary-goal) · [original ask](00-original-ask.md) · Contract: [transaction frame and pending values](../../../specs/threadedTransactionProtocol.md#transaction-frame)

## Deliverable

Create the protocol value module containing `TransactionFrame`, `SendStatus`, `AckStatus`, `CompletionStatus`, and immutable `TransactionOutcome` without socket or transaction-core behavior.

## Depends on

None.

## Files

- Create `src/foundation_tools/socket_transaction/transaction_models.py`.
- Create `tests/test_transaction_models.py`.
- Do not export the types from package `__init__.py` yet; chunk 15 owns the atomic cutover.

## Design constraints

- Use frozen dataclasses and stdlib enums; no external dependencies.
- `TransactionFrame.payload` accepts only `bytes | str | dict[str, object] | None`.
- `TransactionOutcome.events` is a tuple, never a caller-owned mutable list.
- `success` is a derived read-only property: send must be `SENT`; `NOT_REQUESTED` stages are neutral; a requested ACK succeeds only as `ACKNOWLEDGED`; requested completion succeeds only as `RESULT`.
- Keep ACK and completion diagnostics separate so mixed outcomes such as ACK timeout plus result success remain truthful.

## TDD steps

1. Add failing tests for every enum member, frozen mutation rejection, event tuple immutability, and the full `success` truth table.
2. Implement the values exactly as named in the accepted protocol spec.
3. Run `pytest tests/test_transaction_models.py` and `make fullCheck`.

## Acceptance criteria

- [x] Mutation of a frame or outcome raises `FrozenInstanceError`.
- [x] Fire-and-forget `SENT` is successful; `NOT_CONNECTED` and `FAILED` are not.
- [x] ACK-timeout plus `RESULT` is representable and unsuccessful without corrupting the result frame.
- [x] `transaction_models.py` imports neither `socket` nor `asyncio`.
- [x] `make fullCheck` passes.

## Out of scope

- Codec serialization.
- Mutable pending transaction state.
- Package exports and compatibility aliases.

## Ask ↔ result

- **Objective (`human_ask` + `goal`):** the top-level ask directed reducing the asyncio socket stack to threading/sockets via bite-sized tasks; this chunk's recorded goal was to implement immutable transaction frames, stage statuses, and truthful outcomes.
- **Live request:** `/execute-plan .claude/plans/25-threaded-socket-transaction`, explicitly authorizing execution of this chunk now.
- **Delivered:** `src/foundation_tools/socket_transaction/transaction_models.py` with `TransactionFrame` (frozen dataclass), `SendStatus`, `AckStatus`, `CompletionStatus` (stdlib enums), and immutable `TransactionOutcome` (frozen dataclass, `events` coerced to an immutable tuple in `__post_init__`, derived `success` property implementing the truth table from `threadedTransactionProtocol.md`). `tests/test_transaction_models.py` covers every enum member, frozen-mutation rejection on both types, tuple coercion/immutability of `events`, the full `success` truth table (including ACK-timeout + `RESULT`), and a no-`socket`/no-`asyncio`-import assertion via AST inspection. Neither type is exported from `__init__.py`. 27 new tests pass; `make fullCheck` passes (flake8, strict mypy over `src`+`tests`, pytest 654 passed).
- **Gap:** none identified against this chunk's scope. `TransactionFrame` does not runtime-validate non-empty `msg_type`/non-bool `tx_id`/`code` — the protocol spec places that validation at the codec's `decode` boundary (explicitly out of scope for this chunk), not on the frame constructor itself.
