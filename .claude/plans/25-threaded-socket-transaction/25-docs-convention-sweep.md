---
human_ask: >
  I want you to take top level spec: /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/.claude/plans/25-threaded-socket-transaction.md and reduce it to a plural set of bite sized tasks that will rip and tear /Users/nbergantz/**Workspaces**/pythonWorkspaces/py-foundationTools/src/foundation_tools/socket_transaction/...   I do not want to use asyncio for the socket handling and want it reduced to threading and sockets.
goal: >
  Repair Plan 25 documentation, historical navigation, examples, and current-state source descriptions before final re-audit.
last_updated: 2026-09-13
semver: 0.0.1
author: Nicholas Bergantz
status: pending
---

# 25 - Repair documentation and archive navigation

Scope: [summary goal](00-overview.md#summary-goal) · [original ask](../../archive/plans/25-threaded-socket-transaction/00-original-ask.md) · Origin contract: [rip-and-tear cleanup](../../archive/plans/25-threaded-socket-transaction/16-rip-and-tear-cleanup.md)

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

- [ ] Every Plan 25 relative link resolves from its containing file.
- [ ] Historical records are completed; active corrective records remain in progress pending re-audit.
- [ ] Current docs describe actual codec serialization and the archived asyncio spec as historical.
- [ ] Source/test docstrings contain no false export or future-chunk claims.
- [ ] Socket examples compile and make no false out-of-order callback claim.
- [ ] `examples/readme.md` names existing Makefile targets.
- [ ] `make fullCheck` passes.

## Out of scope

- Moving the active top-level plan or corrective set into the archive before re-audit.
- Root `README.md`, `docs/README.md`, or unrelated documentation drift.
- Changing runtime behavior, accepted public API, or unsupported contract decisions.
