---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Replace the asyncio socket stack with a synchronous, threaded client/server transaction family through small delegated execution chunks.
last_updated: 2026-09-13
semver: 0.3.0
author: Nicholas Bergantz
status: completed
---

# Plan 25 execution overview — threaded socket transaction

## Summary goal

Replace `src/foundation_tools/socket_transaction/` with a standard-library IPv4 TCP stack built directly on `socket` and `threading`, covering raw and framed transport, one-client server lifecycle, transaction codecs/state/routing, synchronous client and server facades, and complete removal of the pre-release asyncio socket API. Success means the accepted threaded specifications are implemented, deterministic tests cover the concurrency boundaries, no socket module depends on `asyncio`, and `make fullCheck` passes.

## Original ask

The complete initiating request and subsequent planning clarifications are preserved in [00-original-ask.md](00-original-ask.md).

## Accepted contracts

- [Threaded socket architecture](../../../specs/threadedSocketTransaction.md)
- [Threaded transport](../../../specs/threadedSocketTransport.md)
- [Transaction protocol](../../../specs/threadedTransactionProtocol.md)
- [Transacting handlers](../../../specs/transactingSocketHandlers.md)

The source scaffold remains at [25-threaded-socket-transaction.md](25-threaded-socket-transaction.md). This executed chunk set implemented the accepted sibling specs, not the superseded asyncio behavior recorded historically in `.claude/specs/socketTransact.md`.

## Usability north star

A synchronous caller supplies a logger and codec, connects or listens, calls `send_transaction`, and receives one truthful immutable outcome. Remote requests arrive with an epoch-bound responder that cannot reply to a replacement peer. Raw/framed users may work at the lower handler layer without learning transaction internals; no caller needs an event loop.

## Chunk dependency graph

```text
01 deterministic thread/socket test support
├── 07 socket lifecycle + send → 08 receive + text dispatch → 09 client
│                                                 ├──────→ 10 server listener → 11 admission/replacement
│                                                 └──────→ 12 binary-framed client
└────────────────────────────────────────────────────────────────────────────┐
                                                                             │
02 transaction values → 03 codec + JSON → 04 angle codec                    │
         └──────────────→ 05 core registration/waits → 06 core routing       │
                                      03 + 06 + 08 → 13 transacting engine ──┤
                                                   09 + 13 → 14 client role ─┤
                                           11 + 13 + 14 → 15 server/E2E ─────┤
                                                       04 + 12 + 15 → 16 rip-and-tear cleanup
```

Chunks on separate branches may run in parallel once their listed dependencies are complete. A chunk must not rely on an unlisted future chunk.

## Conventions inherited by every chunk

1. TDD: add the specified failing tests first, confirm the focused failure, implement only the chunk, then run focused tests and `make fullCheck`.
2. Gate: `make fullCheck` is the first-class completion gate. Do not substitute archived `uv-fullCheck` notes.
3. Dependencies: keep `[project].dependencies` empty; production code uses the standard library and existing project types only.
4. Thread tests: synchronize with `threading.Event`, `Barrier`, or queues; no correctness assertion may depend on sleeps, random delays, or unbounded joins.
5. Errors: constructor/codec/connect/listen misuse raises as specified; established send failures are contained as boolean/status outcomes; callback failures are logged and contained.
6. Scope: do not add TLS, UDP, automatic reconnect, multiple active server clients, a callback executor, compatibility shims, or changes to `foundation_abc.PeripheralByteTransport`.
7. Authority: if a chunk cannot satisfy its linked accepted spec, stop and return the conflict for a contract decision; do not silently rewrite the spec.
8. Tracking: keep chunk frontmatter current; status remains `pending` until execution acceptance and ask-to-result comparison are recorded.
9. Naming: new Python modules and tests use snake_case; public type names follow the accepted specs.
10. Ownership: preserve unrelated user changes in the dirty worktree and do not commit unless explicitly asked.

## Chunk index

| # | delegated chunk | track | depends on |
| --- | --- | --- | --- |
| 01 | [Deterministic threaded socket test support](01-threaded-test-support.md) | shared | — |
| 02 | [Transaction values and outcomes](02-transaction-values.md) | protocol | — |
| 03 | [Transaction codec protocol and JSON codec](03-json-transaction-codec.md) | protocol | 02 |
| 04 | [Angle-bracket transaction codec](04-angle-transaction-codec.md) | protocol | 03 |
| 05 | [Transaction core registration and waits](05-transaction-core-state.md) | protocol | 02 |
| 06 | [Transaction core routing and finalization](06-transaction-core-routing.md) | protocol | 05 |
| 07 | [Socket handler epochs, teardown, and sends](07-socket-handler-lifecycle.md) | transport | 01 |
| 08 | [Raw and delimiter-text receive dispatch](08-socket-receive-dispatch.md) | transport | 07 |
| 09 | [Threaded socket client](09-socket-handler-client.md) | transport | 08 |
| 10 | [Server listener lifecycle](10-socket-server-listener.md) | transport | 08 |
| 11 | [Server admission and client replacement](11-socket-server-admission.md) | transport | 10 |
| 12 | [Binary-framed socket client](12-binary-framed-client.md) | framing | 08, 09 |
| 13 | [Shared transacting engine](13-transacting-engine.md) | transaction | 03, 06, 08 |
| 14 | [Transacting client role](14-transacting-client.md) | transaction | 09, 13 |
| 15 | [Transacting server role and bidirectional E2E](15-transacting-server-e2e.md) | transaction | 11, 13, 14 |
| 16 | [Rip-and-tear cleanup](16-rip-and-tear-cleanup.md) | cleanup | 04, 12, 15 |

## Execution handoff

Delegate one chunk at a time to an execution agent, or delegate independent branches in parallel. Each agent begins by reading this overview, the original ask, its chunk, all listed dependency chunks, and the linked accepted spec sections. This scope-plan does not authorize implementation by the planning agent.
