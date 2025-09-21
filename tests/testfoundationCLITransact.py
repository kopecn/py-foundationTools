"""
Unit tests for CLITransact module.

Comprehensive test suite covering synchronous and asynchronous command execution,
timeout handling, success validation, and error scenarios.
"""

import asyncio
import os
import subprocess
import sys
from typing import Any
from unittest.mock import patch, MagicMock

import pytest

# Add src to path for import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from foundationCLIHelpers.cliTransact import (  # type: ignore # pylint: disable=wrong-import-position
    CLITransact,
    CLITransactResult,
    CLITransactResultWithModel,
    ERROR_RETURN_CODE,
    SUCCESS_RETURN_CODE,
)
from foundationDataModelHelpers.dataModelHelper import DataModelHelper  # type: ignore # pylint: disable=wrong-import-position


# Test data model for unit tests
class MockDataModel(DataModelHelper):
    """Simple test data model for testing serialization."""

    def __init__(self, value: str, count: int):
        self.value = value
        self.count = count

    @staticmethod
    def from_dict(obj: Any) -> "MockDataModel":
        return MockDataModel(obj["value"], obj["count"])

    def to_dict(self) -> dict:
        return {"value": self.value, "count": self.count}

    def __eq__(self, other):
        return isinstance(other, MockDataModel) and self.value == other.value and self.count == other.count


def parse_echo_output(output: str) -> MockDataModel:
    """Test serializer that parses echo output into MockDataModel."""
    lines = output.strip().split('\n')
    return MockDataModel(value=lines[0], count=len(lines))


def parse_failing_serializer(output: str) -> MockDataModel:
    """Test serializer that always fails."""
    raise ValueError("Serialization failed")


class TestCLITransactResult:
    """Test cases for CLITransactResult data class."""

    def test_default_initialization(self):
        """Test default CLITransactResult initialization."""
        result = CLITransactResult(return_code=0)
        assert result.return_code == 0
        assert result.stdout is None
        assert result.stderr is None
        assert result.success is False

    def test_full_initialization(self):
        """Test CLITransactResult with all fields."""
        result = CLITransactResult(
            return_code=0, stdout="Hello World", stderr="Warning message", success=True
        )
        assert result.return_code == 0
        assert result.stdout == "Hello World"
        assert result.stderr == "Warning message"
        assert result.success is True


class TestCLITransactResultWithModel:
    """Test cases for CLITransactResultWithModel data class."""

    def test_default_initialization(self):
        """Test default CLITransactResultWithModel initialization."""
        result = CLITransactResultWithModel[MockDataModel](return_code=0)
        assert result.return_code == 0
        assert result.stdout is None
        assert result.stderr is None
        assert result.success is False
        assert result.model is None

    def test_full_initialization_with_model(self):
        """Test CLITransactResultWithModel with all fields including model."""
        test_model = MockDataModel("test", 42)
        result = CLITransactResultWithModel[MockDataModel](
            return_code=0,
            stdout="Hello World",
            stderr="Warning message",
            success=True,
            model=test_model
        )
        assert result.return_code == 0
        assert result.stdout == "Hello World"
        assert result.stderr == "Warning message"
        assert result.success is True
        assert result.model == test_model
        assert result.model.value == "test"
        assert result.model.count == 42


class TestCLITransact:
    """Test cases for CLITransact class."""

    def test_initialization_default(self):
        """Test CLITransact initialization with defaults."""
        cli = CLITransact()
        assert cli.success_string is None

    def test_initialization_with_success_string(self):
        """Test CLITransact initialization with success string."""
        cli = CLITransact(success_string="SUCCESS")
        assert cli.success_string == "SUCCESS"

    def test_validate_command_empty_string(self):
        """Test command validation with empty string."""
        cli = CLITransact()
        result = cli._validate_command("")  # type: ignore[attr-defined] # pylint: disable=protected-access
        assert result is not None
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Empty command provided" in result.stderr

    def test_validate_command_empty_list(self):
        """Test command validation with empty list."""
        cli = CLITransact()
        result = cli._validate_command([])  # type: ignore[attr-defined] # pylint: disable=protected-access
        assert result is not None
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Empty command provided" in result.stderr

    def test_validate_command_valid(self):
        """Test command validation with valid command."""
        cli = CLITransact()
        result = cli._validate_command("echo hello")  # type: ignore[attr-defined] # pylint: disable=protected-access
        assert result is None

    def test_determine_success_with_return_code_zero(self):
        """Test success determination with return code 0."""
        cli = CLITransact()
        assert cli._determine_success(SUCCESS_RETURN_CODE, "output") is True  # type: ignore[attr-defined] # pylint: disable=protected-access

    def test_determine_success_with_return_code_nonzero(self):
        """Test success determination with non-zero return code."""
        cli = CLITransact()
        assert cli._determine_success(1, "output") is False  # type: ignore[attr-defined] # pylint: disable=protected-access

    def test_determine_success_with_success_string_present(self):
        """Test success determination with success string present."""
        cli = CLITransact(success_string="SUCCESS")
        assert (
            cli._determine_success(SUCCESS_RETURN_CODE, "Operation SUCCESS completed")  # type: ignore[attr-defined] # pylint: disable=protected-access
            is True
        )

    def test_determine_success_with_success_string_missing(self):
        """Test success determination with success string missing."""
        cli = CLITransact(success_string="SUCCESS")
        assert (
            cli._determine_success(SUCCESS_RETURN_CODE, "Operation completed") is False  # type: ignore[attr-defined] # pylint: disable=protected-access
        )

    def test_normalize_output_none(self):
        """Test output normalization with None input."""
        cli = CLITransact()
        assert cli._normalize_output(None) is None  # type: ignore[attr-defined] # pylint: disable=protected-access

    def test_normalize_output_empty_string(self):
        """Test output normalization with empty string."""
        cli = CLITransact()
        assert cli._normalize_output("") is None  # type: ignore[attr-defined] # pylint: disable=protected-access

    def test_normalize_output_whitespace_only(self):
        """Test output normalization with whitespace only."""
        cli = CLITransact()
        assert cli._normalize_output("   \n\t  ") is None  # type: ignore[attr-defined] # pylint: disable=protected-access

    def test_normalize_output_with_content(self):
        """Test output normalization with actual content."""
        cli = CLITransact()
        assert cli._normalize_output("  hello world  \n") == "hello world"  # type: ignore[attr-defined] # pylint: disable=protected-access


class TestCLITransactSync:
    """Test cases for synchronous command execution."""

    def test_run_sync_empty_command(self):
        """Test synchronous execution with empty command."""
        cli = CLITransact()
        result = cli.run_sync("")
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Empty command provided" in result.stderr
        assert result.success is False

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_run_sync_successful_command(self):
        """Test synchronous execution of successful command."""
        cli = CLITransact()
        result = cli.run_sync(["echo", "hello"])
        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.stdout == "hello"
        assert result.stderr is None
        assert result.success is True

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_run_sync_failing_command(self):
        """Test synchronous execution of failing command."""
        cli = CLITransact()
        result = cli.run_sync(["false"])
        assert result.return_code != SUCCESS_RETURN_CODE
        assert result.success is False

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_run_sync_with_stderr(self):
        """Test synchronous execution with stderr output."""
        cli = CLITransact()
        result = cli.run_sync(["sh", "-c", "echo 'error' >&2; echo 'output'"])
        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.stdout == "output"
        assert result.stderr == "error"
        assert result.success is True

    def test_run_sync_with_success_string_present(self):
        """Test synchronous execution with success string validation (present)."""
        cli = CLITransact(success_string="SUCCESS")
        result = cli.run_sync(["echo", "Operation SUCCESS completed"])
        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is True

    def test_run_sync_with_success_string_missing(self):
        """Test synchronous execution with success string validation (missing)."""
        cli = CLITransact(success_string="SUCCESS")
        result = cli.run_sync(["echo", "Operation completed"])
        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is False

    @patch("subprocess.run")
    def test_run_sync_timeout_exception(self, mock_run: Any):
        """Test synchronous execution timeout handling."""
        mock_timeout = subprocess.TimeoutExpired(cmd=["sleep", "10"], timeout=1)
        mock_timeout.stdout = b"partial output"
        mock_run.side_effect = mock_timeout

        cli = CLITransact()
        result = cli.run_sync(["sleep", "10"], timeout=1)
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Timeout after 1 seconds" in result.stderr
        assert result.stdout == "partial output"
        assert result.success is False

    @patch("subprocess.run")
    def test_run_sync_generic_exception(self, mock_run: Any):
        """Test synchronous execution with generic exception."""
        mock_run.side_effect = Exception("Command not found")

        cli = CLITransact()
        result = cli.run_sync(["nonexistent-command"])
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Command execution failed" in result.stderr
        assert result.success is False


class TestCLITransactAsync:
    """Test cases for asynchronous command execution."""

    @pytest.mark.asyncio
    async def test_run_async_empty_command(self):
        """Test asynchronous execution with empty command."""
        cli = CLITransact()
        result = await cli.run_async("")
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Empty command provided" in result.stderr
        assert result.success is False

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_successful_command(self):
        """Test asynchronous execution of successful command."""
        cli = CLITransact()
        result = await cli.run_async(["echo", "hello"])
        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.stdout == "hello"
        assert result.stderr is None
        assert result.success is True

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_failing_command(self):
        """Test asynchronous execution of failing command."""
        cli = CLITransact()
        result = await cli.run_async(["false"])
        assert result.return_code != SUCCESS_RETURN_CODE
        assert result.success is False

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_with_stderr(self):
        """Test asynchronous execution with stderr output."""
        cli = CLITransact()
        result = await cli.run_async(["sh", "-c", "echo 'error' >&2; echo 'output'"])
        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.stdout == "output"
        assert result.stderr == "error"
        assert result.success is True

    @pytest.mark.asyncio
    async def test_run_async_with_success_string_present(self):
        """Test asynchronous execution with success string validation (present)."""
        cli = CLITransact(success_string="SUCCESS")
        result = await cli.run_async(["echo", "Operation SUCCESS completed"])
        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is True

    @pytest.mark.asyncio
    async def test_run_async_with_success_string_missing(self):
        """Test asynchronous execution with success string validation (missing)."""
        cli = CLITransact(success_string="SUCCESS")
        result = await cli.run_async(["echo", "Operation completed"])
        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is False

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_timeout(self):
        """Test asynchronous execution with timeout."""
        cli = CLITransact()
        result = await cli.run_async(["sleep", "2"], timeout=1)
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Timeout after 1 seconds" in result.stderr
        assert result.success is False

    @pytest.mark.asyncio
    @patch("asyncio.create_subprocess_exec")
    async def test_run_async_exception_handling(self, mock_create_subprocess: Any):
        """Test asynchronous execution exception handling."""
        mock_create_subprocess.side_effect = Exception("Process creation failed")

        cli = CLITransact()
        result = await cli.run_async(["nonexistent-command"])
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Command execution failed" in result.stderr
        assert result.success is False

    @pytest.mark.asyncio
    @patch("asyncio.create_subprocess_exec")
    async def test_run_async_timeout_with_cleanup(self, mock_create_subprocess: Any):
        """Test asynchronous execution timeout with proper process cleanup."""
        mock_proc = MagicMock()

        # Create async mock functions
        async def mock_communicate():
            raise asyncio.TimeoutError()

        async def mock_wait():
            return None

        mock_proc.communicate = mock_communicate
        mock_proc.wait = mock_wait
        mock_proc.kill = MagicMock()
        mock_proc.terminate = MagicMock()
        mock_create_subprocess.return_value = mock_proc

        cli = CLITransact()
        result = await cli.run_async(["sleep", "10"], timeout=1)

        # Verify cleanup was called
        mock_proc.kill.assert_called()
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Timeout after 1 seconds" in result.stderr
        assert result.success is False


class TestCLITransactSyncWithModel:
    """Test cases for synchronous command execution with model serialization."""

    def test_run_sync_with_model_empty_command(self):
        """Test sync with model execution with empty command."""
        cli = CLITransact()
        result = cli.run_sync_with_model("", parse_echo_output)
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Empty command provided" in result.stderr
        assert result.success is False
        assert result.model is None

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_run_sync_with_model_successful_command(self):
        """Test sync with model execution of successful command."""
        cli = CLITransact()
        result = cli.run_sync_with_model(["echo", "hello world"], parse_echo_output)

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.stdout == "hello world"
        assert result.stderr is None
        assert result.success is True
        assert result.model is not None
        assert result.model.value == "hello world"
        assert result.model.count == 1

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_run_sync_with_model_failing_command(self):
        """Test sync with model execution of failing command."""
        cli = CLITransact()
        result = cli.run_sync_with_model(["false"], parse_echo_output)

        assert result.return_code != SUCCESS_RETURN_CODE
        assert result.success is False
        assert result.model is None  # Model should not be parsed on command failure

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_run_sync_with_model_serialization_failure(self):
        """Test sync with model when serialization fails."""
        cli = CLITransact()
        result = cli.run_sync_with_model(["echo", "hello"], parse_failing_serializer)

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.stdout == "hello"
        assert result.success is True  # Command succeeded
        assert result.model is None  # Model parsing failed
        assert result.stderr is not None and "Model parsing failed" in result.stderr
        assert "Serialization failed" in result.stderr

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_run_sync_with_model_multiline_output(self):
        """Test sync with model with multiline output."""
        cli = CLITransact()
        result = cli.run_sync_with_model(
            ["sh", "-c", "echo 'line1'; echo 'line2'; echo 'line3'"],
            parse_echo_output
        )

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is True
        assert result.model is not None
        assert result.model.value == "line1"  # First line
        assert result.model.count == 3  # Total lines

    def test_run_sync_with_model_no_output(self):
        """Test sync with model when command produces no output."""
        cli = CLITransact()
        result = cli.run_sync_with_model(["true"], parse_echo_output)

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is True
        assert result.model is None  # No output to parse

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_run_sync_with_model_success_string_validation(self):
        """Test sync with model with success string validation."""
        cli = CLITransact(success_string="SUCCESS")
        result = cli.run_sync_with_model(
            ["echo", "Operation SUCCESS completed"],
            parse_echo_output
        )

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is True
        assert result.model is not None
        assert result.model.value == "Operation SUCCESS completed"

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_run_sync_with_model_success_string_missing(self):
        """Test sync with model when success string is missing."""
        cli = CLITransact(success_string="SUCCESS")
        result = cli.run_sync_with_model(
            ["echo", "Operation completed"],
            parse_echo_output
        )

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is False  # Success string not found
        assert result.model is None  # Model not parsed due to success=False

    @patch("subprocess.run")
    def test_run_sync_with_model_timeout(self, mock_run: Any):
        """Test sync with model timeout handling."""
        mock_timeout = subprocess.TimeoutExpired(cmd=["sleep", "10"], timeout=1)
        mock_timeout.stdout = b"partial output"
        mock_run.side_effect = mock_timeout

        cli = CLITransact()
        result = cli.run_sync_with_model(["sleep", "10"], parse_echo_output, timeout=1)

        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Timeout after 1 seconds" in result.stderr
        assert result.stdout == "partial output"
        assert result.success is False
        assert result.model is None


class TestCLITransactAsyncWithModel:
    """Test cases for asynchronous command execution with model serialization."""

    @pytest.mark.asyncio
    async def test_run_async_with_model_empty_command(self):
        """Test async with model execution with empty command."""
        cli = CLITransact()
        result = await cli.run_async_with_model("", parse_echo_output)
        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Empty command provided" in result.stderr
        assert result.success is False
        assert result.model is None

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_with_model_successful_command(self):
        """Test async with model execution of successful command."""
        cli = CLITransact()
        result = await cli.run_async_with_model(["echo", "hello world"], parse_echo_output)

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.stdout == "hello world"
        assert result.stderr is None
        assert result.success is True
        assert result.model is not None
        assert result.model.value == "hello world"
        assert result.model.count == 1

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_with_model_failing_command(self):
        """Test async with model execution of failing command."""
        cli = CLITransact()
        result = await cli.run_async_with_model(["false"], parse_echo_output)

        assert result.return_code != SUCCESS_RETURN_CODE
        assert result.success is False
        assert result.model is None  # Model should not be parsed on command failure

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_with_model_serialization_failure(self):
        """Test async with model when serialization fails."""
        cli = CLITransact()
        result = await cli.run_async_with_model(["echo", "hello"], parse_failing_serializer)

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.stdout == "hello"
        assert result.success is True  # Command succeeded
        assert result.model is None  # Model parsing failed
        assert result.stderr is not None and "Model parsing failed" in result.stderr
        assert "Serialization failed" in result.stderr

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_with_model_multiline_output(self):
        """Test async with model with multiline output."""
        cli = CLITransact()
        result = await cli.run_async_with_model(
            ["sh", "-c", "echo 'line1'; echo 'line2'; echo 'line3'"],
            parse_echo_output
        )

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is True
        assert result.model is not None
        assert result.model.value == "line1"  # First line
        assert result.model.count == 3  # Total lines

    @pytest.mark.asyncio
    async def test_run_async_with_model_no_output(self):
        """Test async with model when command produces no output."""
        cli = CLITransact()
        result = await cli.run_async_with_model(["true"], parse_echo_output)

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is True
        assert result.model is None  # No output to parse

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_with_model_success_string_validation(self):
        """Test async with model with success string validation."""
        cli = CLITransact(success_string="SUCCESS")
        result = await cli.run_async_with_model(
            ["echo", "Operation SUCCESS completed"],
            parse_echo_output
        )

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is True
        assert result.model is not None
        assert result.model.value == "Operation SUCCESS completed"

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_with_model_success_string_missing(self):
        """Test async with model when success string is missing."""
        cli = CLITransact(success_string="SUCCESS")
        result = await cli.run_async_with_model(
            ["echo", "Operation completed"],
            parse_echo_output
        )

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.success is False  # Success string not found
        assert result.model is None  # Model not parsed due to success=False

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    async def test_run_async_with_model_timeout(self):
        """Test async with model timeout handling."""
        cli = CLITransact()
        result = await cli.run_async_with_model(["sleep", "2"], parse_echo_output, timeout=1)

        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Timeout after 1 seconds" in result.stderr
        assert result.success is False
        assert result.model is None

    @pytest.mark.asyncio
    @patch("asyncio.create_subprocess_exec")
    async def test_run_async_with_model_exception_handling(self, mock_create_subprocess: Any):
        """Test async with model exception handling."""
        mock_create_subprocess.side_effect = Exception("Process creation failed")

        cli = CLITransact()
        result = await cli.run_async_with_model(["nonexistent-command"], parse_echo_output)

        assert result.return_code == ERROR_RETURN_CODE
        assert result.stderr is not None and "Command execution failed" in result.stderr
        assert result.success is False
        assert result.model is None


class TestCLITransactModelIntegration:
    """Integration tests for CLI transaction with model serialization."""

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_sync_vs_async_with_model_consistency(self):
        """Test that sync and async model methods produce consistent results."""
        cli = CLITransact()

        # Test successful command with model
        sync_result = cli.run_sync_with_model(["echo", "test"], parse_echo_output)

        async def async_test():
            return await cli.run_async_with_model(["echo", "test"], parse_echo_output)

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
    def test_model_serialization_roundtrip(self):
        """Test that models can be serialized and deserialized correctly."""
        cli = CLITransact()
        result = cli.run_sync_with_model(["echo", "test data"], parse_echo_output)

        assert result.success is True
        assert result.model is not None

        # Serialize to dict
        model_dict = result.model.to_dict()
        assert model_dict == {"value": "test data", "count": 1}

        # Deserialize from dict
        reconstructed_model = MockDataModel.from_dict(model_dict)
        assert reconstructed_model == result.model

    def test_model_inheritance_from_datamodelhelper(self):
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
    def test_sync_vs_async_consistency(self):
        """Test that sync and async methods produce consistent results."""
        cli = CLITransact()

        # Test successful command
        sync_result = cli.run_sync(["echo", "test"])

        async def async_test():
            return await cli.run_async(["echo", "test"])

        async_result = asyncio.run(async_test())

        assert sync_result.return_code == async_result.return_code
        assert sync_result.stdout == async_result.stdout
        assert sync_result.success == async_result.success

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_shell_vs_list_command_execution(self):
        """Test shell vs list command execution differences."""
        cli = CLITransact()

        # Test with shell string
        shell_result = cli.run_sync("echo 'hello world'")

        # Test with command list
        list_result = cli.run_sync(["echo", "hello world"])

        assert shell_result.return_code == SUCCESS_RETURN_CODE
        assert list_result.return_code == SUCCESS_RETURN_CODE
        assert shell_result.stdout == list_result.stdout
        assert shell_result.success == list_result.success

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_large_output_handling(self):
        """Test handling of large command output."""
        cli = CLITransact()

        # Generate large output
        large_text = "x" * 10000
        result = cli.run_sync(["echo", large_text])

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.stdout == large_text
        assert result.success is True

    def test_unicode_output_handling(self):
        """Test handling of unicode characters in output."""
        cli = CLITransact()

        # Test unicode output
        unicode_text = "Hello 世界 🌍"
        result = cli.run_sync(["echo", unicode_text])

        assert result.return_code == SUCCESS_RETURN_CODE
        assert result.stdout == unicode_text
        assert result.success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
