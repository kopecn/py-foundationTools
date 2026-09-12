---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Implement the transaction codec protocol and strict newline-delimited JSON codec.
last_updated: 2026-09-12
semver: 0.0.1
author: Nicholas Bergantz
status: completed
---

# 03 — Transaction codec protocol and JSON codec

Scope: [summary goal](00-overview.md#summary-goal) · [original ask](00-original-ask.md) · Contract: [codec protocol and JSON codec](../../specs/threadedTransactionProtocol.md#codec-protocol)

## Deliverable

Create `TransactionCodec` and `JsonTransactionCodec`, producing and consuming complete newline-terminated transaction messages.

## Depends on

02 transaction values.

## Files

- Create `src/foundation_tools/socket_transaction/transaction_codecs.py`.
- Create `tests/test_transaction_codecs.py`.

## Design constraints

- The protocol exposes `delimiter`, `encode`, and `decode`; it is structural typing only, not runtime-checkable.
- JSON decode requires an object with `tx_id`, `msg_type`, and `code`; missing fields never default.
- Reject booleans for numeric fields, require non-empty string `msg_type`, and wrap malformed JSON/type/numeric failures as `ValueError`.
- `DataModelHelper` payloads call `to_dict`; bytes decode UTF-8 with replacement; strings remain strings; `None` omits the payload field.
- Accept decode input with or without one trailing newline. Do not strip meaningful JSON string content.

## TDD steps

1. Add failing protocol-shape and round-trip tests for no payload, model, bytes, string, and dictionary decoded payload.
2. Add malformed matrices for JSON syntax, non-object roots, missing fields, booleans/nonnumeric values, empty/non-string message types, and invalid payload shapes.
3. Implement the protocol and JSON codec.
4. Run `pytest tests/test_transaction_codecs.py -k json` and `make fullCheck`.

## Acceptance criteria

- [x] Encoded output is UTF-8 bytes ending in exactly one newline.
- [x] All required-field and type failures raise `ValueError`.
- [x] Invalid byte payload sequences visibly use replacement rather than raising.
- [x] No transport, threading, or socket import appears in `transaction_codecs.py`.
- [x] `make fullCheck` passes.

## Out of scope

- Angle-bracket encoding.
- TCP delimiter reconstruction.
- Transaction routing or payload model decoding.

## Ask ↔ result

- **Objective (`human_ask` + `goal`):** the top-level ask directed reducing the asyncio socket stack to threading/sockets via bite-sized tasks; this chunk's recorded goal was to implement the transaction codec protocol and the strict newline-delimited JSON codec. The two agree; no conflict.
- **Live request:** `/execute-plan .claude/plans/25-threaded-socket-transaction`, explicitly authorizing execution of this chunk now.
- **Delivered:** `src/foundation_tools/socket_transaction/transaction_codecs.py` with `TransactionCodec` (a plain `typing.Protocol`, not `@runtime_checkable` — structural conformance only, verified via `_is_protocol` and a raised `TypeError` on `isinstance()`) and `JsonTransactionCodec` implementing `delimiter` (`"\n"`), `encode`, and `decode`. Encode omits `payload` for `None`, calls `to_dict()` for `DataModelHelper` payloads, decodes `bytes` payloads as UTF-8 with `errors="replace"`, and passes `str` through unchanged; output is `json.dumps(...) + "\n"` encoded as UTF-8. Decode accepts `bytes` or `str` with or without a trailing newline, requires `tx_id`/`msg_type`/`code` with no defaults, rejects a non-object JSON root, converts `tx_id`/`code` with `int()` while explicitly rejecting booleans first, requires a non-empty string `msg_type`, and restricts a present `payload` to string/object/null — wrapping all JSON syntax, UTF-8 decode, missing-field, and validation failures as `ValueError`. `tests/test_transaction_codecs.py` (40 tests) covers protocol shape, round trips for no/model/bytes/string/dict-decoded payloads, and the malformed matrix (syntax, non-object roots, missing fields, booleans, nonnumeric fields, empty/non-string `msg_type`, invalid payload shapes), plus an AST-based assertion that the module imports neither `socket`, `asyncio`, nor `threading`. `make fullCheck` passes: flake8 clean, strict mypy clean over 65 `src` files and 41 test files, pytest 694 passed (up from 654 before this chunk).
- **Gap:** none identified against this chunk's scope. `encode`'s runtime type-mismatch guard (`TypeError` for a payload outside `DataModelHelper | bytes | str | None`) is a defensive parallel to existing `DataModelHelper` converter conventions (e.g. `to_class`), not a spec-mandated behavior — the type checker is the primary enforcement per the protocol's type hints.
