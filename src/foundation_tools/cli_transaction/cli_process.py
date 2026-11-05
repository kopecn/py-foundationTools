"""Synchronous ownership of one long-lived child process."""

from __future__ import annotations

import math
import os
import subprocess
from collections.abc import Mapping, Sequence
from types import TracebackType
from typing import IO

from foundation_tools.cli_transaction.cli_process_start_result import CLIProcessStartResult
from foundation_tools.cli_transaction.cliTransact import CLITransactResult, ERROR_RETURN_CODE
from foundation_tools.cli_transaction.process_execution import ProcessExecution
from foundation_tools.standardized_logger import StandardizedLogger

_log = StandardizedLogger(name=__name__)


class CLIProcess:
    """Own one child and manage its lifecycle without threads or an event loop.

    Use ``start`` to obtain a typed launch result. ``wait`` timeouts leave the
    child running. ``stop`` escalates from terminate to kill after its grace
    period. The caller manages concurrency and owns any supplied stream files.
    Only the immediate child is owned; descendants are not signaled.
    """

    def __init__(self, process: subprocess.Popen[bytes], execution: ProcessExecution) -> None:
        """Store the owned child and its command preparation collaborator."""
        self._process = process
        self._execution = execution
        self._result: CLITransactResult | None = None

    @classmethod
    def start(
        cls,
        cli_command: str | list[str],
        *,
        cwd: str | os.PathLike[str] | None = None,
        env: Mapping[str, str] | None = None,
        stdin: int | IO[bytes] | IO[str] | None = subprocess.DEVNULL,
        stdout: int | IO[bytes] | IO[str] | None = subprocess.DEVNULL,
        stderr: int | IO[bytes] | IO[str] | None = subprocess.DEVNULL,
        shell: Sequence[str] | None = None,
    ) -> CLIProcessStartResult:
        """Launch a child, returning an owner or a contained framework error.

        Strings use ``bash -c`` or the explicit shell prefix. Lists run directly.
        Standard streams default to DEVNULL. Files, descriptors, and explicit
        inheritance via None are supported; PIPE is rejected because this class
        does not drain pipes. Redirected output is not captured in results.
        """
        execution = ProcessExecution(shell=shell, cwd=cwd, env=env)
        try:
            if not cli_command:
                raise ValueError("Empty command provided")
            if any(stream == subprocess.PIPE for stream in (stdin, stdout, stderr)):
                raise ValueError("PIPE is not supported; supply a file or DEVNULL")
            argv = execution.build_argv(cli_command)
            execution.log_issued(_log, argv)
            process = subprocess.Popen(
                argv,
                cwd=execution.cwd,
                env=execution.environment(),
                stdin=stdin,
                stdout=stdout,
                stderr=stderr,
                shell=False,
            )
            return CLIProcessStartResult(process=cls(process, execution))
        except Exception as error:
            diagnostic = f"Process launch failed: {error}"
            execution.log_output(_log, ERROR_RETURN_CODE, None, diagnostic)
            return CLIProcessStartResult(
                error=CLITransactResult(
                    return_code=ERROR_RETURN_CODE, stderr=diagnostic, success=False
                )
            )

    @property
    def pid(self) -> int:
        """Return the owned child PID."""
        return self._process.pid

    def poll(self) -> int | None:
        """Return the native exit code, or None while the child runs."""
        return self._process.poll()

    def wait(self, timeout: float | None = None) -> CLITransactResult | None:
        """Wait for completion; return None on timeout without stopping the child."""
        try:
            if timeout is not None:
                self._validate_timeout(timeout)
            if self._result is not None:
                return self._result
            return self._completed(self._process.wait(timeout=timeout))
        except subprocess.TimeoutExpired:
            return None
        except Exception as error:
            return self._error(f"Process wait failed: {error}")

    def stop(self, graceful_timeout: float = 5.0) -> CLITransactResult:
        """Terminate, wait for the grace period, then kill and reap if necessary.

        Repeated calls after completion return the stored terminal result. Signal
        exit codes remain failures even when cleanup finishes successfully.
        """
        try:
            self._validate_timeout(graceful_timeout)
            if self._result is not None:
                return self._result
            if self._process.poll() is None:
                try:
                    self._process.terminate()
                except ProcessLookupError:
                    pass  # The child exited between the status check and signal.
                try:
                    return self._completed(self._process.wait(timeout=graceful_timeout))
                except subprocess.TimeoutExpired:
                    try:
                        self._process.kill()
                    except ProcessLookupError:
                        pass  # The child exited before the forceful signal.
            return self._completed(self._process.wait())
        except Exception as error:
            result = self._error(f"Process stop failed: {error}")
            _log.error(
                "CLI process cleanup failed",
                pid=self.pid,
                diagnostic=self._execution.redact(result.stderr or ""),
            )
            return result

    def __enter__(self) -> CLIProcess:
        """Return this process owner."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Stop the child without suppressing a context-body exception."""
        self.stop()

    @staticmethod
    def _validate_timeout(timeout: float) -> None:
        if not math.isfinite(timeout) or timeout < 0:
            raise ValueError("Timeout must be finite and non-negative")

    def _completed(self, return_code: int) -> CLITransactResult:
        if self._result is None:
            self._execution.log_output(_log, return_code, None, None)
            self._result = CLITransactResult(return_code=return_code, success=return_code == 0)
        return self._result

    def _error(self, diagnostic: str) -> CLITransactResult:
        self._execution.log_output(_log, ERROR_RETURN_CODE, None, diagnostic)
        return CLITransactResult(return_code=ERROR_RETURN_CODE, stderr=diagnostic, success=False)
