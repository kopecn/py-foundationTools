---
plan: Fix02FramingCodecConfigurationValidation
scope: project
status: pending
last_updated: 2026-08-23
semver: 0.0.1
author: Nicholas Bergantz
---

# Fix 02 — Framing-Codec Configuration Validation

## Goal

Reject codec configurations that cannot make parser progress, preventing
constructor-valid states from turning `feed()` into an infinite loop.

Contract: [socketTransact.md](../specs/socketTransact.md), Layer 2.

## Depends on

Fix 01 only in preferred landing order. There is no code dependency.

## Defects

- `DelimiterCodec(delimiter=b"")`: `bytearray.find(b"")` always returns zero and
  deleting a zero-length delimiter never shrinks the buffer.
- `LengthPrefixedCodec(prefix_width=0)`: a zero-byte prefix decodes forever while
  consuming no bytes.

Both configurations can consume a CPU indefinitely inside `feed()`.

## Files

Edit:

- `src/foundation_tools/socket_transaction/framing_codecs.py`
- `tests/test_framing_codecs.py`
- `HISTORY.md`

## Design constraints

**Fail at construction.** Validate once in each constructor. `feed()` must not carry
defensive branches for impossible object state.

**Constructor invariants.** Enforce:

- delimiter is non-empty;
- `prefix_width >= 1`;
- `max_frame_size`, when supplied, is non-negative and no greater than the largest
  value representable by the prefix.

Keep `max_frame_size=0` valid: it is a useful codec that accepts only empty inbound
frames. Preserve the current contract that `max_frame_size` bounds inbound declarations;
do not silently change outbound `encode()` behavior in this fix.

**Deterministic errors.** Raise `ValueError` with the invalid field name and value.

## Steps (TDD)

1. Add constructor tests for an empty delimiter, zero/negative prefix widths, negative
   `max_frame_size`, and a maximum larger than the prefix can represent. Each test
   expects `ValueError`; no test should call a known-hanging `feed()` in-process.
2. Add boundary tests proving a one-byte prefix and `max_frame_size=0` remain valid.
3. Implement constructor validation.
4. Re-run `tests/test_framing_codecs.py`.
5. Add an `[Unreleased]` `Fixed` bullet describing the rejected non-progressing codec
   configurations.
6. Run `make uv-fullCheck`.

## Acceptance criteria

- [ ] `DelimiterCodec(b"")` raises immediately.
- [ ] `LengthPrefixedCodec(prefix_width=0)` and negative widths raise immediately.
- [ ] Invalid `max_frame_size` bounds raise immediately.
- [ ] Existing valid round trips, empty payloads, and custom delimiters still pass.
- [ ] No loop in `feed()` needs a special zero-progress escape hatch.
- [ ] `make uv-fullCheck` passes.

## Out of scope

- Escaping delimiters inside payloads.
- Checksums, compression, or new framing formats.
- Changing the default maximum frame size.
- Router handling of a valid codec raising on malformed wire data; fix 03 owns that.

