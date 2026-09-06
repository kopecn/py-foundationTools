---
plan: Fix14CLICommandModeContract
scope: project
status: needs-approval
last_updated: 2026-09-05
semver: 1.1.0
author: Nicholas Bergantz
---

# Fix candidate 14 — explicit CLI command execution mode

Evidence: synchronous string commands use `subprocess.run(..., shell=True)`, which selects
the platform default shell, while asynchronous string commands always use `bash -c`.
Consequently the same public command input has different syntax, portability, and security
semantics depending only on sync versus async execution.

Minimum fix: fix the actual sync/async inconsistency without changing the primary API
to argv. The contract below is the authorized decision.

## Authorized contract — 2026-09-05 (user)

- **`str` command = shell command.** A single command string stays the primary API
  layer. Callers construct/concatenate the command string themselves; shell and
  tokenization concerns are not pushed upstream onto callers.
- **`list[str]` command = direct argv execution**, no shell interpretation. Remains
  available for callers who want it.
- **String commands run through an explicit, consistent shell on both paths.** Default
  to `bash -c` for sync *and* async (Bash is an intentional supported dependency of
  this project). The sync path must stop using `subprocess.run(shell=True)` with the
  platform default shell.
- **Explicit shell override** is allowed for callers who need another interpreter
  (e.g. `zsh -c`). The override is an explicit parameter/configuration value.
- **Prohibited:** selecting the shell from the ambient environment or platform default;
  any automatic fallback between modes.
- **Hard requirement:** the same public string command has identical execution
  semantics (syntax, portability, security) regardless of sync vs. async. Tests must
  prove sync/async parity and cover platform behavior.

This is a public API change and may be breaking. Do not combine it with the
process-lifetime work in `fix-13`.
