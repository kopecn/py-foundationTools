---
plan: Fix12SocketLifecycleOwnership
scope: project
status: needs-approval
last_updated: 2026-09-05
semver: 1.1.0
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

## Session note — 2026-09-05 (not executed; behavior captured for scoping)

Status held at `needs-approval`. No implementation this session. The user judged this
likely too complex to close inline; the intended behavior is recorded below to seed a
dedicated execution plan that then goes to council review.

Intended lifecycle behavior (user, 2026-09-05):

- **Raw socket handle** — destroy and recreate on close. A closed Python socket cannot
  be reused; the fix must not attempt to restart the same handle.
- **In-domain objects** (`TransactionRouter`, `SocketTransact`, `SocketTransactServer`,
  transport wrapper) — maintain continuity across an *involuntary* dropout through the
  connect / disconnect / reconnect cycle. Reconnection and upper-layer continuity are
  preserved; upper layers are buffered from having to handle the dropout at all.
- **Explicit client `disconnect()`** — clear residual transport data (pending/in-flight
  buffers), but retain the connection characteristics / parameterization. Not building
  polymorphic sockets here (noted as a separate interesting idea).
- **Server shutdown request** — destroy the handle, keep parameterization / configuration,
  delete any pending socket data.
- **Server dropout** — maintain reconnection and preserve continuity, buffering upper
  layers, same as the client dropout case.

Distinction that drives the state model: *involuntary dropout* → preserve continuity and
auto-reconnect; *explicit disconnect/shutdown* → tear down the handle and pending data,
keep configuration. This still needs a scoped execution plan (state representation, legal
transitions across all four types, `is None` dependency defaults, numeric-config validation
at construction) before any code is written.
