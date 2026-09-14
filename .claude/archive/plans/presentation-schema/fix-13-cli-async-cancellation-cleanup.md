---
plan: Fix13CLIAsyncCancellationCleanup
scope: project
status: completed
last_updated: 2026-09-05
semver: 1.0.1
author: Nicholas Bergantz
---

# Fix candidate 13 — asynchronous CLI cancellation cleanup

Evidence: `CLITransact._run_async` terminates children on timeout and catches ordinary
exceptions, but `asyncio.CancelledError` is a `BaseException`. Cancellation while awaiting
`process.communicate()` can propagate without terminating and reaping the child process.

Minimum fix: make child ownership cancellation-safe with explicit terminate/kill/wait
cleanup and then re-raise cancellation. Add a real subprocess regression test that proves
the child exits and no zombie or background process survives the cancelled transaction.

Do not swallow cancellation, convert it into a normal result, alter timeout semantics, or
combine this process-lifetime fix with the shell API decision in `fix-14`.

## Ask ↔ result

**Objective (from "Minimum fix" + user addition):** Make `CLITransact._run_async` child
ownership cancellation-safe — on `asyncio.CancelledError` while the child is alive, run
explicit `terminate()` → short grace `wait()` → `kill()` → `wait()` cleanup and then
re-raise the `CancelledError` unchanged. Add a real-subprocess regression test proving the
child exits with no surviving orphan/zombie. User addition: emit one log line through the
module's existing logging mechanism in that cancellation-cleanup path, just before the
re-raise, naming the child pid.

**Authorizing request:** `/execute-plan fix-09 and onward` with the user's explicit
approval of fix-13 for execution on 2026-09-05, plus the note "13 -- approved, add in the
standardized logger into the re-raise." No `human_ask`/`goal` frontmatter; scope limited to
the async cancellation path.

**Spec check (no contradiction found):** `cliTransact.md` "Total exception containment"
applies to *execution* failures (timeouts, non-zero exit, parser/exec exceptions) being
captured into a result; it explicitly states `BaseException` "is intentionally allowed to
propagate." `asyncio.CancelledError` is a `BaseException` (cooperative task cancellation,
not an execution failure), so re-raising it is consistent with the contract. The existing
timeout `terminate → kill` escalation is untouched; the new handler mirrors that cascade on
a separate code path.

**Delivered:**

- `src/foundation_tools/cli_transaction/cliTransact.py`
  - Added module logger: `from logging import getLogger` + `_log = getLogger(__name__)`
    (matches the existing convention in sibling `foundation_tools/socket_transaction/`
    modules and `foundationTypes/data_model_helper.py`; no new logging mechanism, no
    `setLoggerClass`, zero new dependencies).
  - Added `except asyncio.CancelledError` handler in `_run_async`, ordered before the
    existing `except Exception`. When `process` is alive (`returncode is None`): capture
    `process.pid`, `terminate()`, `await asyncio.wait_for(process.wait(), grace)` with the
    same `min(GRACE_PERIOD_CAP_SECONDS, timeout)` grace window as the timeout path, escalate
    to `kill()` + `await process.wait()` on grace expiry. Reaping is wrapped best-effort
    (`except Exception: pass`). Then `_log.warning("CLITransact async child pid=%s
    terminated and reaped after task cancellation", child_pid)` and bare `raise` to
    re-propagate the `CancelledError`.
  - Timeout semantics, sync path, `*_with_model` wrappers, and the generic-exception
    containment block are unchanged.

- `tests/testfoundationCLITransact.py`
  - New test `TestCLITransactAsync::test_run_async_cancellation_reaps_child_and_reraises`
    (Unix-only via `skipif` on win32). Launches a genuine child
    (`[sys.executable, "-c", "import time; time.sleep(30)"]`), captures the real `Process`
    object by wrapping `asyncio.create_subprocess_exec`, lets the task park in
    `communicate()`, `task.cancel()`s it, and asserts: (a) `pytest.raises(
    asyncio.CancelledError)` on `await task` — not swallowed, not a `CLITransactResult`;
    (b) `process.returncode is not None` (child was `wait()`ed); (c)
    `os.kill(pid, 0)` raises `ProcessLookupError` (pid gone from the OS table — no zombie,
    no orphan).

**How the child was proven reaped:** the captured real `asyncio.subprocess.Process` has
`returncode` set to a signal value (non-`None`) after cancellation, and `os.kill(pid, 0)`
raises `ProcessLookupError` — a zombie would still answer `os.kill(pid, 0)`, so the pid
being absent proves the process was both signalled and `wait()`-reaped. Before the fix the
same test failed with `returncode is None` and left a stray `time.sleep(30)` process
running.

**Logger / level:** stdlib `logging` via `getLogger(__name__)` (logger name
`foundation_tools.cli_transaction.cliTransact`), level `WARNING`, message
`"CLITransact async child pid=%s terminated and reaped after task cancellation"`.

**Failing → passing test:**
`tests/testfoundationCLITransact.py::TestCLITransactAsync::test_run_async_cancellation_reaps_child_and_reraises`
— failed pre-implementation (`AssertionError: child was not reaped (returncode is None)`),
passes post-implementation.

**Gate:** `make uv-fullCheck` → `565 passed` (564 baseline + 1 new); `make uv-lint` →
`All checks passed!`; `make uv-typecheck` → `Success: no issues found` (62 src + 36 test
files).

**Deviations / gaps:** The chunk text says "emit a log line through the module's existing
logger" — the module had *no* logger, so one was added using the codebase's established
`getLogger(__name__)` pattern (the user's note said "add in the standardized logger"; a
direct `StandardizedLogger` instance self-configures stderr/file handlers and is
inappropriate for a library module, and `StandardizedLogger.setLoggerClass()` is explicitly
disallowed by the briefing — `getLogger(__name__)` returns a `StandardizedLogger` instance
automatically wherever the application has installed it as the logger class, so this honours
the intent without the intrusion). No other deviation. `status` left unchanged
(`needs-approval`); only `last_updated` bumped.
