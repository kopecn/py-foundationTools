---
plan: ActionPlanOverview
scope: project
status: active
last_updated: 2026-07-03
semver: 0.1.1
author: Nicholas Bergantz
---

# Action Plan — Transaction/Transport Stack

## Goal

Build the full transaction/transport stack under `src/foundation_tools/` per the
umbrella spec
[transport_transaction_architecture.md](../specs/transport_transaction_architecture.md):
the CLI process-transaction family (kernel hardening, policies, builders,
`SSHTransact`, `RsyncTransact`) and the asyncio socket stream family
([socketTransact.md](../specs/socketTransact.md)) — greenfield, nothing external
depends on the current code.

## Usability north star

End users touch only the Layer-4 transactions (`CLITransact`, `SSHTransact`,
`RsyncTransact`, `SocketTransact`) — one-call stateless surfaces returning result
objects, never raising. Builders/policies/codecs are internal-but-importable. Every
chunk's API review checks against this.

## Chunk dependency graph

```
01 package restructure
├── Track CLI:    02 kernel hardening → 03 policies → 04 builders → 06 SSHTransact → 07 RsyncTransact
├── Track Socket: 05 byte transport → 08 framing codecs → 09 tx router → 10 SocketTransact → 13 server
├── 11 wire-parser bridge   (after 02)
└── 12 docs & drift sync    (after all)
```

The two tracks are independent after chunk 01 and may proceed in parallel
(full-parity priority). Within a track, chunks are strictly ordered.

## Conventions (every chunk)

1. **TDD** — define behavior → write failing test → implement → pass → refactor.
   Tests validate the spec contract, not implementation details.
2. **Gate** — `make fullCheck` (ruff lint + format + mypy + ty + pytest) must pass
   before a chunk is considered done.
3. **Zero runtime deps** — stdlib only; `[project].dependencies` stays empty.
4. **Result objects, not exceptions**, on transaction surfaces (kernel/facade
   containment rules per spec); raw transports keep ABC raising semantics.
5. **Spec is authoritative** — if implementation forces a contract change, update
   the spec in the same chunk and bump its semver.
6. **Stay in scope** — each chunk lists explicit out-of-scope items; do not fold
   adjacent work in.
7. **Frontmatter** — any created/edited managed markdown carries
   `last_updated` / `semver` / `author`.
8. **Test naming** — new test files use `tests/test_<module>.py` (snake_case).
   Existing `testfoundation*.py` files keep their names; renaming them is out of
   scope for this plan.

## Chunk index

| # | chunk | track | depends on |
| --- | --- | --- | --- |
| 01 | [Package restructure](01-package-restructure.md) | shared | — |
| 02 | [CLITransact hardening](02-clitransact-hardening.md) | CLI | 01 |
| 03 | [Execution policies](03-execution-policies.md) | CLI | 02 |
| 04 | [Command builders](04-command-builders.md) | CLI | 03 |
| 05 | [Socket byte transport](05-socket-byte-transport.md) | Socket | 01 |
| 06 | [SSHTransact](06-sshtransact.md) | CLI | 04 |
| 07 | [RsyncTransact](07-rsynctransact.md) | CLI | 04 |
| 08 | [Socket framing codecs](08-socket-framing-codecs.md) | Socket | 05 |
| 09 | [Socket transaction router](09-socket-transaction-router.md) | Socket | 08 |
| 10 | [SocketTransact facade](10-sockettransact.md) | Socket | 09 |
| 11 | [Wire-parser bridge](11-wire-parser-bridge.md) | shared | 02 |
| 12 | [Docs & drift sync](12-docs-and-drift-sync.md) | shared | all |
| 13 | [SocketTransactServer](13-sockettransact-server.md) | Socket | 08, 10 |
