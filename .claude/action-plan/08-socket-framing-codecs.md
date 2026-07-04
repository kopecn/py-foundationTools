---
plan: ActionPlan08SocketFramingCodecs
scope: project
status: pending
last_updated: 2026-07-03
semver: 0.0.1
author: Nicholas Bergantz
---

# 08 — Socket Framing Codecs

## Goal

Implement the pluggable framing layer: the `FramingCodec` protocol plus
`DelimiterCodec` and `LengthPrefixedCodec`.

Contract: Layer 2 of [socketTransact.md](../specs/socketTransact.md).

## Depends on

05 (byte transport — for integration tests; the codec module itself is standalone).

## Files

- `src/foundation_tools/socket_transaction/framing_codecs.py`
- `src/foundation_tools/socket_transaction/__init__.py` (add exports)
- `tests/test_framing_codecs.py`

## Design constraints

- `FramingCodec` as a `typing.Protocol`: `encode(payload: bytes) -> bytes`,
  `feed(data: bytes) -> list[bytes]`. State limited to the reassembly buffer.
- `DelimiterCodec`: configurable delimiter (default `\n`); payloads containing the
  delimiter are a caller error → `ValueError` at encode time.
- `LengthPrefixedCodec`: configurable prefix width/endianness (default 4-byte
  big-endian unsigned); oversized payload or malformed inbound length →
  `ValueError`.
- Codecs frame bytes only; model conversion composes on top via
  `DataModelHelper.to_wire`/`from_wire` (no serialization logic inside codecs).

## Steps (TDD)

1. Tests first: single-frame round trip; multi-frame in one chunk; frame split
   across many chunks (byte-at-a-time feed); empty payloads; delimiter-in-payload
   encode error; malformed length error; buffer survives interleaved calls.
2. Wire-bridge round trip: a schema-generated `DataModelHelper` model with
   `wire_encode`/`wire_decode` configured → `to_wire` → codec encode → feed →
   `from_wire` equals the original model.
3. Implement both codecs.
4. `make fullCheck`.

## Acceptance criteria

- [ ] Both codecs satisfy the protocol (structural check in tests).
- [ ] Partial-delivery reassembly proven by byte-at-a-time tests.
- [ ] Wire-bridge round trip passes with a real generated model.
- [ ] `make fullCheck` passes.

## Out of scope

- Checksums/BCC/escape-sequence framing (add as new codecs when a device needs
  them).
- tx_id semantics (chunk 09).
