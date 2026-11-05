"""Verify synchronous child ownership and cleanup with real processes."""

import os
import shlex
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

from foundation_tools.cli_transaction import CLIProcess, CLIProcessStartResult


def _start(command: str | list[str]) -> CLIProcess:
    """Start a test process and require a valid owner."""
    started = CLIProcess.start(command)
    assert started.success, started.error
    assert started.process is not None
    assert started.error is None
    return started.process


def test_poll_wait_timeout_and_idempotent_stop() -> None:
    process = _start([sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        assert process.pid > 0
        assert process.poll() is None
        assert process.wait(timeout=0.01) is None
        assert process.poll() is None
        result = process.stop(graceful_timeout=0.5)
        assert process.poll() is not None
        assert result.return_code == process.poll()
        assert process.stop() is result
        assert process.wait() is result
    finally:
        process.stop(0)


@pytest.mark.parametrize("exit_code", [0, 7])
def test_natural_exit_preserves_status(exit_code: int) -> None:
    with _start([sys.executable, "-c", f"raise SystemExit({exit_code})"]) as process:
        result = process.wait(timeout=5)
        assert result is not None
        assert result.return_code == exit_code
        assert result.success is (exit_code == 0)
        assert result.stdout is None
        assert result.stderr is None
        assert process.stop() is result


@pytest.mark.parametrize("command", [[], "", ["missing-cli-process-binary-xyz"]])
def test_launch_failure_is_contained(command: str | list[str]) -> None:
    result = CLIProcess.start(command)
    assert not result.success
    assert result.process is None
    assert result.error is not None
    assert result.error.return_code == -1
    assert not result.error.success
    assert result.error.stderr


@pytest.mark.parametrize("as_shell", [False, True])
def test_context_environment_files_and_default_stdin(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, as_shell: bool
) -> None:
    monkeypatch.setenv("CLI_PROCESS_PARENT", "parent")
    monkeypatch.setenv("CLI_PROCESS_VALUE", "old")
    script = (
        "import os, sys; print(os.getcwd()); print(os.environ['CLI_PROCESS_PARENT']); "
        "print(os.environ['CLI_PROCESS_VALUE']); print(repr(sys.stdin.read())); "
        "print('diagnostic', file=sys.stderr)"
    )
    argv = [sys.executable, "-c", script]
    command: str | list[str] = shlex.join(argv) if as_shell else argv
    env = {"CLI_PROCESS_VALUE": "new"}
    stdout_path, stderr_path = tmp_path / "stdout", tmp_path / "stderr"
    with stdout_path.open("w") as stdout, stderr_path.open("w") as stderr:
        started = CLIProcess.start(command, cwd=tmp_path, env=env, stdout=stdout, stderr=stderr)
        assert started.process is not None, started.error
        with started.process as process:
            result = process.wait(timeout=5)
            assert result is not None and result.success
            assert result.stdout is None and result.stderr is None
        assert not stdout.closed and not stderr.closed
    assert stdout_path.read_text().splitlines() == [str(tmp_path.resolve()), "parent", "new", "''"]
    assert stderr_path.read_text().strip() == "diagnostic"
    assert env == {"CLI_PROCESS_VALUE": "new"}
    assert os.environ["CLI_PROCESS_VALUE"] == "old"


def test_stdin_file_and_merged_output(tmp_path: Path) -> None:
    input_path, output_path = tmp_path / "input", tmp_path / "output"
    input_path.write_text("hello")
    with input_path.open("r") as stdin, output_path.open("w") as stdout:
        started = CLIProcess.start(
            [
                sys.executable,
                "-c",
                "import sys; print(sys.stdin.read()); print('err', file=sys.stderr)",
            ],
            stdin=stdin,
            stdout=stdout,
            stderr=subprocess.STDOUT,
        )
        assert started.process is not None, started.error
        with started.process as process:
            result = process.wait(5)
            assert result is not None and result.success
        assert not stdin.closed and not stdout.closed
    assert set(output_path.read_text().splitlines()) == {"hello", "err"}


@pytest.mark.parametrize("stream", ["stdin", "stdout", "stderr"])
def test_pipes_rejected_before_launch(stream: str, monkeypatch: pytest.MonkeyPatch) -> None:
    def unexpected_launch(*args: object, **kwargs: object) -> None:
        pytest.fail("PIPE must be rejected before launch")

    monkeypatch.setattr(subprocess, "Popen", unexpected_launch)
    result = CLIProcess.start(
        [sys.executable, "-c", "pass"],
        stdin=subprocess.PIPE if stream == "stdin" else subprocess.DEVNULL,
        stdout=subprocess.PIPE if stream == "stdout" else subprocess.DEVNULL,
        stderr=subprocess.PIPE if stream == "stderr" else subprocess.DEVNULL,
    )
    assert not result.success
    assert result.error is not None and "PIPE" in (result.error.stderr or "")


def test_context_exit_cleans_up_and_preserves_body_exception() -> None:
    process = _start([sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        with pytest.raises(RuntimeError, match="body failure"):
            with process:
                raise RuntimeError("body failure")
        assert process.poll() is not None
    finally:
        process.stop(0)


@pytest.mark.skipif(os.name != "posix", reason="POSIX signal handling")
def test_stop_escalates_when_sigterm_is_ignored(tmp_path: Path) -> None:
    ready = tmp_path / "ready"
    script = (
        "import pathlib, signal, sys, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); "
        "pathlib.Path(sys.argv[1]).write_text('ready'); time.sleep(30)"
    )
    process = _start([sys.executable, "-c", script, str(ready)])
    try:
        deadline = time.monotonic() + 5
        while not ready.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        assert ready.exists()
        result = process.stop(0.05)
        assert result.return_code == -signal.SIGKILL
        assert not result.success
        with pytest.raises(ProcessLookupError):
            os.kill(process.pid, 0)
    finally:
        process.stop(0)


@pytest.mark.parametrize("timeout", [-1.0, float("inf"), float("nan")])
def test_invalid_timeouts_leave_process_running(timeout: float) -> None:
    with _start([sys.executable, "-c", "import time; time.sleep(30)"]) as process:
        result = process.wait(timeout)
        assert result is not None and not result.success
        result = process.stop(timeout)
        assert not result.success
        assert process.poll() is None


def test_explicit_shell_override(tmp_path: Path) -> None:
    output = tmp_path / "output"
    with output.open("w") as stdout:
        started = CLIProcess.start('printf "%s" "$0"', shell=["bash", "-c"], stdout=stdout)
        assert started.process is not None
        with started.process as process:
            result = process.wait(5)
            assert result is not None and result.success
    assert output.read_text() == "bash"


def test_invalid_start_result_is_rejected() -> None:
    with pytest.raises(ValueError):
        CLIProcessStartResult()


@pytest.mark.skipif(os.name != "posix", reason="POSIX signal handling")
def test_stop_allows_graceful_exit_before_kill(tmp_path: Path) -> None:
    ready = tmp_path / "ready"
    script = (
        "import pathlib, signal, sys, time; "
        "signal.signal(signal.SIGTERM, lambda *_: sys.exit(0)); "
        "pathlib.Path(sys.argv[1]).write_text('ready'); time.sleep(30)"
    )
    process = _start([sys.executable, "-c", script, str(ready)])
    try:
        deadline = time.monotonic() + 5
        while not ready.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        assert ready.exists()
        result = process.stop(1)
        assert result.success
        assert result.return_code == 0
        with pytest.raises(ProcessLookupError):
            os.kill(process.pid, 0)
    finally:
        process.stop(0)


def test_exit_between_poll_and_signal_is_not_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    from unittest.mock import MagicMock

    child = MagicMock(pid=1234)
    child.poll.return_value = None
    child.terminate.side_effect = ProcessLookupError()
    child.wait.return_value = 0
    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: child)
    process = _start(["test-command"])
    result = process.stop(0)
    assert result.success
    assert result.return_code == 0


def test_logging_masks_launch_and_cleanup_errors_after_caller_env_change(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import json
    from io import StringIO
    from logging import DEBUG, StreamHandler

    import foundation_tools.cli_transaction.cli_process as process_module
    from foundation_tools.standardized_logger import StandardizedLogger

    stream = StringIO()
    logger = StandardizedLogger(name="process-test", level=DEBUG, log_dir=tmp_path)
    handler = logger.handlers[0]
    assert isinstance(handler, StreamHandler)
    handler.setStream(stream)
    monkeypatch.setattr(process_module, "_log", logger)
    secret = "process-secret.*[value]"
    env = {"TOKEN": secret}
    started = CLIProcess.start(
        [sys.executable, "-c", "import time; time.sleep(30)", secret], env=env
    )
    assert started.process is not None, started.error
    process = started.process
    env["TOKEN"] = "changed-by-caller"

    def denied() -> None:
        raise PermissionError(secret)

    try:
        with monkeypatch.context() as scoped:
            scoped.setattr(process._process, "terminate", denied)
            error = process.stop(0)
            assert not error.success
            assert error.stderr is not None and secret in error.stderr
            assert process.poll() is None
        result = process.stop(0)
        assert process.poll() is not None
        assert process.wait() is result
    finally:
        process.stop(0)
        for logger_handler in logger.handlers:
            logger_handler.close()
    for text in (stream.getvalue(), next(tmp_path.glob("*.log")).read_text()):
        assert secret not in text
        assert "[REDACTED]" in text
        records = [json.loads(line) for line in text.splitlines()]
        assert records[0]["level"] == "INFO"
        assert records[0]["argv"][-1] == "[REDACTED]"
        assert any(record["level"] == "DEBUG" for record in records)
        assert any(record["level"] == "ERROR" for record in records)
        assert all("env" not in record and "input" not in record for record in records)


def test_missing_working_directory_is_a_launch_error(tmp_path: Path) -> None:
    started = CLIProcess.start([sys.executable, "-c", "pass"], cwd=tmp_path / "missing")
    assert not started.success
    assert started.process is None
    assert started.error is not None and started.error.return_code == -1
