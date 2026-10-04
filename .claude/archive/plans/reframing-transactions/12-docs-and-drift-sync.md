---
plan: ActionPlan12DocsAndDriftSync
scope: project
status: complete
last_updated: 2026-07-05
semver: 0.1.0
author: Nicholas Bergantz
---

# 12 — Docs & Drift Sync (final gate)

## Goal

Close the loop: make every document tell the truth about the shipped stack, and
pass the full CI gate one last time.

## Depends on

All other chunks (run last).

## Files

- `.claude/CLAUDE.md` — flip "planned" wording to "implemented" for shipped
  modules; verify import-path examples
- `.claude/specs/{cliTransact,sshTransact,rsyncTransact,socketTransact,transport_transaction_architecture}.md`
  — update `status:` frontmatter (`proposed`/`planned` → `implemented`), bump
  semver, correct any contract wording that shifted during implementation
- `README.md` — only the section touching the transaction stack, if any
- `.claude/action-plan/*.md` — mark chunk `status:` fields `done`

## Steps

1. Run a drift pass over the touched specs (the repo-to-spec-sync discipline):
   compare each spec's compliance list against the code and tests; fix the spec,
   never invent unimplemented claims.
2. Sweep for stale references:
   `grep -ri "foundationCLIHelpers" src/ tests/ README.md examples/` must return
   nothing. Exempt by design: cliTransact.md's intentional naming-history note and
   `.claude/action-plan/` / `.claude/plans/` files that record the rename. Every
   `applies_to:` path must exist.
3. Verify frontmatter on all touched markdown (`last_updated`, `semver`, `author`).
4. `make fullCheck` and `make testInEnv` (packaging path validates the new
   subpackages ship).

## Acceptance criteria

- [x] Zero `foundationCLIHelpers` references in `src/`, `tests/`, `README.md`,
      and `examples/` (spec/plan naming-history notes exempt).
- [x] Every spec `status:` and `applies_to:` matches reality.
- [x] `make uv-fullCheck` and `make testInEnv` pass (`make fullCheck` no longer
      exists).

## Out of scope

- New features of any kind.
- README overhaul beyond the transaction-stack section (the README's stale tooling
  claims are a separately-scoped known issue).

## Implementation notes

- Ran the drift pass manually (per this chunk's own instructions, not via the
  `repo-to-spec-sync` skill) across the 5 transaction-stack specs, comparing
  each against the real implementation in `src/foundation_tools/`:
  - **cliTransact.md**: flipped `status: partial` → `implemented`. The
    "Planned Layers (not yet implemented)" section (SSHTransact, RsyncTransact,
    retry/backoff, Windows/MSYS2) described modules that are now built with
    their own dedicated specs — replaced with a short **Sibling Layers**
    pointer section rather than duplicating content now owned elsewhere
    (Define Once, Only Once). Fixed the `System Role` diagram's stale
    `(planned)` tags.
  - **sshTransact.md**: flipped `status: proposed` → `implemented`. Found one
    real Source→Spec gap: `SSHTransact`'s four methods all accept an optional
    `retry_policy: RetryPolicy | None = None` (per the policy-ownership rule
    the "Zero execution policy" section already described qualitatively) but
    the concrete parameter was never named in the Public API section — added.
  - **rsyncTransact.md**: flipped `status: planned` → `implemented`, reworded
    the top banner (was "defines the required contract for the future
    implementation"), fixed the `Retry Policy (planned)` tag in the System
    Role diagram, renamed "Future Retry Integration" → "Retry Integration" and
    documented the real `RSYNC_TRANSIENT_RETURN_CODES` /
    `RSYNC_PERMANENT_RETURN_CODES` constants `rsyncTransact.py` actually
    exports (the spec previously only described the recommended code sets in
    prose, not the concrete exported names). Same `retry_policy` parameter gap
    as SSHTransact, fixed the same way.
  - **socketTransact.md**: the whole top banner claimed "Nothing in this spec
    is implemented yet" — false for all of chunks 05/08/09/10/13. Flipped the
    banner and all five per-layer `Status: Proposed` tags (transport, codecs,
    router, client facade, server) to `Implemented`. Also documented that
    `codec` defaults to `DelimiterCodec()` in the client facade's Construction
    section (previously only shown as an explicit example, not stated as the
    default — a minor Source→Spec gap).
  - **transport_transaction_architecture.md**: the Package Layout section
    marked every non-kernel file `# planned`/`# proposed`; flipped all to
    `# implemented`. Layers 2–4 and the Stream-Transport Family section were
    each tagged `Status: Proposed`; flipped to `Implemented`. Found two
    INTERFACE_DRIFT items while doing this: Layer 2's example list named
    `RsyncCommandBuilder`/`SSHCommandBuilder` (implying builder *classes*) but
    the real implementation is plain functions `build_rsync_command`/
    `build_ssh_command` — corrected the examples and marked the
    still-hypothetical `DockerCommandBuilder`/`GitCommandBuilder`/
    `GitTransact`/`DockerTransact`/`SuccessPolicy`/`TimeoutPolicy` entries as
    illustrative-only, not implemented (`SuccessPolicy`/`TimeoutPolicy`
    specifically: those responsibilities are already owned inline by
    `CLITransact`, so no separate policy class exists or is planned for them).
- Independently (before the spec sweep) fixed the stale `foundationCLIHelpers`
  references the grep in step 2 must return zero for: the import in
  `examples/exampleDataModel.py` (now `foundation_tools.cli_transaction.cliTransact`)
  plus two stale camelCase calls in the same file (`saveToFile`/`loadFromFile` →
  `save_to_file`/`load_from_file` — the example was actually broken, not just
  misnamed; ran it end-to-end after fixing to confirm), and the README.md
  feature-list header. Left the README's other stale `saveToFile`/`loadFromFile`
  calls (Data Model Management / Mathematical Data Types sections) untouched —
  out of scope per this chunk's explicit carve-out (README overhaul beyond the
  transaction-stack section).
- `make uv-fullCheck` (lint + mypy + 288 tests) and `make testInEnv` (clean-room
  venv, packaging path) both pass — the clean-room install confirms the wheel
  actually ships `builders/`, `policies/`, and `socket_transaction/` as
  importable subpackages, not just that they exist in the source tree.
- This is the last chunk in the action plan (`00-overview.md` lists it as
  "after all"); flipped that file's `status: active` → `complete` alongside
  this one now that all 13 chunks are done.
