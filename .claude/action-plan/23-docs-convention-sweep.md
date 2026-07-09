---
plan: ActionPlan23DocsConventionSweep
scope: project
status: pending
last_updated: 2026-07-08
semver: 0.0.1
author: Nicholas Bergantz
---

# 23 — Docs & Convention Sweep (corrective)

## Origin

Post-audit of chunk 21 (2026-07-08), minor doc/convention drift findings F3 +
F4. Run after (or independently of) chunk 22 — no code dependency.

## Findings → fixes

- [ ] **F4 — stale docstring in `src/foundation_abc/math/mathEnums.py`
  (lines 3–5).** The module docstring says the enums exist so "the
  hand-written tier modules (`precisionTimeInterval.py` /
  `precisionTimestamp.py`)" can import them — those modules do not exist
  anywhere in the repo (pre-existing staleness carried through the verbatim
  move). Rewrite the sentence to name the actual importers: the generated
  `MathTypes.py` and the Tier-2 ABC module `precisionTimeABC.py`. This file
  is hand-written (not codegen output), so a direct edit is safe.
- [ ] **F3 — chunk 21 frontmatter semver not bumped.** The plan file
  `.claude/action-plan/21-math-abcs-to-foundation-abc.md` gained
  `status: complete` + Resolution Notes but still carries `semver: 0.0.1`;
  convention (see chunk 20 at 0.2.0, and the frontmatter-tracking rule) is to
  bump on edit. Set `semver: 0.1.0`.

## Recorded, no action (do not relitigate)

- ABC docstrings referencing not-yet-written
  `foundationTypes.mathTypes.*MathLike` modules (`spatialABCs.py`,
  `sphericalABCs.py`, `precisionTimeABC.py`) — explicitly out-of-scope in
  chunk 21's Resolution Notes; the modules' eventual home is undecided.
- `schemaCodegen.md` naming `generateUnitSphericalSmallCircle.sh` as the
  golden template — pre-existing staleness recorded in chunk 21's
  Out-of-Scope section, independent of the Plan-21 change.

## Acceptance

- [ ] `mathEnums.py` docstring names only modules that exist.
- [ ] Chunk 21 frontmatter at `semver: 0.1.0`.
- [ ] `make uv-fullCheck` passes (docstring-only code change).
