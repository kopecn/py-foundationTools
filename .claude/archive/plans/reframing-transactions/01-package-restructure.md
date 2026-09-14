---
plan: ActionPlan01PackageRestructure
scope: project
status: complete
last_updated: 2026-07-04
semver: 0.1.0
author: Nicholas Bergantz
---

# 01 — Package Restructure

## Goal

Establish the canonical `foundation_tools` layout for the transaction/transport
stack. **No behavior change** — skeletons and exports only.

## Depends on

Nothing (first chunk).

## Files

Create (each with a module docstring stating its layer role per the umbrella spec;
empty of logic):

```
src/foundation_tools/builders/__init__.py
src/foundation_tools/policies/__init__.py
src/foundation_tools/socket_transaction/__init__.py
```

Keep as-is: `src/foundation_tools/cli_transaction/` (kernel already lives here).

Update: `src/foundation_tools/cli_transaction/__init__.py` — re-export the public
surface (`CLITransact`, `CLITransactResult`, `CLITransactResultModel`) so end users
import from the package, not the module file.

## Steps

1. Write a test asserting the public imports work:
   `from foundation_tools.cli_transaction import CLITransact, CLITransactResult, CLITransactResultModel`.
2. Create the three subpackage skeletons and the `__init__` exports.
3. `make fullCheck`.

## Acceptance criteria

- [x] All three subpackages importable; `cli_transaction` re-exports its surface.
- [x] No production logic added or changed (diff is `__init__`/docstrings only).
- [x] `make uv-fullCheck` passes (`make fullCheck` no longer exists — Makefile has
      migrated to the `uv-` targets; CLAUDE.md is stale on this point).

## Out of scope

- Any kernel behavior change (chunk 02).
- Moving/renaming `cliTransact.py` itself.
- pyproject/packaging changes beyond what auto-discovery already handles.
