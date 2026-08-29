---
plan: Fix07ReadmeDriftRepair
scope: project
status: needs-approval
last_updated: 2026-08-28
semver: 1.0.0
author: Nicholas Bergantz
---

# Fix candidate 07 — executable documentation drift

Evidence: README and contributing examples name removed imports, camelCase data-model
methods, and Make targets no longer present.

Minimum fix: correct only broken quick-start imports/methods/commands against the
current package and `make help`. Add a small smoke test for the curated quick-start
surface if it prevents a demonstrated regression.

Do not reorganize package exports, add compatibility aliases, create a documentation
site, or rewrite unrelated prose.
