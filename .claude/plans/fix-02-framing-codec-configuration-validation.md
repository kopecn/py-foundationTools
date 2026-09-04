---
plan: Fix02FramingCodecConfigurationValidation
scope: project
status: complete
last_updated: 2026-09-04
semver: 1.0.0
author: Nicholas Bergantz
---

# Fix candidate 02 — non-progressing framing configurations

Evidence: `DelimiterCodec(b"")` and `LengthPrefixedCodec(prefix_width=0)` can loop
without consuming input. Negative or unrepresentable `max_frame_size` values are also
invalid constructor state.

Minimum fix: reject those values in constructors with `ValueError`; cover invalid and
boundary-valid inputs in `tests/test_framing_codecs.py`; run the gate.

Do not change framing formats, outbound behavior, router policy, or defaults.

## Ask ↔ result

- **Objective:** reject non-progressing / unrepresentable framing-codec constructor configs.
- **Authorized by:** `/execute-plan please proceed` (user approved all of fix-01–07).
- **Delivered:** `DelimiterCodec` rejects `b""`; `LengthPrefixedCodec` rejects `prefix_width < 1` and `max_frame_size` that is negative or exceeds the prefix's max representable value — all `ValueError` in the constructor. 9 new tests in `tests/test_framing_codecs.py` (invalid + boundary-valid, incl. `max_frame_size==max_representable` and `==0` accepted). Confirmed failing pre-fix.
- **Gate:** `make uv-fullCheck` — ruff/mypy clean, 496 passed.
- **Gap:** negative `prefix_width` is also rejected (plan named only zero) — same invalid-state class; previously raised an opaque native error, now a clear message. No formats/outbound/policy/defaults changed.
