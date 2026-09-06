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
from logging import getLogger
from typing import Generic, TypeVar, overload

from foundationTypes.data_model_helper import DataModelHelper

_log = getLogger(__name__)

# Constants
ERROR_RETURN_CODE = -1
SUCCESS_RETURN_CODE = 0
GRACE_PERIOD_CAP_SECONDS = 1.0

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

    def __init__(self, success_marker: str | None = None):
        self.success_marker = success_marker

    # -----------------------------------------------------------------------
    # MARK: - Public — stateless classmethod API
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

    @overload
    @classmethod
    def run_sync_with_model(
        cls,
        cli_command: type[T],
        output_parser: Callable[[str], T] | None = None,
        *,
        timeout: int | None = None,
        success_marker: str | None = None,
    ) -> "CLITransactResultModel[T]": ...

    @overload
    @classmethod
    def run_sync_with_model(
        cls,
        cli_command: str | list[str],
        output_parser: Callable[[str], T],
        *,
        timeout: int | None = None,
        success_marker: str | None = None,
    ) -> "CLITransactResultModel[T]": ...

    @classmethod
    def run_sync_with_model(
        cls,
        cli_command: "str | list[str] | type[T]",
        output_parser: Callable[[str], T] | None = None,
        *,
        timeout: int | None = None,
        success_marker: str | None = None,
    ) -> "CLITransactResultModel[T]":
        """Execute synchronously and parse stdout into a data model.

        Parsing runs only on success with non-empty stdout, and never changes the
        execution ``success`` flag — a parser failure is appended to stderr.

        Pass a ``DataModelHelper`` subclass alone when it declares its own
        ``wire_invoke`` — the command to run and the canonical ``from_wire``
        parser are both pulled from the model::

            result = CLITransact.run_sync_with_model(DiskUsage)

        or supply an explicit ``(cli_command, output_parser)`` pair, e.g. when
        the caller constructs the command itself::

            result = CLITransact.run_sync_with_model(["cat", "coord.json"], GeoCoordinate.from_wire)
        """
        command, parser = cls._resolve_model_invocation(cli_command, output_parser)
        return cls(success_marker)._run_sync_with_model(command, parser, timeout)

    @overload
    @classmethod
    async def run_async_with_model(
        cls,
        cli_command: type[T],
        *,
        timeout: int | None = None,
        success_marker: str | None = None,
    ) -> "CLITransactResultModel[T]": ...

    @overload
    @classmethod
    async def run_async_with_model(
        cls,
        cli_command: str | list[str],
        output_parser: Callable[[str], T],
        *,
        timeout: int | None = None,
        success_marker: str | None = None,
    ) -> "CLITransactResultModel[T]": ...

    @classmethod
    async def run_async_with_model(
        cls,
        cli_command: "str | list[str] | type[T]",
        output_parser: Callable[[str], T] | None = None,
        *,
        timeout: int | None = None,
        success_marker: str | None = None,
    ) -> "CLITransactResultModel[T]":
        """Execute asynchronously and parse stdout into a data model.

        Parsing runs only on success with non-empty stdout, and never changes the
        execution ``success`` flag — a parser failure is appended to stderr.

        Accepts either a bare ``DataModelHelper`` subclass (using its own
        ``wire_invoke``/``from_wire``) or an explicit ``(cli_command,
        output_parser)`` pair — see ``run_sync_with_model`` for the two forms.
        """
        command, parser = cls._resolve_model_invocation(cli_command, output_parser)
        return await cls(success_marker)._run_async_with_model(command, parser, timeout)

    @staticmethod
    def _resolve_model_invocation(
        cli_command: "str | list[str] | type[T]",
        output_parser: Callable[[str], T] | None,
    ) -> "tuple[str | list[str], Callable[[str], T]]":
        """Resolve the (command, parser) pair for the ``*_with_model`` methods.

        ``cli_command`` is either a plain command (paired with an explicit
        ``output_parser``) or a ``DataModelHelper`` subclass, in which case the
        command and parser are pulled from the model's own ``wire_invoke`` and
        ``from_wire``. The CLI transport only supports a ``str``/``list[str]``
        ``wire_invoke``; a ``type[DataModelHelper]`` arm (a request-model class,
        meaningful for other transports, e.g. a request/response pair over a
        socket transaction) has no defined meaning here — do not invent one
        (e.g. no stdin piping).
        """
        if isinstance(cli_command, type):
            model_cls = cli_command
            invocation = model_cls.wire_invoke
            if invocation is None:
                raise ValueError(
                    f"{model_cls.__name__}.wire_invoke is not set; either set it or call "
                    "with an explicit (cli_command, output_parser) pair."
                )
            if isinstance(invocation, type):
                raise ValueError(
                    f"{model_cls.__name__}.wire_invoke is {invocation.__name__}; CLITransact "
                    "only supports a str/list[str] wire_invoke — a type[DataModelHelper] "
                    "request is not meaningful for the CLI transport."
                )
            parser = output_parser if output_parser is not None else model_cls.from_wire
            return invocation, parser

        if output_parser is None:
            raise ValueError(
                "output_parser is required when cli_command is not a DataModelHelper type"
            )
        return cli_command, output_parser

    # -----------------------------------------------------------------------
    # MARK: - Private — implementation
    # -----------------------------------------------------------------------

    def _validate_command(self, cli_command: str | list[str]) -> CLITransactResult | None:
        """Validate command input and return an error result if invalid."""
        if not cli_command:
            return self._framework_error("Empty command provided")
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

    def _finalize_result(
        self, return_code: int, raw_stdout: str, raw_stderr: str
    ) -> CLITransactResult:
        """Build the result for a completed (non-framework-error) execution."""
        return CLITransactResult(
            return_code=return_code,
            stdout=self._normalize_output(raw_stdout),
            stderr=self._normalize_output(raw_stderr),
            success=self._determine_success(return_code, raw_stdout),
        )

    def _framework_error(self, stderr: str, stdout: str | None = None) -> CLITransactResult:
        """Build a framework-level failure result (invalid input, timeout, contained exception)."""
        return CLITransactResult(
            return_code=ERROR_RETURN_CODE,
            stdout=self._normalize_output(stdout),
            stderr=self._normalize_output(stderr),
            success=False,
        )

    def _decode_timeout_capture(self, value: str | bytes | None) -> str | None:
        """Decode a subprocess.TimeoutExpired stdout/stderr capture (str or bytes) to str."""
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return bytes(value).decode(errors="replace")

    def _attach_model(
        self, base_result: CLITransactResult, output_parser: Callable[[str], T]
    ) -> CLITransactResultModel[T]:
        """Wrap a base result in CLITransactResultModel and attempt model parsing.

        Parsing runs only when the base result succeeded and stdout is non-empty; a
        parser failure is swallowed and appended to stderr — it never changes success.
        """
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
                    f"{base_result.stderr or ''}\nModel parsing failed: {parse_error}"
                ).strip()

        return extended_result

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
                errors="replace",
                timeout=timeout,
                shell=isinstance(cli_command, str),
                check=False,
            )

            return self._finalize_result(
                process_result.returncode,
                process_result.stdout or "",
                process_result.stderr or "",
            )
        except subprocess.TimeoutExpired as timeout_error:
            # Surface partial stdout/stderr captured before the timeout.
            partial_stdout = self._decode_timeout_capture(timeout_error.stdout)
            partial_stderr = (self._decode_timeout_capture(timeout_error.stderr) or "").strip()

            timeout_message = f"Timeout after {timeout} seconds"
            combined_stderr = (
                f"{timeout_message}\n{partial_stderr}" if partial_stderr else timeout_message
            )

            return self._framework_error(combined_stderr, stdout=partial_stdout)
        except Exception as exec_error:  # pylint: disable=broad-exception-caught
            # Total containment: no exception escapes the public API. BaseException
            # (KeyboardInterrupt / SystemExit) is intentionally allowed to propagate.
            return self._framework_error(f"Command execution failed: {exec_error}")

    def _run_sync_with_model(
        self,
        cli_command: str | list[str],
        output_parser: Callable[[str], T],
        timeout: int | None = None,
    ) -> CLITransactResultModel[T]:
        return self._attach_model(self._run_sync(cli_command, timeout), output_parser)

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
                    # Cap the grace window at the caller's own timeout so a short
                    # timeout doesn't pay a disproportionate fixed overhead before
                    # escalating to SIGKILL.
                    grace_period = (
                        min(GRACE_PERIOD_CAP_SECONDS, timeout)
                        if timeout is not None
                        else GRACE_PERIOD_CAP_SECONDS
                    )
                    try:
                        await asyncio.wait_for(process.wait(), timeout=grace_period)
                    except asyncio.TimeoutError:
                        process.kill()
                        await process.wait()

                return self._framework_error(f"Timeout after {timeout} seconds")

            stdout_text = stdout.decode(errors="replace") if stdout else ""
            stderr_text = stderr.decode(errors="replace") if stderr else ""

            return_code = (
                process.returncode if process.returncode is not None else ERROR_RETURN_CODE
            )

            return self._finalize_result(return_code, stdout_text, stderr_text)
        except asyncio.CancelledError:
            # Cooperative task cancellation is NOT an execution failure: it is a
            # BaseException and must propagate unchanged (never swallowed, never
            # turned into a CLITransactResult, timeout semantics untouched). But we
            # still own the child we spawned — reap it here with the same
            # graceful-then-forceful cascade the timeout path uses so a cancelled
            # transaction never leaves an orphan or zombie.
            if process is not None:
                child_pid = process.pid
                try:
                    if process.returncode is None:
                        process.terminate()
                        grace_period = (
                            min(GRACE_PERIOD_CAP_SECONDS, timeout)
                            if timeout is not None
                            else GRACE_PERIOD_CAP_SECONDS
                        )
                        try:
                            await asyncio.wait_for(process.wait(), timeout=grace_period)
                        except asyncio.TimeoutError:
                            process.kill()
                            await process.wait()
                except Exception:  # pylint: disable=broad-exception-caught
                    # Best-effort reaping; the child may already be gone.
                    pass
                _log.warning(
                    "CLITransact async child pid=%s terminated and reaped after task "
                    "cancellation",
                    child_pid,
                )
            raise
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

            return self._framework_error(f"Command execution failed: {exec_error}")

    async def _run_async_with_model(
        self,
        cli_command: str | list[str],
        output_parser: Callable[[str], T],
        timeout: int | None = None,
    ) -> CLITransactResultModel[T]:
        return self._attach_model(await self._run_async(cli_command, timeout), output_parser)
