---
plan: Fix07ReadmeDriftRepair
scope: project
status: complete
last_updated: 2026-09-04
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

## Ask ↔ result

- **Objective:** correct only the factually-broken quick-start imports, methods, and Make commands in README/CONTRIBUTING.
- **Authorized by:** `/execute-plan please proceed` (user approved all of fix-01–07).
- **Delivered (all verified against reality):** camelCase `saveToFile`/`loadFromFile` → snake_case `save_to_file`/`load_from_file`; math-type imports → real `foundationTypes.mathTypes.MathTypes` with the actual `…Type`-suffixed class names, plus a false "abstract base" comment on `QuaternionType` corrected to direct construction; absent/renamed Make targets fixed (`installDev`, `uv-lint`/`uv-format`, `release-test`, `clean-build`/`clean-test`, `bump-patch/minor/major`) and non-existent ones removed (`dist`, `tag`, `docs`); `CONTRIBUTING.md` test path → an existing file. Supervisor re-ran the README quick-start verbatim end-to-end: passes.
- **Verification:** doc-only change; the gate does not cover markdown, so verification was executing the corrected snippets, `make help`, and the Makefile directly. `make uv-fullCheck` still green (532).
- **Gap:** none in scope. Out-of-scope items flagged not fixed: a broken Code-of-Conduct hyperlink (prose link, not import/method/target).
