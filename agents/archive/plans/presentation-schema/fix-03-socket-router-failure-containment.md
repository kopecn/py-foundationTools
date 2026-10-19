---
plan: Fix03SocketRouterFailureContainment
scope: project
status: complete
last_updated: 2026-09-04
semver: 1.0.0
author: Nicholas Bergantz
---

# Fix candidate 03 — router failure containment

Evidence: exceptions from codec feeding or transaction-ID extraction can escape the
reader task, leaving pending requests unresolved and making shutdown re-raise.

Minimum fix: route ordinary frame-processing exceptions through the router's existing
teardown path; preserve cancellation; verify one pending request, unsolicited-stream
closure, and clean idempotent stop/disconnect.

Do not add reconnect, retry, bad-frame recovery, or protocol-specific replies.

## Ask ↔ result

- **Objective:** contain frame-processing exceptions so they don't orphan pending requests or make shutdown re-raise.
- **Authorized by:** `/execute-plan please proceed` (user approved all of fix-01–07).
- **Delivered:** wrapped the `codec.feed`/`_dispatch` block in `_reader_loop` (`transaction_router.py`, +11 lines) and routed failures through the existing `_teardown(ConnectionClosedError(...))` path — the same one used for transport-level loss. Catches `Exception`, not `BaseException`, so `asyncio.CancelledError` still propagates. 3 new tests (codec-feed fault fails pending + closes unsolicited stream; extractor fault fails pending; idempotent stop after fault), confirmed failing pre-fix.
- **Gate:** `make uv-fullCheck` — ruff/mypy clean, 499 passed.
- **Gap:** none. No reconnect/retry/recovery/protocol replies added.
