---
plan: ActionPlan03PresentationResolvers
scope: project
status: complete
last_updated: 2026-08-28
semver: 1.0.0
author: Nicholas Bergantz
---

# 03 — presentation resolvers (completed baseline)

Commit `1a768d3` added the MVP color, layout, region, and unit-resolution helpers. Later
work expanded title/subtitle behavior. The implementation exists, so this is not an
active implementation plan.

Any resolver change now requires one concrete failing case against the current public
API. Keep helpers stdlib-only and do not add file loading, rendering, migration, or
registry behavior.
