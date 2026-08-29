---
plan: Fix03SocketRouterFailureContainment
scope: project
status: needs-approval
last_updated: 2026-08-28
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
