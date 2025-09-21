"""
CLI Transaction Manager

A Python module for managing command-line interface transactions with support for
both synchronous and asynchronous execution, timeout handling, and success validation.

This module provides a robust interface for executing shell commands with proper
error handling, timeout management, and optional success string validation.

Classes:
    CLITransactResult: Data class containing command execution results
    CLITransact: Main transaction manager for CLI operations

Example Usage:
    # Basic synchronous execution
    cli = CLITransact()
    result = cli.run_sync("ls -la")
    if result.success:
        print(result.stdout)

    # With success string validation
    cli = CLITransact(success_string="Success")
    result = cli.run_sync("deployment-script.sh")

    # Asynchronous execution with timeout
    import asyncio

    async def main():
        cli = CLITransact()
        result = await cli.run_async(["python", "script.py"], timeout=30)
        return result

    result = asyncio.run(main())

Generated via prompt spec:
provide a python class that manages transactions with the cli (via subprocess / PIPE)
that handles both for sync, async and timeout? It should optionally look for a success
string, and maintain a simple type for the return code, which contains an optional for
err and the stdout.
"""

import subprocess
import asyncio
from dataclasses import dataclass
from typing import Optional, Union, List


# Constants
ERROR_RETURN_CODE = -1
SUCCESS_RETURN_CODE = 0


@dataclass
class CLITransactResult:
    """
    Result container for CLI command execution.

    Attributes:
        return_code (int): The exit code returned by the command.
                          0 typically indicates success, non-zero indicates error.
                          -1 is used for internal errors (timeouts, exceptions).
        stdout (Optional[str]): Standard output from the command, if any.
                               None if no output or command failed to start.
        stderr (Optional[str]): Standard error output from the command, if any.
                               None if no error output.
        success (bool): Whether the command was considered successful.
                       Based on return_code == 0 and optional success_string validation.

    Example:
        result = CLITransactResult(
            return_code=0,
            stdout="Hello World",
            stderr=None,
            success=True
        )
    """

    return_code: int
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    success: bool = False


class CLITransact:
    """
    CLI Transaction Manager for executing shell commands with robust error handling.

    This class provides both synchronous and asynchronous methods for executing
    shell commands with support for timeouts and optional success string validation.

    Attributes:
        success_string (Optional[str]): If provided, the command output must contain
                                       this string for the operation to be considered
                                       successful, even if return_code is 0.

    Example:
        # Basic usage
        cli = CLITransact()
        result = cli.run_sync("echo 'Hello World'")

        # With success validation
        cli = CLITransact(success_string="deployment complete")
        result = cli.run_sync("./deploy.sh")
        if result.success:
            print("Deployment successful")
    """

    def __init__(self, success_string: Optional[str] = None):
        """
        Initialize CLITransact instance.

        Args:
            success_string (Optional[str]): String that must be present in stdout
                                          for the command to be considered successful.
                                          If None, success is determined solely by
                                          return_code == 0.
        """
        self.success_string = success_string

    def _validate_command(
        self, command: Union[str, List[str]]
    ) -> Optional[CLITransactResult]:
        """Validate command input and return error result if invalid."""
        if not command:
            return CLITransactResult(
                return_code=ERROR_RETURN_CODE,
                stderr="Empty command provided",
                success=False,
            )
        return None

    def _determine_success(self, return_code: int, stdout: str) -> bool:
        """Determine if command execution was successful."""
        if return_code != SUCCESS_RETURN_CODE:
            return False
        if self.success_string and self.success_string not in stdout:
            return False
        return True

    def _normalize_output(self, output: Optional[str]) -> Optional[str]:
        """Normalize output string, returning None for empty strings."""
        if not output:
            return None
        stripped = output.strip()
        return stripped if stripped else None

    def run_sync(
        self, command: Union[str, List[str]], timeout: Optional[int] = None
    ) -> CLITransactResult:
        """
        Execute a command synchronously.

        Args:
            command (Union[str, List[str]]): Command to execute. Can be a string
                                            (executed via shell) or list of arguments.
                                            WARNING: String commands are executed via shell
                                            and may be vulnerable to injection attacks.
            timeout (Optional[int]): Maximum execution time in seconds.
                                    If None, no timeout is applied.

        Returns:
            CLITransactResult: Result object containing return code, stdout,
                              stderr, and success status.

        Raises:
            No exceptions are raised; all errors are captured in the result object.

        Example:
            # String command (use with caution)
            result = cli.run_sync("ls -la /tmp")

            # List command (preferred for security)
            result = cli.run_sync(["python", "-c", "print('hello')"])

            # With timeout
            result = cli.run_sync("sleep 10", timeout=5)
            if not result.success:
                print(f"Command failed: {result.stderr}")
        """
        # Validate input
        validation_error = self._validate_command(command)
        if validation_error:
            return validation_error

        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
                shell=isinstance(command, str),
                check=False,
            )

            stdout_text = result.stdout or ""
            success = self._determine_success(result.returncode, stdout_text)

            return CLITransactResult(
                return_code=result.returncode,
                stdout=self._normalize_output(stdout_text),
                stderr=self._normalize_output(result.stderr),
                success=success,
            )
        except subprocess.TimeoutExpired as e:
            # Handle text vs bytes output consistently
            stdout_text: str | None = None
            if e.stdout is not None:
                if isinstance(e.stdout, str):
                    stdout_text = e.stdout
                else:
                    # Handle bytes, bytearray, memoryview
                    stdout_text = bytes(e.stdout).decode()
            return CLITransactResult(
                return_code=ERROR_RETURN_CODE,
                stdout=self._normalize_output(stdout_text),
                stderr=f"Timeout after {timeout} seconds",
                success=False,
            )
        except Exception as e:
            return CLITransactResult(
                return_code=ERROR_RETURN_CODE,
                stderr=f"Command execution failed: {str(e)}",
                success=False,
            )

    async def run_async(
        self, command: Union[str, List[str]], timeout: Optional[int] = None
    ) -> CLITransactResult:
        """
        Execute a command asynchronously.

        Args:
            command (Union[str, List[str]]): Command to execute. Can be a string
                                            (executed via bash -c) or list of arguments.
                                            WARNING: String commands are executed via shell
                                            and may be vulnerable to injection attacks.
            timeout (Optional[int]): Maximum execution time in seconds.
                                    If None, no timeout is applied.

        Returns:
            CLITransactResult: Result object containing return code, stdout,
                              stderr, and success status.

        Raises:
            No exceptions are raised; all errors are captured in the result object.

        Example:
            import asyncio

            async def main():
                cli = CLITransact()

                # String command (use with caution)
                result = await cli.run_async("ls -la /tmp")

                # List command (preferred for security)
                result = await cli.run_async(["python", "-c", "print('hello')"])

                # With timeout
                result = await cli.run_async("sleep 10", timeout=5)
                if not result.success:
                    print(f"Command failed: {result.stderr}")

                return result

            result = asyncio.run(main())
        """
        # Validate input
        validation_error = self._validate_command(command)
        if validation_error:
            return validation_error

        proc = None
        try:
            proc = await asyncio.create_subprocess_exec(
                *command if isinstance(command, list) else ["bash", "-c", command],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout)
            except asyncio.TimeoutError:
                # Proper cleanup on timeout
                if proc:
                    proc.kill()
                    try:
                        await asyncio.wait_for(proc.wait(), timeout=1.0)
                    except asyncio.TimeoutError:
                        proc.terminate()
                        await proc.wait()
                return CLITransactResult(
                    return_code=ERROR_RETURN_CODE,
                    stdout=None,
                    stderr=f"Timeout after {timeout} seconds",
                    success=False,
                )

            stdout_text = stdout.decode() if stdout else ""
            stderr_text = stderr.decode() if stderr else ""

            # proc.returncode should be set after communicate(), but handle None case
            return_code = (
                proc.returncode if proc.returncode is not None else ERROR_RETURN_CODE
            )
            success = self._determine_success(return_code, stdout_text)

            return CLITransactResult(
                return_code=return_code,
                stdout=self._normalize_output(stdout_text),
                stderr=self._normalize_output(stderr_text),
                success=success,
            )
        except Exception as e:
            # Cleanup on exception
            if proc:
                try:
                    proc.kill()
                    await proc.wait()
                except:
                    pass
            return CLITransactResult(
                return_code=ERROR_RETURN_CODE,
                stderr=f"Command execution failed: {str(e)}",
                success=False,
            )
