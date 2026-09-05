---
plan: Fix12SocketLifecycleOwnership
scope: project
status: needs-approval
last_updated: 2026-09-04
semver: 1.0.0
author: Nicholas Bergantz
---

# Fix candidate 12 — socket lifecycle and resource ownership

Evidence: a completed router reader task remains non-`None`, so `start()` refuses to
restart it; `_closed` is never reset; repeated transport `connect()` and server `start()`
calls can overwrite live resources. Constructors also use truthiness for injected codec,
transport, generator, and concurrency values, conflating `None` with valid falsy objects
or with zero/unbounded policy.

Minimum fix: choose and document either a reusable lifecycle or an explicitly one-shot
lifecycle, represent its states, and enforce legal transitions consistently across
`SocketByteTransport`, `TransactionRouter`, `SocketTransact`, and `SocketTransactServer`.
Close or reject duplicate live resources, use `is None` for dependency defaults, and
validate numeric configuration at construction.

Do not partially advertise reconnect support, silently replace live sockets, or add retry
policy. Keep transaction registration atomicity in `fix-09` independently testable.
