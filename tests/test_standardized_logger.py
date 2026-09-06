"""Tests for foundation_tools.standardized_logger.

Covers the private external-rotation detection plus the public ``logging.Logger``
call contract and the safety of the structured (JSON) output on both the stderr
console handler and the date-rolling file handler.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from datetime import datetime, timezone
from logging import DEBUG, StreamHandler
from pathlib import Path

import pytest

from foundation_tools.standardized_logger import (
    StandardizedLogger,
    _DateRollingFileHandler,
)
from foundationTypes.standardizedLoggerConfig.StandardizedLoggerConfig import (
    LogLevel,
    StandardizedLoggerConfig,
)


def _open_handler(tmp_path: Path) -> _DateRollingFileHandler:
    """Build a handler writing into tmp_path, for a fixed logger name."""
    return _DateRollingFileHandler(log_dir=tmp_path, logger_name="rollovertest")


def _current_path(handler: _DateRollingFileHandler) -> Path:
    """Return the path the handler currently believes it has open."""
    assert handler._current_date is not None
    return handler._path_for_date(handler._current_date)


def test_no_change_does_not_report_rollover(tmp_path: Path) -> None:
    """An untouched, still-open file must not be flagged for rollover."""
    handler = _open_handler(tmp_path)
    try:
        assert handler._needs_inode_rollover() is False
    finally:
        handler.close()


def test_replaced_path_reports_rollover(tmp_path: Path) -> None:
    """If the configured path now points at a different (new) file, that's a rollover."""
    handler = _open_handler(tmp_path)
    try:
        path = _current_path(handler)
        path.unlink()
        path.write_text("new file, new inode\n", encoding="utf-8")

        assert handler._needs_inode_rollover() is True
    finally:
        handler.close()


def test_missing_path_reports_rollover(tmp_path: Path) -> None:
    """If the configured path has been removed outright, that's a rollover."""
    handler = _open_handler(tmp_path)
    try:
        path = _current_path(handler)
        path.unlink()

        assert handler._needs_inode_rollover() is True
    finally:
        handler.close()


# ---------------------------------------------------------------------------
# Public contract: helpers
# ---------------------------------------------------------------------------

LoggerFactory = Callable[..., StandardizedLogger]


@pytest.fixture
def make_logger(tmp_path: Path) -> Iterator[LoggerFactory]:
    """Yield a factory for StandardizedLoggers whose handlers are closed on teardown."""
    created: list[StandardizedLogger] = []

    def _make(name: str = "svc", **kwargs: object) -> StandardizedLogger:
        kwargs.setdefault("level", DEBUG)
        kwargs.setdefault("log_dir", tmp_path)
        log = StandardizedLogger(name, **kwargs)  # type: ignore[arg-type]
        created.append(log)
        return log

    yield _make

    for log in created:
        for handler in list(log.handlers):
            handler.close()


def _json_lines(text: str) -> list[dict[str, object]]:
    """Parse every JSON object line out of a captured stream."""
    out: list[dict[str, object]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("{"):
            out.append(json.loads(stripped))
    return out


def _console_entries(capsys: pytest.CaptureFixture[str]) -> list[dict[str, object]]:
    """Return the structured entries written to stderr so far."""
    return _json_lines(capsys.readouterr().err)


def _file_entries(log_dir: Path, name: str = "svc") -> list[dict[str, object]]:
    """Return the structured entries written to today's log file."""
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = Path(log_dir) / f"{name}_{stamp}.log"
    return _json_lines(path.read_text(encoding="utf-8"))


def _file_handler(log: StandardizedLogger) -> _DateRollingFileHandler:
    """Return the logger's date-rolling file handler."""
    return next(h for h in log.handlers if isinstance(h, _DateRollingFileHandler))


def _console_handler(log: StandardizedLogger) -> StreamHandler:  # type: ignore[type-arg]
    """Return the logger's stderr console handler."""
    return next(
        h
        for h in log.handlers
        if isinstance(h, StreamHandler) and not isinstance(h, _DateRollingFileHandler)
    )


# ---------------------------------------------------------------------------
# Standard logging keyword forwarding
# ---------------------------------------------------------------------------


def test_exc_info_forwarded_not_leaked_as_field(
    make_logger: LoggerFactory, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """``exc_info`` must produce an ``exception`` field, not a raw ``exc_info`` field."""
    log = make_logger()
    try:
        raise ValueError("boom")
    except ValueError:
        log.error("it failed", exc_info=True)

    for entry in (_console_entries(capsys)[-1], _file_entries(tmp_path)[-1]):
        assert "exc_info" not in entry
        assert isinstance(entry["exception"], str)
        assert "ValueError: boom" in entry["exception"]


def test_stack_info_forwarded_not_leaked_as_field(
    make_logger: LoggerFactory, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """``stack_info=True`` must yield a formatted ``stack_info`` string, never the bool."""
    log = make_logger()
    log.info("with stack", stack_info=True)

    for entry in (_console_entries(capsys)[-1], _file_entries(tmp_path)[-1]):
        stack = entry.get("stack_info")
        assert isinstance(stack, str)
        assert "Stack (most recent call last):" in stack


def _emit_via_helper(log: StandardizedLogger) -> None:
    """Indirection so ``stacklevel=2`` has a frame to skip."""
    log.info("through helper", stacklevel=2)


def test_stacklevel_forwarded_to_caller_resolution(
    make_logger: LoggerFactory, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """``stacklevel`` must shift caller resolution and never appear as a field."""
    log = make_logger()
    _emit_via_helper(log)

    for entry in (_console_entries(capsys)[-1], _file_entries(tmp_path)[-1]):
        assert "stacklevel" not in entry
        assert entry["function"] == "test_stacklevel_forwarded_to_caller_resolution"


def test_extra_dict_merged_and_cannot_shadow_canonical(
    make_logger: LoggerFactory, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """``extra`` keys become fields but cannot overwrite canonical metadata."""
    log = make_logger()
    log.info("real", extra={"request_id": "r-1", "level": "sneaky"})

    for entry in (_console_entries(capsys)[-1], _file_entries(tmp_path)[-1]):
        assert "extra" not in entry
        assert entry["request_id"] == "r-1"
        assert entry["level"] == "INFO"
        assert entry["caller_level"] == "sneaky"


# ---------------------------------------------------------------------------
# Reserved canonical keys
# ---------------------------------------------------------------------------


def test_caller_kwargs_cannot_replace_canonical_fields(
    make_logger: LoggerFactory, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """timestamp / level / logger / message stay canonical; caller values are namespaced."""
    log = make_logger()
    log.warning(
        "the truth",
        timestamp="2000-01-01T00:00:00Z",
        level="LOL",
        message="hijacked",
        logger="evil",
    )

    for entry in (_console_entries(capsys)[-1], _file_entries(tmp_path)[-1]):
        assert entry["level"] == "WARNING"
        assert entry["message"] == "the truth"
        assert entry["logger"] == "svc"
        assert isinstance(entry["timestamp"], str)
        assert entry["timestamp"].endswith("Z") and entry["timestamp"] != "2000-01-01T00:00:00Z"
        assert entry["caller_timestamp"] == "2000-01-01T00:00:00Z"
        assert entry["caller_level"] == "LOL"
        assert entry["caller_message"] == "hijacked"
        assert entry["caller_logger"] == "evil"


# ---------------------------------------------------------------------------
# Deterministic serialization
# ---------------------------------------------------------------------------


def test_supported_value_types_round_trip(
    make_logger: LoggerFactory, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """str/int/float/bool/None/list/dict fields serialize natively and unchanged."""
    log = make_logger()
    log.info(
        "types",
        count=3,
        ratio=1.5,
        ok=True,
        nothing=None,
        items=[1, 2, "x"],
        meta={"k": "v"},
    )

    for entry in (_console_entries(capsys)[-1], _file_entries(tmp_path)[-1]):
        assert entry["count"] == 3
        assert entry["ratio"] == 1.5
        assert entry["ok"] is True
        assert entry["nothing"] is None
        assert entry["items"] == [1, 2, "x"]
        assert entry["meta"] == {"k": "v"}


def test_unsupported_value_type_falls_back_to_repr(
    make_logger: LoggerFactory, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A value json cannot serialize is emitted as its repr, not raised to the caller."""
    log = make_logger()
    sentinel = object()
    log.info("weird", obj=sentinel)  # must not raise

    for entry in (_console_entries(capsys)[-1], _file_entries(tmp_path)[-1]):
        assert entry["obj"] == repr(sentinel)


def test_formatting_failure_routed_through_handle_error(
    make_logger: LoggerFactory, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An unserializable structured payload is dropped via handleError on both handlers."""
    log = make_logger()
    file_calls: list[object] = []
    console_calls: list[object] = []
    monkeypatch.setattr(_file_handler(log), "handleError", file_calls.append)
    monkeypatch.setattr(_console_handler(log), "handleError", console_calls.append)

    circular: dict[str, object] = {}
    circular["self"] = circular
    log.info("cannot serialize", payload=circular)  # must not raise

    assert len(file_calls) == 1
    assert len(console_calls) == 1
    assert all(entry.get("message") != "cannot serialize" for entry in _file_entries(tmp_path))


def test_write_failure_routed_through_handle_error(
    make_logger: LoggerFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A raw write error reaches handleError instead of propagating to the caller."""
    log = make_logger()
    handler = _file_handler(log)

    class _BoomStream:
        name = "boom"

        def write(self, _text: str) -> int:
            raise RuntimeError("disk gone")

        def flush(self) -> None:
            pass

    monkeypatch.setattr(handler, "_stream", _BoomStream())
    monkeypatch.setattr(handler, "_needs_date_rollover", lambda _today: False)
    monkeypatch.setattr(handler, "_needs_inode_rollover", lambda: False)
    calls: list[object] = []
    monkeypatch.setattr(handler, "handleError", calls.append)

    log.error("write will fail")  # must not raise

    assert len(calls) == 1


# ---------------------------------------------------------------------------
# Logger name path confinement
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "evil_name",
    [
        "../escape",
        "../../escape",
        "/abs/escape",
        "a/b/escape",
        "a\\b\\escape",
        "..",
        "with\x00null",
    ],
)
def test_logger_name_cannot_escape_log_dir(tmp_path: Path, evil_name: str) -> None:
    """A logger name with separators / traversal stays confined to log_dir."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    handler = _DateRollingFileHandler(log_dir=log_dir, logger_name=evil_name)
    try:
        assert handler._current_date is not None
        target = handler._path_for_date(handler._current_date).resolve()
        assert target.is_relative_to(log_dir.resolve())
        assert handler._stream is not None
        assert Path(handler._stream.name).resolve().is_relative_to(log_dir.resolve())
    finally:
        handler.close()

    stray = [p for p in tmp_path.iterdir() if p != log_dir]
    assert stray == []


def test_standardized_logger_traversal_name_writes_inside_log_dir(
    make_logger: LoggerFactory, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The path is sanitized while the JSON ``logger`` field keeps the true name."""
    log = make_logger(name="../../evil")
    log.info("hi")

    handler = _file_handler(log)
    assert handler._stream is not None
    assert Path(handler._stream.name).resolve().is_relative_to(tmp_path.resolve())
    assert _console_entries(capsys)[-1]["logger"] == "../../evil"


# ---------------------------------------------------------------------------
# Existing public construction paths
# ---------------------------------------------------------------------------


def test_from_config_construction_preserved(tmp_path: Path) -> None:
    """StandardizedLogger.from_config still builds a working file-backed logger."""
    config = StandardizedLoggerConfig(
        name="cfgsvc",
        log_dir=str(tmp_path),
        log_level=LogLevel.DEBUG,
    )
    log = StandardizedLogger.from_config(config)
    try:
        assert isinstance(log, StandardizedLogger)
        assert log.log_dir == tmp_path
        log.info("hello")
        assert _file_entries(tmp_path, "cfgsvc")[-1]["message"] == "hello"
    finally:
        for handler in list(log.handlers):
            handler.close()


def test_direct_construction_without_log_dir_preserved(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Direct construction with no log_dir still emits structured stderr only."""
    log = StandardizedLogger("console-only", level=DEBUG)
    try:
        log.info("just stderr", answer=42)
        entry = _console_entries(capsys)[-1]
        assert entry["message"] == "just stderr"
        assert entry["answer"] == 42
        assert entry["logger"] == "console-only"
    finally:
        for handler in list(log.handlers):
            handler.close()
