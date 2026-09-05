---
plan: Fix11PresentationMigrationVersionIntegrity
scope: project
status: needs-approval
last_updated: 2026-09-04
semver: 1.0.0
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
