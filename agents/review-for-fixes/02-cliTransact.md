# Review: cliTransact.py

## ERROR — Async timeout uses the wrong duration for SIGTERM wait (line 305)
```python
await asyncio.wait_for(process.wait(), timeout=1.0)
```
The code says "escalate to SIGKILL only if the process ignores the graceful signal" and gives it a hard-coded 1 second, but:
- **`1.0` is always used**, regardless of what `timeout` was. A command with `timeout=5` gets a generous 1s grace period; one with `timeout=2` also gets a full 2× its allotted time before escalation. The timeout parameter should apply to *both* the initial wait and the escalate window — consider `min(timeout, some_fraction)` instead of hardcoding to `1.0`.
- This is especially problematic when the user sets a short timeout (e.g., `timeout=3`) but then waits another 1s after SIGTERM before sending SIGKILL — that's up to 4s total for a 3s call.

## ERROR — `_run_async` does not handle list vs string differently (line 289)
```python
process = await asyncio.create_subprocess_exec(
    *cli_command if isinstance(cli_command, list) else ["bash", "-c", cli_command],
    ...
)
```
If `cli_command` is a **single-item list** like `["echo"]`, the expression evaluates as:
```python
*cli_command  # → no arguments passed!
```
This silently creates a subprocess with zero args, causing `create_subprocess_exec()` to raise `ArgumentListTooLongError` or similar at runtime. This is actually correct (`*["echo"]` expands to just `"echo"`) — but if someone passes an empty list like `[]`, the validation catches it in `_validate_command`. So **not a real bug**.

## WARNING — async path normalizes stderr differently from sync (lines 316-317, 225)
In the **sync** path:
```python
stderr=self._normalize_output(process_result.stderr),
```
In the **async** path:
```python
stderr_text = stderr.decode() if stderr else ""
...
stdout=self._normalize_output(stdout_text),
# NOTE: *no* `self._normalize_output()` here — it's missing!
```
The async `_run_async` returns normalized stdout but normalizes stderr only for the timeout case (line 313). On non-timeout error paths, `stderr_text` is **never normalized** in the final result at line 325-328... let me re-check.

Actually: the final return at lines 325-329 uses `self._normalize_output(stderr_text)`. So it **is** normalized. That's fine.

## WARNING — `CLITransactResult.success` default is `False`, not computed (line 71)
```python
success: bool = False
```
Because dataclass fields can't have defaults before fields with defaults, and there's no `@property` or `__post_init__`, the `success` value is set by each caller in the return statement. This is fragile — any new code returning `CLITransactResult` directly could forget to set `success=True`. Consider computing it via validation or a factory helper.
