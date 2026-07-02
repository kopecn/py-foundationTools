"""
CLI Transaction Manager

A Python module for managing command-line interface transactions with support for
both synchronous and asynchronous execution, timeout handling, and success validation.

The public API is a set of four stateless classmethods (sync/async × plain/model).
Each call optionally takes a ``success_marker`` keyword: a substring that MUST appear in
stdout for the command to be considered successful, even when the exit code is 0. All
failures (timeouts, exceptions, non-zero exit) are captured into a ``CLITransactResult``;
nothing escapes the API.

Classes:
    CLITransactResult: Data class containing command execution results
    CLITransactResultModel: CLITransactResult extended with a parsed data model
    CLITransact: Stateless transaction manager for CLI operations

Example Usage:
    # Basic synchronous execution
    result = CLITransact.run_sync("ls -la")
    if result.success:
        print(result.stdout)

    # With success-marker validation
    result = CLITransact.run_sync("deployment-script.sh", success_marker="Success")

    # Asynchronous execution with timeout
    import asyncio

    async def main():
        return await CLITransact.run_async(["python", "script.py"], timeout=30)

    result = asyncio.run(main())
"""

import asyncio
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

from foundationTypes.dataModelHelper import DataModelHelper

# Constants
ERROR_RETURN_CODE = -1
SUCCESS_RETURN_CODE = 0

# Type variable for generic serialization
T = TypeVar("T", bound=DataModelHelper)


@dataclass
class CLITransactResult:
    """
    Result container for CLI command execution.

    Attributes:
        return_code: The exit code returned by the command. ``SUCCESS_RETURN_CODE`` (0)
                     indicates success; a positive value is a command-defined error;
                     ``ERROR_RETURN_CODE`` (-1) is the framework-level sentinel reserved
                     for timeouts, invalid input, and contained exceptions.
        stdout: Normalized standard output, or None when empty/whitespace-only.
        stderr: Normalized standard error, or None when empty/whitespace-only.
        success: Computed field — return_code == 0 AND (no success_marker OR the marker
                 is present in stdout).
    """

    return_code: int
    stdout: str | None = None
    stderr: str | None = None
    success: bool = False


@dataclass
class CLITransactResultModel(CLITransactResult, Generic[T]):
    """
    Extended result container that includes a parsed data model.

    Attributes:
        model: Parsed data model instance created from stdout. None if the command
               failed, stdout was empty, or the parser raised.
    """

    model: T | None = None


class CLITransact:
    """
    Stateless CLI Transaction Manager.

    The public surface is four classmethods — ``run_sync``, ``run_async``,
    ``run_sync_with_model``, ``run_async_with_model``. Each constructs a short-lived
    instance carrying the per-call ``success_marker`` and delegates to the private
    implementation. No exception escapes a public method (``BaseException`` excepted).

    Example:
        result = CLITransact.run_sync("echo 'Hello World'")

        result = CLITransact.run_sync("./deploy.sh", success_marker="deployment complete")
        if result.success:
            print("Deployment successful")
    """

    # -----------------------------------------------------------------------
    # Public — stateless classmethod API
    # -----------------------------------------------------------------------

    @classmethod
    def run_sync(
        cls,
        cli_command: str | list[str],
        *,
        timeout: int | None = None,
        success_marker: str | None = None,
    ) -> "CLITransactResult":
        """Execute a command synchronously.

        String commands run via the shell (``shell=True``) and are vulnerable to
        injection; list commands are executed directly and preferred.
        """
        return cls(success_marker)._run_sync(cli_command, timeout)

    @classmethod
    async def run_async(
        cls,
        cli_command: str | list[str],
        *,
        timeout: int | None = None,
        success_marker: str | None = None,
    ) -> "CLITransactResult":
        """Execute a command asynchronously.

        String commands run via ``bash -c``; list commands are executed directly via
        ``create_subprocess_exec`` and preferred.
        """
        return await cls(success_marker)._run_async(cli_command, timeout)

    @classmethod
    def run_sync_with_model(
        cls,
        cli_command: str | list[str],
        output_parser: Callable[[str], T],
        *,
        timeout: int | None = None,
        success_marker: str | None = None,
    ) -> "CLITransactResultModel[T]":
        """Execute synchronously and parse stdout into a data model.

        Parsing runs only on success with non-empty stdout, and never changes the
        execution ``success`` flag — a parser failure is appended to stderr.
        """
        return cls(success_marker)._run_sync_with_model(cli_command, output_parser, timeout)

    @classmethod
    async def run_async_with_model(
        cls,
        cli_command: str | list[str],
        output_parser: Callable[[str], T],
        *,
        timeout: int | None = None,
        success_marker: str | None = None,
    ) -> "CLITransactResultModel[T]":
        """Execute asynchronously and parse stdout into a data model.

        Parsing runs only on success with non-empty stdout, and never changes the
        execution ``success`` flag — a parser failure is appended to stderr.
        """
        return await cls(success_marker)._run_async_with_model(cli_command, output_parser, timeout)

    # -----------------------------------------------------------------------
    # Private — constructor and implementation
    # -----------------------------------------------------------------------

    def __init__(self, success_marker: str | None = None):
        self.success_marker = success_marker

    def _validate_command(self, cli_command: str | list[str]) -> CLITransactResult | None:
        """Validate command input and return an error result if invalid."""
        if not cli_command:
            return CLITransactResult(
                return_code=ERROR_RETURN_CODE,
                stderr="Empty command provided",
                success=False,
            )
        return None

    def _determine_success(self, return_code: int, stdout: str) -> bool:
        """Compute semantic success: exit code 0 plus optional marker presence."""
        if return_code != SUCCESS_RETURN_CODE:
            return False
        if self.success_marker and self.success_marker not in stdout:
            return False
        return True

    def _normalize_output(self, output: str | None) -> str | None:
        """Normalize output: empty / whitespace-only collapses to None."""
        if not output:
            return None
        stripped = output.strip()
        return stripped if stripped else None

    def _run_sync(
        self, cli_command: str | list[str], timeout: int | None = None
    ) -> CLITransactResult:
        validation_error = self._validate_command(cli_command)
        if validation_error:
            return validation_error

        try:
            process_result = subprocess.run(
                cli_command,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=isinstance(cli_command, str),
                check=False,
            )

            stdout_text = process_result.stdout or ""
            success = self._determine_success(process_result.returncode, stdout_text)

            return CLITransactResult(
                return_code=process_result.returncode,
                stdout=self._normalize_output(stdout_text),
                stderr=self._normalize_output(process_result.stderr),
                success=success,
            )
        except subprocess.TimeoutExpired as timeout_error:
            # Surface partial stdout captured before the timeout, normalizing text/bytes.
            partial_stdout_on_timeout: str | None = None
            if timeout_error.stdout is not None:
                if isinstance(timeout_error.stdout, str):
                    partial_stdout_on_timeout = timeout_error.stdout
                else:
                    partial_stdout_on_timeout = bytes(timeout_error.stdout).decode()

            return CLITransactResult(
                return_code=ERROR_RETURN_CODE,
                stdout=self._normalize_output(partial_stdout_on_timeout),
                stderr=f"Timeout after {timeout} seconds",
                success=False,
            )
        except Exception as exec_error:  # pylint: disable=broad-exception-caught
            # Total containment: no exception escapes the public API. BaseException
            # (KeyboardInterrupt / SystemExit) is intentionally allowed to propagate.
            return CLITransactResult(
                return_code=ERROR_RETURN_CODE,
                stderr=f"Command execution failed: {str(exec_error)}",
                success=False,
            )

    def _run_sync_with_model(
        self,
        cli_command: str | list[str],
        output_parser: Callable[[str], T],
        timeout: int | None = None,
    ) -> CLITransactResultModel[T]:
        base_result = self._run_sync(cli_command, timeout)

        extended_result = CLITransactResultModel[T](
            return_code=base_result.return_code,
            stdout=base_result.stdout,
            stderr=base_result.stderr,
            success=base_result.success,
            model=None,
        )

        if base_result.success and base_result.stdout:
            try:
                extended_result.model = output_parser(base_result.stdout)
            except Exception as parse_error:  # pylint: disable=broad-exception-caught
                # Parsing is advisory: any parser failure is contained and never changes
                # the execution success flag — raw execution truth wins.
                extended_result.stderr = (
                    f"{base_result.stderr or ''}\nModel parsing failed: {str(parse_error)}"
                ).strip()

        return extended_result

    async def _run_async(
        self, cli_command: str | list[str], timeout: int | None = None
    ) -> CLITransactResult:
        validation_error = self._validate_command(cli_command)
        if validation_error:
            return validation_error

        process = None
        try:
            process = await asyncio.create_subprocess_exec(
                *cli_command if isinstance(cli_command, list) else ["bash", "-c", cli_command],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout)
            except asyncio.TimeoutError:
                # Forceful cleanup cascade: ask politely first (SIGTERM), escalate to
                # SIGKILL only if the process ignores the graceful signal. The reverse
                # order is a no-op — SIGKILL is uncatchable, so a later SIGTERM signals
                # an already-dead process.
                if process:
                    process.terminate()
                    try:
                        await asyncio.wait_for(process.wait(), timeout=1.0)
                    except asyncio.TimeoutError:
                        process.kill()
                        await process.wait()

                return CLITransactResult(
                    return_code=ERROR_RETURN_CODE,
                    stdout=None,
                    stderr=f"Timeout after {timeout} seconds",
                    success=False,
                )

            stdout_text = stdout.decode() if stdout else ""
            stderr_text = stderr.decode() if stderr else ""

            return_code = (
                process.returncode if process.returncode is not None else ERROR_RETURN_CODE
            )
            success = self._determine_success(return_code, stdout_text)

            return CLITransactResult(
                return_code=return_code,
                stdout=self._normalize_output(stdout_text),
                stderr=self._normalize_output(stderr_text),
                success=success,
            )
        except Exception as exec_error:  # pylint: disable=broad-exception-caught
            # Total containment: no exception escapes the public API. BaseException
            # (KeyboardInterrupt / SystemExit) is intentionally allowed to propagate.
            if process:
                try:
                    process.kill()
                    await process.wait()
                except Exception:  # pylint: disable=broad-exception-caught
                    # Best-effort cleanup; the process may already be gone.
                    pass

            return CLITransactResult(
                return_code=ERROR_RETURN_CODE,
                stderr=f"Command execution failed: {str(exec_error)}",
                success=False,
            )

    async def _run_async_with_model(
        self,
        cli_command: str | list[str],
        output_parser: Callable[[str], T],
        timeout: int | None = None,
    ) -> CLITransactResultModel[T]:
        base_result = await self._run_async(cli_command, timeout)

        extended_result = CLITransactResultModel[T](
            return_code=base_result.return_code,
            stdout=base_result.stdout,
            stderr=base_result.stderr,
            success=base_result.success,
            model=None,
        )

        if base_result.success and base_result.stdout:
            try:
                extended_result.model = output_parser(base_result.stdout)
            except Exception as parse_error:  # pylint: disable=broad-exception-caught
                # Parsing is advisory: any parser failure is contained and never changes
                # the execution success flag — raw execution truth wins.
                extended_result.stderr = (
                    f"{base_result.stderr or ''}\nModel parsing failed: {str(parse_error)}"
                ).strip()

        return extended_result
