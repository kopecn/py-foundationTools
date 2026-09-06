---
plan: Fix14CLICommandModeContract
scope: project
status: completed
last_updated: 2026-09-05
semver: 1.2.0
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

## Ask ↔ result

- **Objective (authorized contract):** `str` command = shell command run through an
  explicit, consistent shell — default `bash -c` on BOTH sync and async; the sync
  path must stop using `subprocess.run(shell=True)` / platform default shell.
  `list[str]` = direct argv, no shell, stays available. Explicit `shell` override
  allowed (explicit parameter, not ambient). Prohibited: ambient/platform shell
  selection; automatic fallback between modes. Hard requirement: identical
  sync/async execution semantics for the same `str` command, proven by tests.
- **Authorizing request:** `/execute-plan fix-09 and onward` + the user's explicit
  written contract in "## Authorized contract — 2026-09-05 (user)" + "add in 14 to
  execute on this pass" (2026-09-05).
- **Delivered:**
  - `cliTransact.py`: added `DEFAULT_SHELL = ("bash", "-c")`; a keyword-only
    `shell: Sequence[str] | None` parameter on all four public methods (+ overloads),
    carried on the short-lived instance beside `success_marker`; a shared
    `_build_argv` helper used by both `_run_sync` and `_run_async`. `str` → `[*shell,
    command]`; `list[str]` → unchanged direct argv. Sync path now calls
    `subprocess.run(argv, shell=False)` — `shell=True` removed. Async path now routes
    through the same helper instead of an inline `["bash", "-c", …]`.
  - `tests/testfoundationCLITransact.py`: new `TestCLITransactShellContract` (12
    tests) — see test names below.
  - `.claude/specs/cliTransact.md`: realigned to the authorized contract (edits
    listed in the execution report), `semver` 0.4.0 → 0.5.0.
- **Gap / deviation:** none against the authorized contract. One documentation-only
  drift left untouched (out of the chunk's file scope): `.claude/CLAUDE.md`
  "CLITransact pattern" still says "String commands run via `shell=True`".
- **Status:** left as `needs-approval` per instruction (not set to `completed`).
