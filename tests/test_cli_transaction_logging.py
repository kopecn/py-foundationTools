"""Verify command logging levels and environment-value redaction."""

import json
import subprocess
import sys
from io import StringIO
from logging import DEBUG, INFO, StreamHandler
from pathlib import Path
from unittest.mock import patch

import pytest

import foundation_tools.cli_transaction.cliTransact as cli_module
from foundation_tools.cli_transaction import CLITransact
from foundation_tools.standardized_logger import StandardizedLogger


@pytest.mark.asyncio
@pytest.mark.parametrize("as_async", [False, True])
@pytest.mark.parametrize("as_shell", [False, True])
@pytest.mark.parametrize("level", [INFO, DEBUG])
async def test_command_and_output_logs_mask_environment_values(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, as_async: bool, as_shell: bool, level: int
) -> None:
    """Console and file logs mask env values while execution and results stay intact."""
    import shlex

    stream = StringIO()
    logger = StandardizedLogger(name="cli-test", level=level, log_dir=tmp_path)
    console_handler = logger.handlers[0]
    assert isinstance(console_handler, StreamHandler)
    console_handler.setStream(stream)
    monkeypatch.setattr(cli_module, "_log", logger)
    secret = "test-secret-long.*[token]"
    script = (
        "import os, sys; print(sys.argv[1]); "
        "print(os.environ['TOKEN'], file=sys.stderr); sys.stdin.read()"
    )
    argv = [sys.executable, "-c", script, secret]
    command: str | list[str] = shlex.join(argv) if as_shell else argv
    try:
        if as_async:
            result = await CLITransact.run_async(
                command,
                env={"TOKEN": secret, "OVERLAP": "test-secret", "EMPTY": ""},
                input="private-stdin-text",
            )
        else:
            result = CLITransact.run_sync(
                command,
                env={"TOKEN": secret, "OVERLAP": "test-secret", "EMPTY": ""},
                input="private-stdin-text",
            )
    finally:
        for handler in logger.handlers:
            handler.close()
    assert result.success
    assert result.stdout == secret
    assert result.stderr == secret
    console = stream.getvalue()
    file_text = next(tmp_path.glob("*.log")).read_text()
    for text in (console, file_text):
        assert secret not in text
        assert "test-secret" not in text
        assert "private-stdin-text" not in text
        records = [json.loads(line) for line in text.splitlines()]
        assert records[0]["level"] == "INFO"
        expected_argv = [
            part.replace(secret, "[REDACTED]")
            for part in (shlex.split(command) if isinstance(command, str) else command)
        ]
        if isinstance(command, str):
            expected_argv = ["bash", "-c", command.replace(secret, "[REDACTED]")]
        assert records[0]["argv"] == expected_argv
        assert all("env" not in record and "input" not in record for record in records)
        if level == DEBUG:
            assert len(records) == 2
            assert records[1]["level"] == "DEBUG"
            assert records[1]["stdout"] == "[REDACTED]\n"
            assert records[1]["stderr"] == "[REDACTED]\n"
        else:
            assert len(records) == 1


def test_command_is_logged_before_subprocess_starts(monkeypatch: pytest.MonkeyPatch) -> None:
    """The INFO event precedes the actual command issuance."""
    from unittest.mock import MagicMock

    logger = MagicMock()
    monkeypatch.setattr(cli_module, "_log", logger)

    def execute(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        logger.info.assert_called_once_with("CLI command issued", argv=["test-command"])
        return subprocess.CompletedProcess(["test-command"], 0, "", "")

    with patch("subprocess.run", side_effect=execute):
        assert CLITransact.run_sync(["test-command"]).success


@pytest.mark.asyncio
@pytest.mark.parametrize("as_async", [False, True])
async def test_launch_failure_is_logged_with_redaction(
    monkeypatch: pytest.MonkeyPatch, as_async: bool
) -> None:
    """A launch exception is logged at DEBUG without exposing its env value."""
    from unittest.mock import MagicMock

    logger = MagicMock()
    monkeypatch.setattr(cli_module, "_log", logger)
    command = ["missing-secret-binary"]
    if as_async:
        result = await CLITransact.run_async(command, env={"TOKEN": "secret"})
    else:
        result = CLITransact.run_sync(command, env={"TOKEN": "secret"})
    assert not result.success
    assert result.stderr is not None and "secret" in result.stderr
    assert "secret" not in str(logger.info.call_args)
    assert "secret" not in str(logger.debug.call_args)
