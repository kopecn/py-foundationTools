---
plan: ActionPlan08SocketFramingCodecs
scope: project
status: complete
last_updated: 2026-07-05
semver: 0.1.0
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

- [x] Both codecs satisfy the protocol (structural check in tests).
- [x] Partial-delivery reassembly proven by byte-at-a-time tests.
- [x] Wire-bridge round trip passes with a real generated model.
- [x] `make uv-fullCheck` passes (`make fullCheck` no longer exists).

## Out of scope

- Checksums/BCC/escape-sequence framing (add as new codecs when a device needs
  them).
- tx_id semantics (chunk 09).

## Implementation notes

"Malformed inbound length" needed a concrete definition: an unsigned length
prefix can never decode to something structurally invalid, so the only realistic
malformed/corrupt case is a declared length that would force unbounded
reassembly-buffer growth (e.g. a bit-flipped or malicious prefix). Added an
opt-in `max_frame_size` constructor parameter (default: the largest value
`prefix_width` can represent, i.e. no extra restriction) — when a declared length
exceeds it, `feed` raises immediately instead of buffering forever waiting for
bytes that will never arrive.

The wire-bridge round-trip test used `GeoCoordinate` (an existing schema-generated
model) with `wire_encode`/`wire_decode` monkeypatched in for the test only, since
no `wire_config.py` wiring exists in the repo yet — `DataModelHelper.to_wire`
looks up `type(self).wire_encode`/`cls.wire_decode` as plain (unbound) callables,
so the monkeypatched lambdas must NOT be wrapped in `staticmethod`/`classmethod`
or the internal `encoder(self, **kwargs)` / `decoder(cls, wire_str)` call sites
would double-supply `self`/`cls`.
