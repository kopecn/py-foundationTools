"""A standardized logger for shared API use."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from errno import EACCES, ENOSPC, EPIPE
from json import dumps
from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    NOTSET,
    WARNING,
    Formatter,
    Handler,
    Logger,
    LogRecord,
    StreamHandler,
    setLoggerClass,
)
from pathlib import Path
from typing import IO, Any

_COLORS: dict[int, str] = {
    DEBUG: "🔵",
    INFO: "🟢",
    WARNING: "🟠",
    ERROR: "🔴",
    CRITICAL: "🔴",
}


def _timestamp_format(log: LogRecord) -> str:
    """Render a log record's creation time as millisecond-precision UTC ISO-8601."""
    dt = datetime.fromtimestamp(log.created, tz=timezone.utc)
    ms = dt.microsecond // 1000
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + f".{ms:03d}Z"


class _HumanReadableFormatter(Formatter):
    """Formats log records as a single human-readable line, optionally with a colored level dot."""

    def __init__(self, colored_dots: bool = False) -> None:
        """Store whether formatted lines should be prefixed with a level-colored dot."""
        super().__init__()
        self._colored_dots = colored_dots

    def _format_base(self, record: LogRecord) -> str:
        """Build the base "timestamp [LEVEL] name: message" line."""
        ts = _timestamp_format(record)
        msg = record.getMessage()

        if self._colored_dots:
            dot = _COLORS.get(record.levelno, "")
            return f"{dot} {ts} [{record.levelname}] {record.name}: {msg}"

        return f"{ts} [{record.levelname}] {record.name}: {msg}"

    def format(self, record: LogRecord) -> str:
        """Format the record, appending exception details if present."""
        base_line = self._format_base(record)

        exc = record.exc_info
        if exc and exc[0] is not None:
            base_line = self._append_exception(base_line, exc)

        return base_line

    def _append_exception(
        self,
        line: str,
        exc: tuple[type[BaseException], BaseException, Any],
    ) -> str:
        """Append a formatted traceback to an already-formatted line."""
        return f"{line}\n{self.formatException(exc)}"


class _StructuredFormatter(Formatter):
    """Formats log records as single-line JSON for machine consumption."""

    def format(self, record: LogRecord) -> str:
        """Build and serialize the JSON log entry for the record."""
        log_entry = self._build_log_entry(record)
        return self._serialize(log_entry)

    def _build_log_entry(self, record: LogRecord) -> dict[str, Any]:
        """Assemble the structured fields describing the record."""
        entry: dict[str, Any] = {
            "timestamp": _timestamp_format(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "logger": record.name,
        }

        self._add_exception(entry, record)
        self._add_extra_fields(entry, record)

        return entry

    def _add_exception(self, entry: dict[str, Any], record: LogRecord) -> None:
        """Add a formatted traceback to the entry if the record carries one."""
        if record.exc_info and record.exc_info[0] is not None:
            entry["exception"] = self.formatException(record.exc_info)

    def _add_extra_fields(self, entry: dict[str, Any], record: LogRecord) -> None:
        """Merge caller-supplied structured fields into the entry."""
        extra = getattr(record, "extra_fields", None)
        if isinstance(extra, dict):
            entry.update(extra)

    def _serialize(self, entry: dict[str, Any]) -> str:
        """Serialize the entry dict to a JSON string."""
        return dumps(entry)


class _DateRollingFileHandler(Handler):
    """A file handler that rolls over to a new file at UTC day boundaries.

    Also detects the underlying file being replaced or removed out from under it
    (e.g. by log rotation tooling) via inode comparison, and reopens as needed.
    """

    def __init__(
        self,
        log_dir: Path,
        logger_name: str,
        level: int = NOTSET,
        flush_every: int = 1,
    ) -> None:
        """Open the initial log file for today's date under log_dir."""
        super().__init__(level)

        self._log_dir = log_dir
        self._logger_name = logger_name

        self._flush_every = max(flush_every, 1)
        self._write_count = 0

        self._stream: IO[str] | None = None
        self._current_date: str | None = None
        self._current_inode: int | None = None

        self._rollover(self._utc_date())

    @staticmethod
    def _utc_date() -> str:
        """Return today's date in UTC as YYYY-MM-DD."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _path_for_date(self, date_str: str) -> Path:
        """Build the log file path for a given date."""
        return self._log_dir / f"{self._logger_name}_{date_str}.log"

    def _close_stream(self) -> None:
        """Flush and close the current stream, ignoring filesystem-level errors."""
        if self._stream is None:
            return

        try:
            self._stream.flush()
            self._stream.close()
        except OSError:
            # Only filesystem-level failures are expected here
            pass
        finally:
            self._stream = None
            self._current_inode = None

    def _open_stream(self, date_str: str) -> None:
        """Open the log file for date_str and record its inode."""
        path = self._path_for_date(date_str)
        self._stream = open(path, "a", encoding="utf-8")  # noqa: SIM115

        try:
            self._current_inode = os.fstat(self._stream.fileno()).st_ino
        except OSError:
            self._current_inode = None

        self._current_date = date_str
        self._write_count = 0

    def _rollover(self, date_str: str) -> None:
        """Close the current stream and open the one for date_str."""
        self._close_stream()
        self._open_stream(date_str)

    def _needs_date_rollover(self, today: str) -> bool:
        """Return True if the open file's date no longer matches today."""
        return self._current_date != today

    def _needs_inode_rollover(self) -> bool:
        """Return True if the stream is missing or points at an unexpected inode."""
        if self._stream is None:
            return True

        try:
            current_inode = os.fstat(self._stream.fileno()).st_ino
            return self._current_inode is None or current_inode != self._current_inode
        except OSError:
            return True

    def emit(self, record: LogRecord) -> None:
        """Write a formatted record to the current file, rolling over first if needed."""
        try:
            today = self._utc_date()

            if self._needs_date_rollover(today) or self._needs_inode_rollover():
                self._rollover(today)

            if self._stream is None:
                return

            msg = self.format(record)
            self._stream.write(msg + "\n")

            self._write_count += 1
            if self._write_count >= self._flush_every:
                self._stream.flush()
                self._write_count = 0

        except OSError as e:
            # Expected: broken pipe, disk full, permission issues, etc.
            if e.errno in (EPIPE, ENOSPC, EACCES):
                self.handleError(record)
            else:
                raise  # don't silently hide unexpected system errors

    def close(self) -> None:
        """Close the underlying stream and the handler."""
        try:
            self._close_stream()
        finally:
            super().close()


class StandardizedLogger(Logger):
    """A `Logger` that self-configures structured JSON and/or stderr handlers.

    File logging (JSON, date-rolling) is used when `log_dir` is provided;
    otherwise falls back to a stderr stream handler.
    """

    def __init__(
        self,
        name: str,
        level: int = INFO,
        log_dir: Path | None = None,
        colored_logs: bool = False,
    ) -> None:
        """Configure this logger's handlers based on the given options."""
        super().__init__(name, level)

        self._log_dir = log_dir
        self._colored_logs = colored_logs

        self._configure_handlers()

    @classmethod
    def setLoggerClass(cls) -> None:
        """Register this class as the default logging.Logger implementation."""
        setLoggerClass(cls)

    # -------------------------
    # Handler setup
    # -------------------------
    def _configure_handlers(self) -> None:
        """Attach a file handler (if log_dir is set) and/or a stderr fallback handler."""
        self.handlers.clear()

        formatter = _StructuredFormatter()

        # File logging
        if self._log_dir is not None:
            self._log_dir.mkdir(parents=True, exist_ok=True)

            file_handler = _DateRollingFileHandler(
                log_dir=self._log_dir,
                logger_name=self.name,
                level=self.level,
            )
            file_handler.setFormatter(formatter)
            self.addHandler(file_handler)

        # Optional: fallback to stderr if no handlers exist
        if not self.handlers:
            self.addHandler(self._build_default_stream_handler(formatter))

    def _build_default_stream_handler(self, formatter: Formatter) -> StreamHandler[IO[str]]:
        """Build a stderr StreamHandler using the given formatter."""
        handler = StreamHandler(sys.stderr)
        handler.setFormatter(formatter)
        return handler

    @property
    def log_dir(self) -> Path | None:
        """The directory this logger writes date-rolled log files to, if any."""
        return self._log_dir

    def debug(self, msg: object, *args: object, **kwargs: Any) -> None:
        """Log msg at DEBUG level with structured keyword fields."""
        self._log_structured(DEBUG, msg, args, **kwargs)

    def info(self, msg: object, *args: object, **kwargs: Any) -> None:
        """Log msg at INFO level with structured keyword fields."""
        self._log_structured(INFO, msg, args, **kwargs)

    def warning(self, msg: object, *args: object, **kwargs: Any) -> None:
        """Log msg at WARNING level with structured keyword fields."""
        self._log_structured(WARNING, msg, args, **kwargs)

    def error(self, msg: object, *args: object, **kwargs: Any) -> None:
        """Log msg at ERROR level with structured keyword fields."""
        self._log_structured(ERROR, msg, args, **kwargs)

    def critical(self, msg: object, *args: object, **kwargs: Any) -> None:
        """Log msg at CRITICAL level with structured keyword fields."""
        self._log_structured(CRITICAL, msg, args, **kwargs)

    def _log_structured(
        self,
        level: int,
        msg: object,
        args: tuple[object, ...],
        **kwargs: Any,
    ) -> None:
        """Split reserved kwargs (exc_info, extra) from structured fields and dispatch."""
        if not self.isEnabledFor(level):
            return

        exc_info = kwargs.pop("exc_info", None)
        extra = kwargs.pop("extra", None)

        # everything else becomes structured fields
        structured_fields = {k: v for k, v in kwargs.items() if not k.startswith("_")}

        if isinstance(extra, dict):
            structured_fields.update(extra)

        self._structured_log(
            level=level,
            msg=str(msg),
            args=args,
            exc_info=exc_info,
            extra=structured_fields,
        )

    def _structured_log(
        self,
        level: int,
        msg: str,
        args: tuple[Any, ...] = (),
        extra: dict[str, Any] | None = None,
        exc_info: bool = False,
        **kwargs: Any,
    ) -> None:
        """Merge extra/kwargs fields and emit the record via the stdlib logging machinery."""
        if args:
            msg = msg % args
        merged: dict[str, Any] = {**(extra or {}), **kwargs}
        Logger._log(
            self,
            level,
            msg,
            (),
            exc_info=exc_info,
            extra={"extra_fields": merged} if merged else None,
            stacklevel=3,
        )
