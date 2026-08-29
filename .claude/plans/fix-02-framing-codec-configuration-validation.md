---
plan: Fix02FramingCodecConfigurationValidation
scope: project
status: needs-approval
last_updated: 2026-08-28
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
