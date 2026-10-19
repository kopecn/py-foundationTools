---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Normalize every JSON numeric conversion failure to ValueError so malformed tokens stay inside the receive error boundary.
last_updated: 2026-09-13
semver: 0.1.0
author: Nicholas Bergantz
status: completed
---

# 22 - Normalize JSON numeric failures

Scope: [summary goal](00-corrective-overview.md#summary-goal) · [original ask](00-original-ask.md) · Contract: [codec failure boundary](25-threaded-socket-transaction.md#4-transactioncodec) and [JSON codec](../../../specs/threadedTransactionProtocol.md#json-codec)

## Origin

PA25-06: `JsonTransactionCodec.decode('{"tx_id": Infinity, ...}')` raises uncaught `OverflowError`, while malformed codec input is required to raise `ValueError` and the transaction receive pipeline catches only `ValueError`.

## Deliverable

Make JSON numeric conversion wrap `OverflowError` alongside the existing conversion failures, with tests for every affected required numeric field and the facade malformed-token path.

## Depends on

None.

## Files

- Edit `src/foundation_tools/socket_transaction/transaction_codecs.py`.
- Edit `tests/test_transaction_codecs.py`.
- Edit `tests/test_transacting_socket_handler.py`.

## Design constraints

- Preserve Python `int()` conversion for otherwise supported integer, float, and numeric-string values.
- Reject non-finite JSON numbers through the existing public `ValueError` boundary; do not allow `OverflowError` to escape.
- Do not change missing-field, Boolean, payload-shape, or encode-time validation policy in this chunk.
- The facade test must prove malformed raw-token passthrough still runs after this specific conversion failure.

## TDD steps

1. Add failing decode cases for positive/negative infinity in both `tx_id` and `code`.
2. Add a facade regression proving the original token reaches the string callback and no frame is routed.
3. Extend only the numeric conversion exception normalization.
4. Run `pytest tests/test_transaction_codecs.py tests/test_transacting_socket_handler.py` and `make fullCheck`.

## Acceptance criteria

- [x] Every non-finite JSON numeric field raises `ValueError`, never `OverflowError`.
- [x] The transaction receive path logs the malformed token and still invokes string passthrough.
- [x] Existing valid numeric conversion behavior remains unchanged.
- [x] `make fullCheck` passes.

## Out of scope

- Encode-time Boolean or empty-message-type validation.
- JSON parser strictness for nonstandard constants beyond normalizing the public error category.
- Angle-bracket codec behavior.

## Ask ↔ result

**Objective (human_ask + goal):** the original human ask designated the top-level socket spec as the source to decompose into threading-only chunks; this chunk's `goal` — normalize every JSON numeric conversion failure to `ValueError` so malformed tokens stay inside the receive error boundary — was set during that planning-phase decomposition, not disputed by the live instruction. The live execution request (`/execute-plan 17 ... 25 these were from a post audit`) explicitly authorizes running this and the other post-audit chunks now; it does not change the objective itself, so no ask/goal conflict exists.

**Source verification:** confirmed before implementing, not assumed. The top-level plan, §4 TransactionCodec ("Reject malformed input with `ValueError`") and `.claude/specs/threadedTransactionProtocol.md` §"JSON codec" ("raise `ValueError` for malformed JSON, the wrong top-level or payload shape, missing required fields, or failed field validation") and §"Codec protocol" ("raise `ValueError` for malformed syntax or identifier/code values that `int` cannot convert") both require `ValueError` for this case, with no carve-out for `OverflowError`. `PA25-06`'s claim — that `int(float("inf"))` escapes as an uncaught `OverflowError` — was reproduced firsthand against the pre-fix code.

**Delivered:**
- `src/foundation_tools/socket_transaction/transaction_codecs.py`: `_decode_numeric_field` now also catches `OverflowError` alongside `TypeError`/`ValueError` and re-raises as `ValueError`, preserving the existing message format. One-line change; no other validation policy touched.
- `tests/test_transaction_codecs.py`: four new failing-first cases (`test_decode_rejects_positive_infinity_tx_id`, `test_decode_rejects_negative_infinity_tx_id`, `test_decode_rejects_positive_infinity_code`, `test_decode_rejects_negative_infinity_code`), each confirmed to fail with an escaping `OverflowError` before the fix.
- `tests/test_transacting_socket_handler.py`: `test_non_finite_numeric_field_skips_routing_but_still_reaches_the_string_handler` proves the malformed (`Infinity`-bearing) raw token still reaches `set_string_message_handler` unchanged and never reaches the inbound-transaction handler, mirroring the existing invalid-JSON facade test.
- `make fullCheck` (flake8 + strict mypy over `src/`+`tests/` + pytest): green, 910 tests passed.

**Gap:** none identified against this chunk's scope. Boolean/missing-field/payload-shape/encode-time validation policy was left untouched, per "Out of scope."
