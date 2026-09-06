---
plan: Fix11PresentationMigrationVersionIntegrity
scope: project
status: needs-approval
last_updated: 2026-09-05
semver: 1.1.0
author: Nicholas Bergantz
---

# Fix candidate 11 — truthful presentation migration versions

Evidence: `migrate_deck` stamps target theme/layout metadata before unresolved layout,
region, or color references are known. A result with `ok == False` can therefore contain
a deck claiming the destination standard while still carrying source-standard references.
Empty maps also currently mean "migrate this dimension but every reference is missing";
there is no explicit way to say a dimension is outside the migration scope.

Minimum fix: define migration scope explicitly and stamp each target version only after
that dimension succeeds. Tests must cover partial failures independently for theme colors,
layouts, and regions and prove the returned metadata never overstates conformance.

Do not silently drop unresolved content, infer mappings, or introduce registry/discovery
I/O. Decide the partial-result representation before implementation rather than treating
the current accidental behavior as a compatibility requirement.

## Session note — 2026-09-05 (not executed; design dialog pending)

Status held at `needs-approval`. No implementation this session. A subsequent session
opens a design dialog; capture how it gets dialed in here.

Direction to explore (user, 2026-09-05): a mechanism to assign a semantic **type id
/ role tag** to a generated field in the pptx model, so that tagging a field drives
its characteristics from the active theme/layout rather than from per-deck literals.
Example: a field tagged `title` automatically receives the title font, the title
color, and the title position. This is the field-level expression of the "CSS for
pptx" goal, and it is also the resolution target that migration references would map
onto — a migrated deck adopts the destination standard by re-resolving role tags
against the new theme/layout, instead of the migration stamping a version it has not
actually satisfied.

Open questions for the dialog:

- where the role vocabulary lives (schema enum vs. layout/region definition);
- how a role resolves to concrete font/color/position, and precedence when a field
  also carries explicit overrides;
- how this interacts with the per-dimension version stamping this fix requires
  (theme colors, layouts, regions stamped only after that dimension resolves);
- whether unresolved role tags are the explicit "outside migration scope" signal
  that the current empty-map ambiguity lacks.

Revisit before scoping an execution plan.
