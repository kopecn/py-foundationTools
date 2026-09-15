---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Repair Plan 25 documentation, historical navigation, examples, and current-state source descriptions before final re-audit.
last_updated: 2026-09-13
semver: 0.1.0
author: Nicholas Bergantz
status: completed
---

# 25 - Repair documentation and archive navigation

Scope: [summary goal](00-corrective-overview.md#summary-goal) · [original ask](00-original-ask.md) · Origin contract: [rip-and-tear cleanup](16-rip-and-tear-cleanup.md)

## Origin

PA25-09: the audit found dead active/archive links, active statuses on completed historical records, incorrect serialization statements, examples that claim concurrency they cannot demonstrate, and stale chunk-era source docstrings.

## Deliverable

Make the Plan 25 documentation and navigation truthful for the current implementation and the corrective lifecycle, while leaving final archive closure to the next clean post-audit.

## Depends on

24.

## Files

- Edit `.claude/plans/25-threaded-socket-transaction.md`.
- Edit `.claude/archive/plans/25-threaded-socket-transaction/00-overview.md`.
- Edit `.claude/archive/plans/25-threaded-socket-transaction/00-original-ask.md`.
- Edit `.claude/archive/plans/25-threaded-socket-transaction/01-threaded-test-support.md` through `16-rip-and-tear-cleanup.md` only for links/tracking and confirmed stale execution notes.
- Edit `.claude/specs/transport_transaction_architecture.md`.
- Edit `.claude/specs/socketTransact.md`.
- Edit `.claude/CLAUDE.md` only for the Plan 25 archive path/current socket description.
- Edit `src/foundation_tools/socket_transaction/socket_handler.py`.
- Edit `src/foundation_tools/socket_transaction/transaction_models.py`.
- Edit `src/foundation_tools/socket_transaction/transacting_socket_handler.py`.
- Edit `tests/test_transaction_codecs.py` and `tests/test_transaction_core.py` only for stale module/helper prose.
- Edit `examples/exampleSocketClientServer.py` and `examples/readme.md`.
- Edit this corrective `00-overview.md` and completed corrective chunk tracking only as required by execution acceptance.

## Design constraints

- Keep the historical chunks in `.claude/archive/plans/25-threaded-socket-transaction/`; do not restore the concurrent archive move.
- Fix archived spec links from `../../specs/...` to `../../../specs/...` and make the top-level plan link separately to historical chunks and active corrective chunks.
- Correct the canonical cleanup filename to `16-rip-and-tear-cleanup.md`; remove stale future-agent and incorrect source-line-count wording.
- Mark the archived original overview and original-ask record completed with maintained tracking fields; keep the active top-level plan and corrective overview in progress until a clean post-audit performs final closure.
- Describe actual socket model serialization: JSON uses `DataModelHelper.to_dict()`, angle-bracket uses `to_bytes()`, and decode returns a `TransactionFrame` without automatic model reconstruction.
- Label the deleted asyncio spec body explicitly historical; do not rewrite or reactivate it.
- Remove chunk-era source/test narration and false "not exported" statements; retain durable behavior descriptions.
- Make `exampleSocketClientServer.py` describe its synchronous callback execution honestly; do not claim randomized callback delays prove out-of-order replies.
- Correct only stale commands in `examples/readme.md` that chunk 16 was assigned to edit; do not sweep unrelated repository documentation.
- Preserve every unsupported/open contract item from the corrective overview as recorded/no-action.

## Link check recipe

```text
for each edited relative Markdown link:
    resolve from the containing file's directory
    assert the target exists
```

Use a mechanical link check or direct path resolution; do not infer link validity from visible text.

## TDD and verification steps

1. Resolve every listed stale statement and link against current files before editing.
2. Apply the minimum documentation-only corrections and tracking bumps.
3. Run a relative-link check for Plan 25 records and compile both socket examples.
4. Run the chunk-16 forbidden-name/asyncio greps and `make fullCheck`.

## Acceptance criteria

- [x] Every Plan 25 relative link resolves from its containing file.
- [x] Historical records are completed; active corrective records remain in progress pending re-audit.
- [x] Current docs describe actual codec serialization and the archived asyncio spec as historical.
- [x] Source/test docstrings contain no false export or future-chunk claims.
- [x] Socket examples compile and make no false out-of-order callback claim.
- [x] `examples/readme.md` names existing Makefile targets.
- [x] `make fullCheck` passes.

## Out of scope

- Moving the active top-level plan or corrective set into the archive before re-audit.
- Root `README.md`, `docs/README.md`, or unrelated documentation drift.
- Changing runtime behavior, accepted public API, or unsupported contract decisions.

## Ask ↔ result

- **Objective (human_ask + goal):** the top-level `human_ask` is the original Plan 25 request to rip out asyncio in favor of threading/sockets; this chunk's own `goal` is narrower and downstream of that — repair Plan 25 documentation, historical navigation, examples, and current-state source descriptions before a final re-audit, per PA25-09's findings (dead links, historical statuses left `active`, incorrect serialization statements, examples claiming concurrency they cannot demonstrate, stale chunk-era source docstrings).
- **Live authorization:** `/execute-plan 17 ... 25 these were from a post audit` — explicit user instruction to execute this chunk now; the recorded `human_ask` and this chunk's `goal` do not conflict on the objective itself (decompose-and-build vs. repair-the-resulting-docs are compatible, sequential objectives), so execution proceeded without stopping for clarification per the live command's own guidance.
- **Delivered:**
  - Fixed 20 broken `../../specs/...` → `../../../specs/...` links across all 17 files in `.claude/archive/plans/25-threaded-socket-transaction/` (00-overview.md plus chunks 01-16), and the dead `../25-threaded-socket-transaction.md` link in the archived `00-overview.md` (now `../../../plans/25-threaded-socket-transaction.md`), removing its stale "856-line" claim and "future agents" framing (the chunk set is executed, not future work).
  - Marked the archived `00-overview.md` and `00-original-ask.md` `status: completed` with bumped `last_updated`/`semver`.
  - Rewrote the top-level `.claude/plans/25-threaded-socket-transaction.md`'s "Delegated execution plans" paragraph to link separately to the historical decomposition overview (chunks 01-16, archived, completed) and the active corrective overview (chunks 17-25, in progress), and corrected the chunk-16 reference from the stale draft filename `16-public-cutover.md` to the canonical `16-rip-and-tear-cleanup.md` at its actual archive path.
  - Labeled `.claude/specs/socketTransact.md`'s per-layer `Status: Implemented` lines and its top status banner as historical (implemented, then deleted by the Action Plan 25 cutover) without rewriting the surrounding asyncio-era body.
  - Corrected `.claude/specs/transport_transaction_architecture.md`'s stream-family serialization claim: it previously asserted `DataModelHelper.to_wire`/`from_wire` (the wire-bridge ClassVars); the actual `transaction_codecs.py` implementation uses `to_dict()` for the JSON codec and `to_bytes()` for the angle-bracket codec, and `decode()` returns a `TransactionFrame` with no automatic model reconstruction — confirmed by reading `src/foundation_tools/socket_transaction/transaction_codecs.py` directly.
  - Fixed `.claude/CLAUDE.md`'s single Plan-25-relevant sentence: it previously implied the threaded socket family's build history lives in `.claude/archive/action-plan/` (which does not contain it); now states the socket family's build (Action Plan 25) is archived separately at `.claude/archive/plans/25-threaded-socket-transaction/`. No other line was touched.
  - Removed chunk-era narration and false "not exported"/"no package export yet" statements from `socket_handler.py` (module docstring, `ConnectionObserver`, `SocketHandler` class docstring, a section comment, and `_process_received_chunk`'s docstring), `transaction_models.py` (module docstring falsely claimed the module's types are not exported — all five are), and `transacting_socket_handler.py` (module docstring's ambiguous not-exported claim clarified, plus `InboundTransaction`'s docstring falsely claimed "Not a package export" — it is exported).
  - Fixed `tests/test_transaction_codecs.py`'s module docstring, which falsely claimed angle-bracket codec behavior was "out of scope for this chunk" while the file extensively tests `AngleBracketTransactionCodec`; and `tests/test_transaction_core.py`'s chunk-numbered docstring/comments, including one white-box helper's now-false claim that it was "standing in for chunk 06's `route()`, not yet implemented" (`route()` is implemented and in active use).
  - Corrected `examples/exampleSocketClientServer.py`'s claim that randomized handler delays demonstrate out-of-order reply resolution; the server's inbound handler runs synchronously on the connection's single receive thread, so replies are actually produced in receipt order — the demo's real point (correlation by transaction id, not send order) is now stated honestly, and the function/print text renamed accordingly.
  - Corrected the one stale Makefile target in `examples/readme.md` (`make devInstall` → `make installDev`; `installDev` is the actual target, `devInstall` does not exist).
- **Verification (this agent, firsthand):** a mechanical link-resolution check over every edited Plan 25 markdown file (all links resolve); `python -m py_compile` on both socket examples (`exampleSocketClientServer.py`, `exampleBenchmarkPerformance.py`); the chunk-16 greps for asyncio (`rg -n "asyncio|async def|async with|await " src/foundation_tools/socket_transaction`) and forbidden legacy names both empty; `make fullCheck` → lint clean, mypy clean (both source and tests), 934 tests passed.
- **Gap:** none against the chunk as written. Final archival of the top-level plan and corrective set is deliberately left open, per this chunk's own scope, for the next clean post-audit.
