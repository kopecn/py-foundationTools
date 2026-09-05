---
plan: Fix13CLIAsyncCancellationCleanup
scope: project
status: needs-approval
last_updated: 2026-09-04
semver: 1.0.0
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
