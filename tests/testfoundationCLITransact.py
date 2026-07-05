"""
Unit tests for CLITransact module.

Comprehensive test suite covering synchronous and asynchronous command execution,
timeout handling, success validation, and error scenarios. Exercises the stateless
classmethod API (``run_sync`` / ``run_async`` / ``*_with_model``) with the per-call
``success_marker`` keyword.
"""

import asyncio
import os
import subprocess
import sys
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# Add src to path for import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from foundation_tools.cli_transaction.cliTransact import (  # pylint: disable=wrong-import-position
    ERROR_RETURN_CODE,
    SUCCESS_RETURN_CODE,
    CLITransact,
    CLITransactResult,
    CLITransactResultModel,
)
from foundationTypes.data_model_helper import (
    DataModelHelper,  # pylint: disable=wrong-import-position
)


# Test data model for unit tests
class MockDataModel(DataModelHelper):
    """Simple test data model for testing serialization."""

    def __init__(self, value: str, count: int) -> None:
        self.value = value
        self.count = count

    @staticmethod
    def from_dict(obj: Any) -> "MockDataModel":
        return MockDataModel(obj["value"], obj["count"])

    def to_dict(self) -> dict[str, Any]:
        return {"value": self.value, "count": self.count}

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, MockDataModel)
            and self.value == other.value
            and self.count == other.count
        )


def parse_echo_output(output: str) -> MockDataModel:
    """Test parser that parses echo output into MockDataModel."""
    lines = output.strip().split("\n")
    return MockDataModel(value=lines[0], count=len(lines))


def parse_failing_serializer(output: str) -> MockDataModel:
    """Test parser that always fails."""
    raise ValueError("Serialization failed")


def parse_nonstdlib_failing_serializer(output: str) -> MockDataModel:
    """Test parser that fails with a non-stdlib-validation exception type."""
    raise RuntimeError("Unexpected serializer failure")


class TestCLITransactResult:
    """Test cases for CLITransactResult data class."""

    def test_default_initialization(self) -> None:
        """Test default CLITransactResult initialization."""
        result = CLITransactResult(return_code=0)
        assert result.return_code == 0
        assert result.stdout is None
        assert result.stderr is None
        assert result.success is False

    def test_full_initialization(self) -> None:
        """Test CLITransactResult with all fields."""
        result = CLITransactResult(
            return_code=0, stdout="Hello World", stderr="Warning message", success=True
        )
        assert result.return_code == 0
        assert result.stdout == "Hello World"
        assert result.stderr == "Warning message"
        assert result.success is True


class TestCLITransactResultModel:
    """Test cases for CLITransactResultModel data class."""

    def test_default_initialization(self) -> None:
        """Test default CLITransactResultModel initialization."""
        result = CLITransactResultModel[MockDataModel](return_code=0)
        assert result.return_code == 0
        assert result.stdout is None
        assert result.stderr is None
        assert result.success is False
        assert result.model is None

    def test_full_initialization_with_model(self) -> None:
        """Test CLITransactResultModel with all fields including model."""
        test_model = MockDataModel("test", 42)
        result = CLITransactResultModel[MockDataModel](
            return_code=0,
            stdout="Hello World",
            stderr="Warning message",
            success=True,
            model=test_model,
        )
        assert result.return_code == 0
        assert result.stdout == "Hello World"
        assert result.stderr == "Warning message"
        assert result.success is True
        assert result.model == test_model
        assert result.model is not None
        assert result.model.value == "test"
        assert result.model.count == 42


class TestCLITransact:
    """Test cases for CLITransact instance internals."""

    def test_initialization_default(self) -> None:
        """Test CLITransact initialization with defaults."""
        cli = CLITransact()
        assert cli.success_marker is None

    def test_initialization_with_success_marker(self) -> None:
        """Test CLITransact initialization with success marker."""
        cli = CLITransact(success_marker="SUCCESS")
        assert cli.success_marker == "SUCCESS"

    def test_validate_command_empty_string(self) -> None:
        """Test command validation with empty string."""
        cli = CLITransact()
        result = cli._validate_command("")  # pylint: disable=protected-access
        assert result is not None
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Empty command provided" in result.stderr

    def test_validate_command_empty_list(self) -> None:
        """Test command validation with empty list."""
        cli = CLITransact()
        result = cli._validate_command([])  # pylint: disable=protected-access
        assert result is not None
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Empty command provided" in result.stderr

    def test_validate_command_valid(self) -> None:
        """Test command validation with valid command."""
        cli = CLITransact()
        result = cli._validate_command("echo hello")  # pylint: disable=protected-access
        assert result is None

    def test_determine_success_with_return_code_zero(self) -> None:
        """Test success determination with return code 0."""
        cli = CLITransact()
        assert cli._determine_success(SUCCESS_RETURN_CODE, "output") is True  # pylint: disable=protected-access

    def test_determine_success_with_return_code_nonzero(self) -> None:
        """Test success determination with non-zero return code."""
        cli = CLITransact()
        assert cli._determine_success(1, "output") is False  # pylint: disable=protected-access

    def test_determine_success_with_marker_present(self) -> None:
        """Test success determination with success marker present."""
        cli = CLITransact(success_marker="SUCCESS")
        assert (
            cli._determine_success(SUCCESS_RETURN_CODE, "Operation SUCCESS completed")  # pylint: disable=protected-access
            is True
        )

    def test_determine_success_with_marker_missing(self) -> None:
        """Test success determination with success marker missing."""
        cli = CLITransact(success_marker="SUCCESS")
        assert (
            cli._determine_success(SUCCESS_RETURN_CODE, "Operation completed") is False  # pylint: disable=protected-access
        )

    def test_determine_success_with_error_sentinel(self) -> None:
        """The framework error sentinel (-1) is always a failure, marker or not."""
        cli = CLITransact()
        assert cli._determine_success(ERROR_RETURN_CODE, "output") is False  # pylint: disable=protected-access

        cli_with_marker = CLITransact(success_marker="SUCCESS")
        assert (
            cli_with_marker._determine_success(ERROR_RETURN_CODE, "SUCCESS")  # pylint: disable=protected-access
            is False
        )

    def test_normalize_output_none(self) -> None:
        """Test output normalization with None input."""
        cli = CLITransact()
        assert cli._normalize_output(None) is None  # pylint: disable=protected-access

    def test_normalize_output_empty_string(self) -> None:
        """Test output normalization with empty string."""
        cli = CLITransact()
        assert cli._normalize_output("") is None  # pylint: disable=protected-access

    def test_normalize_output_whitespace_only(self) -> None:
        """Test output normalization with whitespace only."""
        cli = CLITransact()
        assert cli._normalize_output("   \n\t  ") is None  # pylint: disable=protected-access

    def test_normalize_output_with_content(self) -> None:
        """Test output normalization with actual content."""
        cli = CLITransact()
        assert cli._normalize_output("  hello world  \n") == "hello world"  # pylint: disable=protected-access


class TestCLITransactSync:
    """Test cases for synchronous command execution."""

    def test_run_sync_empty_command(self) -> None:
        """Test synchronous execution with empty command."""
        result = CLITransact.run_sync("")
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Empty command provided" in result.stderr
        assert result.success is False

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_run_sync_successful_command(self) -> None:
        """Test synchronous execution of successful command."""
        result = CLITransact.run_sync(["echo", "hello"])
        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.stdout == "hello"
        assert result.stderr is None
        assert result.success is True

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_run_sync_failing_command(self) -> None:
        """Test synchronous execution of failing command."""
        result = CLITransact.run_sync(["false"])
        assert result.return_code != SUCCESS_RETURN_CODE
        assert result.success is False

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_run_sync_with_stderr(self) -> None:
        """Test synchronous execution with stderr output."""
        result = CLITransact.run_sync(["sh", "-c", "echo 'error' >&2; echo 'output'"])
        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.stdout == "output"
        assert result.stderr == "error"
        assert result.success is True

    def test_run_sync_with_marker_present(self) -> None:
        """Test synchronous execution with success marker validation (present)."""
        result = CLITransact.run_sync(
            ["echo", "Operation SUCCESS completed"], success_marker="SUCCESS"
        )
        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is True

    def test_run_sync_with_marker_missing(self) -> None:
        """Test synchronous execution with success marker validation (missing)."""
        result = CLITransact.run_sync(["echo", "Operation completed"], success_marker="SUCCESS")
        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is False

    @patch("subprocess.run")
    def test_run_sync_timeout_exception(self, mock_run: Any) -> None:
        """Test synchronous execution timeout handling."""
        mock_timeout = subprocess.TimeoutExpired(cmd=["sleep", "10"], timeout=1)
        mock_timeout.stdout = b"partial output"
        mock_run.side_effect = mock_timeout

        result = CLITransact.run_sync(["sleep", "10"], timeout=1)
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Timeout after 1 seconds" in result.stderr
        assert result.stdout == "partial output"
        assert result.success is False

    @patch("subprocess.run")
    def test_run_sync_timeout_preserves_partial_stderr(self, mock_run: Any) -> None:
        """Test that partial stderr (bytes) is preserved on sync timeout."""
        mock_timeout = subprocess.TimeoutExpired(cmd=["sleep", "10"], timeout=1)
        mock_timeout.stdout = b"partial output"
        mock_timeout.stderr = b"partial error"
        mock_run.side_effect = mock_timeout

        result = CLITransact.run_sync(["sleep", "10"], timeout=1)
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stdout == "partial output"
        assert result.stderr is not None
        assert "Timeout after 1 seconds" in result.stderr
        assert "partial error" in result.stderr
        assert result.success is False

    @patch("subprocess.run")
    def test_run_sync_timeout_stderr_str_type(self, mock_run: Any) -> None:
        """Test that partial stderr (str) is preserved on sync timeout."""
        mock_timeout = subprocess.TimeoutExpired(
            cmd=["sleep", "10"], timeout=1, output="partial output", stderr="partial error"
        )
        mock_run.side_effect = mock_timeout

        result = CLITransact.run_sync(["sleep", "10"], timeout=1)
        assert result.stdout == "partial output"
        assert result.stderr is not None
        assert "Timeout after 1 seconds" in result.stderr
        assert "partial error" in result.stderr

    @patch("subprocess.run")
    def test_run_sync_forwards_errors_replace_kwarg(self, mock_run: Any) -> None:
        """Test that subprocess.run is called with errors='replace' for decode robustness."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=["echo", "x"], returncode=0, stdout="x", stderr=""
        )

        CLITransact.run_sync(["echo", "x"])

        _, call_kwargs = mock_run.call_args
        assert call_kwargs["errors"] == "replace"

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_run_sync_invalid_utf8_stdout_does_not_raise(self) -> None:
        """Invalid byte sequences in stdout must not turn a successful run into a failure."""
        result = CLITransact.run_sync(
            [sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'\\xff\\xfe')"]
        )
        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is True

    @patch("subprocess.run")
    def test_run_sync_generic_exception(self, mock_run: Any) -> None:
        """Test synchronous execution with generic exception."""
        mock_run.side_effect = Exception("Command not found")

        result = CLITransact.run_sync(["nonexistent-command"])
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Command execution failed" in result.stderr
        assert result.success is False

    @patch("subprocess.run")
    def test_run_sync_contains_nonstdlib_exception(self, mock_run: Any) -> None:
        """No exception escapes: even a non-stdlib type is contained as a result."""
        mock_run.side_effect = RuntimeError("kernel-level surprise")

        result = CLITransact.run_sync(["whatever"])
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "kernel-level surprise" in result.stderr
        assert result.success is False

    def test_run_sync_nonexistent_binary_is_contained(self) -> None:
        """A real (unmocked) missing binary raises FileNotFoundError in subprocess;
        it must be contained as a framework-error result, not escape as an exception.
        """
        result = CLITransact.run_sync(["definitely-not-a-real-binary-xyz"])
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Command execution failed" in result.stderr
        assert result.success is False


class TestCLITransactAsync:
    """Test cases for asynchronous command execution."""

    @pytest.mark.asyncio
    async def test_run_async_empty_command(self) -> None:
        """Test asynchronous execution with empty command."""
        result = await CLITransact.run_async("")
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Empty command provided" in result.stderr
        assert result.success is False

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_successful_command(self) -> None:
        """Test asynchronous execution of successful command."""
        result = await CLITransact.run_async(["echo", "hello"])
        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.stdout == "hello"
        assert result.stderr is None
        assert result.success is True

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_failing_command(self) -> None:
        """Test asynchronous execution of failing command."""
        result = await CLITransact.run_async(["false"])
        assert result.return_code != SUCCESS_RETURN_CODE
        assert result.success is False

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_with_stderr(self) -> None:
        """Test asynchronous execution with stderr output."""
        result = await CLITransact.run_async(["sh", "-c", "echo 'error' >&2; echo 'output'"])
        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.stdout == "output"
        assert result.stderr == "error"
        assert result.success is True

    @pytest.mark.asyncio
    async def test_run_async_with_marker_present(self) -> None:
        """Test asynchronous execution with success marker validation (present)."""
        result = await CLITransact.run_async(
            ["echo", "Operation SUCCESS completed"], success_marker="SUCCESS"
        )
        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is True

    @pytest.mark.asyncio
    async def test_run_async_with_marker_missing(self) -> None:
        """Test asynchronous execution with success marker validation (missing)."""
        result = await CLITransact.run_async(
            ["echo", "Operation completed"], success_marker="SUCCESS"
        )
        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is False

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_timeout(self) -> None:
        """Test asynchronous execution with timeout."""
        result = await CLITransact.run_async(["sleep", "2"], timeout=1)
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Timeout after 1 seconds" in result.stderr
        assert result.success is False

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_invalid_utf8_stdout_does_not_raise(self) -> None:
        """Invalid byte sequences in stdout must not turn a successful run into a failure."""
        result = await CLITransact.run_async(
            [sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'\\xff\\xfe')"]
        )
        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is True

    @pytest.mark.asyncio
    @patch("asyncio.create_subprocess_exec")
    async def test_run_async_timeout_grace_period_scales_down(
        self, mock_create_subprocess: Any
    ) -> None:
        """A short timeout must not incur the full fixed grace-period overhead."""
        mock_proc = MagicMock()
        wait_timeouts: list[float | None] = []
        orig_wait_for = asyncio.wait_for

        async def mock_communicate() -> None:
            raise asyncio.TimeoutError()

        async def mock_wait() -> None:
            return None

        mock_proc.communicate = mock_communicate
        mock_proc.wait = mock_wait
        mock_proc.kill = MagicMock()
        mock_proc.terminate = MagicMock()
        mock_create_subprocess.return_value = mock_proc

        async def spy_wait_for(aw: Any, timeout: float | None) -> Any:
            wait_timeouts.append(timeout)
            return await orig_wait_for(aw, timeout)

        with patch("asyncio.wait_for", side_effect=spy_wait_for):
            # A sub-1-second timeout is required to observe the grace-period cap
            # kick in; the public `timeout: int | None` annotation doesn't forbid
            # this at runtime (asyncio.wait_for accepts any real number).
            result = await CLITransact.run_async(["sleep", "10"], timeout=0.2)  # type: ignore[arg-type]

        # First recorded call is the outer communicate() wait (timeout=0.2); the
        # second is the post-terminate grace wait, which must be capped at the
        # caller's own timeout rather than the fixed 1.0s default.
        assert wait_timeouts[1] == 0.2
        assert result.return_code == ERROR_RETURN_CODE
        assert result.success is False

    @pytest.mark.asyncio
    @patch("asyncio.create_subprocess_exec")
    async def test_run_async_exception_handling(self, mock_create_subprocess: Any) -> None:
        """Test asynchronous execution exception handling."""
        mock_create_subprocess.side_effect = Exception("Process creation failed")

        result = await CLITransact.run_async(["nonexistent-command"])
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Command execution failed" in result.stderr
        assert result.success is False

    @pytest.mark.asyncio
    @patch("asyncio.create_subprocess_exec")
    async def test_run_async_timeout_graceful_cleanup(self, mock_create_subprocess: Any) -> None:
        """On timeout, the graceful signal (SIGTERM/terminate) is sent first.

        When the process exits promptly after terminate(), the forceful kill()
        escalation must NOT fire.
        """
        mock_proc = MagicMock()

        async def mock_communicate() -> None:
            raise asyncio.TimeoutError()

        async def mock_wait() -> None:
            return None  # process exits promptly after terminate()

        mock_proc.communicate = mock_communicate
        mock_proc.wait = mock_wait
        mock_proc.kill = MagicMock()
        mock_proc.terminate = MagicMock()
        mock_create_subprocess.return_value = mock_proc

        result = await CLITransact.run_async(["sleep", "10"], timeout=1)

        # Graceful first, no escalation needed.
        mock_proc.terminate.assert_called()
        mock_proc.kill.assert_not_called()
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Timeout after 1 seconds" in result.stderr
        assert result.success is False

    @pytest.mark.asyncio
    @patch("asyncio.create_subprocess_exec")
    async def test_run_async_timeout_escalates_to_kill(self, mock_create_subprocess: Any) -> None:
        """A process that ignores SIGTERM must be escalated to SIGKILL (kill())."""
        mock_proc = MagicMock()
        wait_calls = 0

        async def mock_communicate() -> None:
            raise asyncio.TimeoutError()

        # First wait() (after terminate) outlasts the grace window so wait_for times
        # out and forces escalation to kill(); the second wait() (after kill) returns.
        async def mock_wait() -> None:
            nonlocal wait_calls
            wait_calls += 1
            if wait_calls == 1:
                await asyncio.sleep(5)
            return None

        mock_proc.communicate = mock_communicate
        mock_proc.wait = mock_wait
        mock_proc.kill = MagicMock()
        mock_proc.terminate = MagicMock()
        mock_create_subprocess.return_value = mock_proc

        result = await CLITransact.run_async(["sleep", "10"], timeout=1)

        mock_proc.terminate.assert_called()
        mock_proc.kill.assert_called()
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Timeout after 1 seconds" in result.stderr
        assert result.success is False

    @pytest.mark.asyncio
    async def test_run_async_nonexistent_binary_is_contained(self) -> None:
        """A real (unmocked) missing binary raises FileNotFoundError from
        create_subprocess_exec; it must be contained as a framework-error result.
        """
        result = await CLITransact.run_async(["definitely-not-a-real-binary-xyz"])
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Command execution failed" in result.stderr
        assert result.success is False


class TestCLITransactSyncWithModel:
    """Test cases for synchronous command execution with model serialization."""

    def test_run_sync_with_model_empty_command(self) -> None:
        """Test sync with model execution with empty command."""
        result = CLITransact.run_sync_with_model("", parse_echo_output)
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Empty command provided" in result.stderr
        assert result.success is False
        assert result.model is None

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_run_sync_with_model_successful_command(self) -> None:
        """Test sync with model execution of successful command."""
        result = CLITransact.run_sync_with_model(["echo", "hello world"], parse_echo_output)

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.stdout == "hello world"
        assert result.stderr is None
        assert result.success is True
        assert result.model is not None
        assert result.model.value == "hello world"
        assert result.model.count == 1

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_run_sync_with_model_failing_command(self) -> None:
        """Test sync with model execution of failing command."""
        result = CLITransact.run_sync_with_model(["false"], parse_echo_output)

        assert result.return_code != SUCCESS_RETURN_CODE
        assert result.success is False
        assert result.model is None  # Model should not be parsed on command failure

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_run_sync_with_model_serialization_failure(self) -> None:
        """Test sync with model when serialization fails."""
        result = CLITransact.run_sync_with_model(["echo", "hello"], parse_failing_serializer)

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.stdout == "hello"
        assert result.success is True  # Command succeeded
        assert result.model is None  # Model parsing failed
        assert result.stderr is not None and "Model parsing failed" in result.stderr
        assert "Serialization failed" in result.stderr

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_run_sync_with_model_nonstdlib_serializer_failure(self) -> None:
        """A parser raising a non-stdlib type is contained, success unchanged."""
        result = CLITransact.run_sync_with_model(
            ["echo", "hello"], parse_nonstdlib_failing_serializer
        )

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is True  # parsing is advisory, never changes success
        assert result.model is None
        assert result.stderr is not None and "Model parsing failed" in result.stderr
        assert "Unexpected serializer failure" in result.stderr

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_run_sync_with_model_multiline_output(self) -> None:
        """Test sync with model with multiline output."""
        result = CLITransact.run_sync_with_model(
            ["sh", "-c", "echo 'line1'; echo 'line2'; echo 'line3'"], parse_echo_output
        )

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is True
        assert result.model is not None
        assert result.model.value == "line1"  # First line
        assert result.model.count == 3  # Total lines

    def test_run_sync_with_model_no_output(self) -> None:
        """Test sync with model when command produces no output."""
        result = CLITransact.run_sync_with_model(["true"], parse_echo_output)

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is True
        assert result.model is None  # No output to parse

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_run_sync_with_model_marker_validation(self) -> None:
        """Test sync with model with success marker validation."""
        result = CLITransact.run_sync_with_model(
            ["echo", "Operation SUCCESS completed"], parse_echo_output, success_marker="SUCCESS"
        )

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is True
        assert result.model is not None
        assert result.model.value == "Operation SUCCESS completed"

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_run_sync_with_model_marker_missing(self) -> None:
        """Test sync with model when success marker is missing."""
        result = CLITransact.run_sync_with_model(
            ["echo", "Operation completed"], parse_echo_output, success_marker="SUCCESS"
        )

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is False  # Success marker not found
        assert result.model is None  # Model not parsed due to success=False

    @patch("subprocess.run")
    def test_run_sync_with_model_timeout(self, mock_run: Any) -> None:
        """Test sync with model timeout handling."""
        mock_timeout = subprocess.TimeoutExpired(cmd=["sleep", "10"], timeout=1)
        mock_timeout.stdout = b"partial output"
        mock_run.side_effect = mock_timeout

        result = CLITransact.run_sync_with_model(["sleep", "10"], parse_echo_output, timeout=1)

        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Timeout after 1 seconds" in result.stderr
        assert result.stdout == "partial output"
        assert result.success is False
        assert result.model is None


class TestCLITransactAsyncWithModel:
    """Test cases for asynchronous command execution with model serialization."""

    @pytest.mark.asyncio
    async def test_run_async_with_model_empty_command(self) -> None:
        """Test async with model execution with empty command."""
        result = await CLITransact.run_async_with_model("", parse_echo_output)
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Empty command provided" in result.stderr
        assert result.success is False
        assert result.model is None

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_with_model_successful_command(self) -> None:
        """Test async with model execution of successful command."""
        result = await CLITransact.run_async_with_model(["echo", "hello world"], parse_echo_output)

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.stdout == "hello world"
        assert result.stderr is None
        assert result.success is True
        assert result.model is not None
        assert result.model.value == "hello world"
        assert result.model.count == 1

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_with_model_failing_command(self) -> None:
        """Test async with model execution of failing command."""
        result = await CLITransact.run_async_with_model(["false"], parse_echo_output)

        assert result.return_code != SUCCESS_RETURN_CODE
        assert result.success is False
        assert result.model is None  # Model should not be parsed on command failure

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_with_model_serialization_failure(self) -> None:
        """Test async with model when serialization fails."""
        result = await CLITransact.run_async_with_model(["echo", "hello"], parse_failing_serializer)

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.stdout == "hello"
        assert result.success is True  # Command succeeded
        assert result.model is None  # Model parsing failed
        assert result.stderr is not None and "Model parsing failed" in result.stderr
        assert "Serialization failed" in result.stderr

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_with_model_multiline_output(self) -> None:
        """Test async with model with multiline output."""
        result = await CLITransact.run_async_with_model(
            ["sh", "-c", "echo 'line1'; echo 'line2'; echo 'line3'"], parse_echo_output
        )

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is True
        assert result.model is not None
        assert result.model.value == "line1"  # First line
        assert result.model.count == 3  # Total lines

    @pytest.mark.asyncio
    async def test_run_async_with_model_no_output(self) -> None:
        """Test async with model when command produces no output."""
        result = await CLITransact.run_async_with_model(["true"], parse_echo_output)

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is True
        assert result.model is None  # No output to parse

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_with_model_marker_validation(self) -> None:
        """Test async with model with success marker validation."""
        result = await CLITransact.run_async_with_model(
            ["echo", "Operation SUCCESS completed"], parse_echo_output, success_marker="SUCCESS"
        )

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is True
        assert result.model is not None
        assert result.model.value == "Operation SUCCESS completed"

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_with_model_marker_missing(self) -> None:
        """Test async with model when success marker is missing."""
        result = await CLITransact.run_async_with_model(
            ["echo", "Operation completed"], parse_echo_output, success_marker="SUCCESS"
        )

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is False  # Success marker not found
        assert result.model is None  # Model not parsed due to success=False

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_with_model_timeout(self) -> None:
        """Test async with model timeout handling."""
        result = await CLITransact.run_async_with_model(
            ["sleep", "2"], parse_echo_output, timeout=1
        )

        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Timeout after 1 seconds" in result.stderr
        assert result.success is False
        assert result.model is None

    @pytest.mark.asyncio
    @patch("asyncio.create_subprocess_exec")
    async def test_run_async_with_model_exception_handling(
        self, mock_create_subprocess: Any
    ) -> None:
        """Test async with model exception handling."""
        mock_create_subprocess.side_effect = Exception("Process creation failed")

        result = await CLITransact.run_async_with_model(["nonexistent-command"], parse_echo_output)

        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Command execution failed" in result.stderr
        assert result.success is False
        assert result.model is None


class TestCLITransactModelIntegration:
    """Integration tests for CLI transaction with model serialization."""

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_sync_vs_async_with_model_consistency(self) -> None:
        """Test that sync and async model methods produce consistent results."""
        sync_result = CLITransact.run_sync_with_model(["echo", "test"], parse_echo_output)

        async def async_test() -> CLITransactResultModel[MockDataModel]:
            return await CLITransact.run_async_with_model(["echo", "test"], parse_echo_output)

        async_result = asyncio.run(async_test())

        # Compare base properties
        assert sync_result.return_code == async_result.return_code
        assert sync_result.stdout == async_result.stdout
        assert sync_result.success == async_result.success

        # Compare models
        assert sync_result.model == async_result.model
        if sync_result.model and async_result.model:
            assert sync_result.model.value == async_result.model.value
            assert sync_result.model.count == async_result.model.count

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_model_serialization_roundtrip(self) -> None:
        """Test that models can be serialized and deserialized correctly."""
        result = CLITransact.run_sync_with_model(["echo", "test data"], parse_echo_output)

        assert result.success is True
        assert result.model is not None

        # Serialize to dict
        model_dict = result.model.to_dict()
        assert model_dict == {"value": "test data", "count": 1}

        # Deserialize from dict
        reconstructed_model = MockDataModel.from_dict(model_dict)
        assert reconstructed_model == result.model

    def test_model_inheritance_from_datamodelhelper(self) -> None:
        """Test that MockDataModel properly inherits from DataModelHelper."""
        model = MockDataModel("test", 5)
        assert isinstance(model, DataModelHelper)

        # Test abstract methods are implemented
        model_dict = model.to_dict()
        assert model_dict == {"value": "test", "count": 5}

        reconstructed = MockDataModel.from_dict(model_dict)
        assert reconstructed.value == "test"
        assert reconstructed.count == 5


class TestCLITransactIntegration:
    """Integration tests for CLITransact."""

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_sync_vs_async_consistency(self) -> None:
        """Test that sync and async methods produce consistent results."""
        sync_result = CLITransact.run_sync(["echo", "test"])

        async def async_test() -> CLITransactResult:
            return await CLITransact.run_async(["echo", "test"])

        async_result = asyncio.run(async_test())

        assert sync_result.return_code == async_result.return_code
        assert sync_result.stdout == async_result.stdout
        assert sync_result.success == async_result.success

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_shell_vs_list_command_execution(self) -> None:
        """Test shell vs list command execution differences."""
        # Test with shell string
        shell_result = CLITransact.run_sync("echo 'hello world'")

        # Test with command list
        list_result = CLITransact.run_sync(["echo", "hello world"])

        assert shell_result.return_code == SUCCESS_RETURN_CODE
        assert list_result.return_code == SUCCESS_RETURN_CODE
        assert shell_result.stdout == list_result.stdout
        assert shell_result.success == list_result.success

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_large_output_handling(self) -> None:
        """Test handling of large command output."""
        # Generate large output
        large_text = "x" * 10000
        result = CLITransact.run_sync(["echo", large_text])

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.stdout == large_text
        assert result.success is True

    def test_unicode_output_handling(self) -> None:
        """Test handling of unicode characters in output."""
        # Test unicode output
        unicode_text = "Hello 世界 🌍"
        result = CLITransact.run_sync(["echo", unicode_text])

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.stdout == unicode_text
        assert result.success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
