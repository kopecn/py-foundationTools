---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Add the strict textual angle-bracket transaction codec.
last_updated: 2026-09-12
semver: 0.0.1
author: Nicholas Bergantz
status: completed
---

# 04 — Angle-bracket transaction codec

Scope: [summary goal](00-overview.md#summary-goal) · [original ask](00-original-ask.md) · Contract: [angle-bracket codec](../../specs/threadedTransactionProtocol.md#angle-bracket-codec)

## Deliverable

Add `AngleBracketTransactionCodec` to the codec module and complete its isolated tests.

## Depends on

03 transaction codec protocol and JSON codec.

## Files

- Edit `src/foundation_tools/socket_transaction/transaction_codecs.py`.
- Edit `tests/test_transaction_codecs.py`.

## Design constraints

- Encode `<tx_id,msg_type,code[,payload]>\n`; omit the fourth field only for `None`.
- Split decode input at no more than the first three commas so payload commas survive verbatim.
- Reject empty message types and message types containing comma, CR, or LF.
- Reject payload text containing CR or LF; internal `>` and commas remain legal payload text.
- Convert model `to_bytes()` and byte payloads through UTF-8 replacement exactly as the accepted spec requires.

## TDD steps

1. Add failing no-payload/payload/model/bytes/string round trips, including payload commas.
2. Add failures for missing brackets/fields, invalid integers, empty type, comma-bearing type, and CR/LF injection.
3. Implement the codec without changing JSON behavior.
4. Run `pytest tests/test_transaction_codecs.py` and `make fullCheck`.

## Acceptance criteria

- [x] No-payload output is exactly `<id,type,code>\n`.
- [x] The fourth field preserves all commas.
- [x] Every ambiguous or message-injecting input raises `ValueError` before bytes are emitted.
- [x] All JSON codec tests remain unchanged and green.
- [x] `make fullCheck` passes.

## Out of scope

- Escaping rules or binary-safe transaction payloads.
- Custom transaction codecs.
- Package exports.

## Ask ↔ result

- **Objective (`human_ask` + `goal`):** the top-level ask directed reducing the asyncio socket stack to threading/sockets via bite-sized tasks; this chunk's recorded goal was to add the strict textual angle-bracket transaction codec. The two agree; no conflict.
- **Live request:** `/execute-plan .claude/plans/25-threaded-socket-transaction`, explicitly authorizing execution of this chunk now.
- **Delivered:** `AngleBracketTransactionCodec` added to `src/foundation_tools/socket_transaction/transaction_codecs.py`, implementing `delimiter` (`"\n"`), `encode`, and `decode` per `.claude/specs/threadedTransactionProtocol.md#angle-bracket-codec`. `encode` rejects an empty `msg_type` or one containing comma/CR/LF, converts `DataModelHelper` payloads via `to_bytes()` decoded UTF-8 with replacement, bytes the same way, and passes strings through, then rejects CR/LF in the resulting payload text — all validation happens before any bytes are built, so a rejected input never emits partial/ambiguous output (`test_encode_no_bytes_emitted_on_rejected_msg_type`). Output is exactly `<tx_id,msg_type,code>\n` with no payload, or `<tx_id,msg_type,code,payload>\n` with one, with `tx_id`/`code` via plain `str()`. `decode` strips surrounding whitespace, requires `<`/`>` wrapping, splits the inner text with `str.split(",", 3)` so at most three commas are consumed (payload commas and internal `>` survive verbatim), requires at least three fields and a non-empty `msg_type`, and converts `tx_id`/`code` with `int()`, raising `ValueError` on any structural or field failure. `tests/test_transaction_codecs.py` gained 33 new tests (`TestAngleBracketTransactionCodecDelimiter/Encode/RoundTrip/Malformed`) covering the exact no-payload wire form, comma-preserving and angle-bracket-preserving payloads, model/bytes/string payload conversions, CR/LF and comma injection rejection in both `msg_type` and payload, round trips, and malformed-structure decode failures — all 40 pre-existing JSON codec tests are unchanged and still green. `make fullCheck` passes: flake8 clean, strict mypy clean over 65 `src` files and 41 test files, pytest 727 passed (up from 694 before this chunk).
- **Gap:** none identified against this chunk's scope. Unsupported payload types (anything other than `DataModelHelper | bytes | str | None`) raise `TypeError` via `_angle_encode_payload`, mirroring the existing JSON codec's `_encode_payload` guard — a defensive parallel, not a spec-mandated behavior; the type checker is the primary enforcement per the protocol's type hints. No escaping rules, custom codecs, or package exports were added, per Out of scope.
