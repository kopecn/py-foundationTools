"""Tests for foundation_tools.standardized_logger's external-rotation detection."""

from pathlib import Path

from foundation_tools.standardized_logger import _DateRollingFileHandler


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
