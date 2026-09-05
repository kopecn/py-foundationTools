---
plan: Fix14CLICommandModeContract
scope: project
status: needs-approval
last_updated: 2026-09-04
semver: 1.0.0
author: Nicholas Bergantz
---

# Fix candidate 14 — explicit CLI command execution mode

Evidence: synchronous string commands use `subprocess.run(..., shell=True)`, which selects
the platform default shell, while asynchronous string commands always use `bash -c`.
Consequently the same public command input has different syntax, portability, and security
semantics depending only on sync versus async execution.

Minimum fix: choose one explicit command contract shared by both paths. Prefer argv input
for direct execution and a separate, deliberately named shell-command value/configuration
when shell interpretation is required. Test sync/async parity and platform behavior.

This is a public API decision and may be breaking. Do not preserve ambiguous string behavior
through an automatic fallback or select a shell from the ambient environment without an
explicit contract.
