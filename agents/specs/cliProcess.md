---
spec: CLIProcess
scope: project
status: active
applies_to: src/foundation_tools/cli_transaction/cli_process.py
last_updated: 2026-11-05
semver: 0.1.0
author: Nicholas Bergantz
frontmatter_schema_semver: 1.1.1
structured_language: creative
document_type: specification
---

# Synchronous CLI Process

## Scope

`CLIProcess` owns one long-lived child process. The caller manages concurrency. Async execution, automatic retries, process-group management, and captured pipes are outside this contract.

## Requirements

### Construction and composition

`CLIProcess.start(command, *, cwd=None, env=None, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL, shell=None)` must return `CLIProcessStartResult`. A successful start contains a `process` handle and no `error`. A failed start contains a framework-error `CLITransactResult` in `error` and no process. The result's `success` property indicates successful launch, not child completion. Exactly one of `process` and `error` must be present.

An empty command or a launch exception must produce a failed start result. `BaseException` must propagate.

`CLIProcess` must compose a `subprocess.Popen` handle. It must not inherit from `CLITransact`. Both classes must compose the same internal `ProcessExecution` helper for command preparation, environment overlays, and logging. `CLITransact` retains its existing sync and async execution mechanisms.

Command interpretation, `cwd`, `env`, and logging with secret masking must obey [cliTransact.md](cliTransact.md#command-input-contract), [child context](cliTransact.md#child-process-context-and-standard-input), and [execution logging](cliTransact.md#execution-logging). The shared helper must keep a copy of supplied environment values so that later caller changes cannot alter redaction.

### Standard streams

Each standard stream must default to `subprocess.DEVNULL`. Callers may supply file objects, file descriptors, or `None` to inherit a stream explicitly. `stderr` may use `subprocess.STDOUT`. `subprocess.PIPE` must be rejected before launch because this class does not drain pipes. Callers retain ownership of supplied files; the class must not close them.

Output redirected to files or discarded is not captured, read back, or included in results. Completed results have `stdout=None` and `stderr=None`. Framework errors carry their diagnostic in `stderr`. These diagnostics must use the shared DEBUG logging and secret-masking rules. No text-input parameter or model parsing is provided.

### Lifecycle

`pid` must expose the child PID as a read-only property. `poll()` must return the native exit code or `None` while the child runs. It uses the underlying `Popen.poll()` status operation.

`wait(timeout=None)` must return a completed `CLITransactResult` when the child exits. A wait timeout must return `None` without terminating the child. A finite timeout must be non-negative. Invalid timeouts and execution failures must return framework-error results.

`stop(graceful_timeout=5.0)` must terminate a running child, wait for the specified grace period, and kill and reap the child if that period expires. The grace period must be finite and non-negative. An already-exited child must not be signaled. A child that exits between a status check and a signal must not cause a false failure. Stop failures must return framework-error results and must leave the handle available for another cleanup attempt.

Completed results must preserve native exit codes, including negative signal codes on POSIX. Success means exit code zero. A completed shutdown does not convert a signal exit into success. The existing result type uses `-1` for framework errors; a native POSIX SIGHUP exit also has that value. This type does not separately tag those outcomes.

Repeated `wait()` or `stop()` calls after observed completion must return the same stored terminal result. The class must not cache an operation error as child completion.

The context manager must return the process owner on entry and call `stop()` on exit. It must not suppress an exception from the context body. A failed stop must be logged at ERROR with secret masking.

### Ownership boundary

The class owns only the immediate child and its reaping. It must not signal descendants or process groups. A shell or launcher that remains the parent of another process does not transfer that descendant to this owner. Callers must use a launcher that replaces itself with the required process when direct ownership is necessary.
