"""A standardized logger for shared API use."""

from __future__ import annotations

import os
import sys
from datetime import date, datetime, timezone
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
from types import TracebackType
from typing import IO, Any

from foundationTypes.standardizedLoggerConfig.StandardizedLoggerConfig import (
    LogLevel,
    StandardizedLoggerConfig,
)

_LOG_LEVEL_MAP: dict[LogLevel, int] = {
    LogLevel.DEBUG: DEBUG,
    LogLevel.INFO: INFO,
    LogLevel.WARNING: WARNING,
    LogLevel.ERROR: ERROR,
    LogLevel.CRITICAL: CRITICAL,
}

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
    return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")


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
        exc: tuple[type[BaseException], BaseException, TracebackType | None],
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
    """A file handler that rolls over to a new file every `rotation_days` UTC days.

    Also detects the underlying file being replaced or removed out from under it
    (e.g. by log rotation tooling) via inode comparison, and reopens as needed.
    """

    def __init__(
        self,
        log_dir: Path,
        logger_name: str,
        level: int = NOTSET,
        flush_every: int = 1,
        rotation_days: int = 1,
    ) -> None:
        """Open the initial log file for today's date under log_dir."""
        super().__init__(level)

        self._log_dir = log_dir
        self._logger_name = logger_name

        self._flush_every = max(flush_every, 1)
        self._write_count = 0
        self._rotation_days = max(rotation_days, 1)

        self._stream: IO[str] | None = None
        self._current_date: str | None = None

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

    def _open_stream(self, date_str: str) -> None:
        """Open the log file for date_str."""
        path = self._path_for_date(date_str)
        self._stream = open(path, "a", encoding="utf-8")  # noqa: SIM115

        self._current_date = date_str
        self._write_count = 0

    def _rollover(self, date_str: str) -> None:
        """Close the current stream and open the one for date_str."""
        self._close_stream()
        self._open_stream(date_str)

    def _needs_date_rollover(self, today: str) -> bool:
        """Return True if rotation_days have elapsed since the open file's anchor date."""
        if self._current_date is None:
            return True
        elapsed = (date.fromisoformat(today) - date.fromisoformat(self._current_date)).days
        return elapsed >= self._rotation_days

    def _needs_inode_rollover(self) -> bool:
        """Return True if the configured path no longer refers to our open file.

        Compares the currently open descriptor's (device, inode) against a fresh
        `stat` of the configured path, so an external rename, replacement, or
        removal of that path is detected. A missing path counts as rollover.
        """
        if self._stream is None:
            return True

        try:
            open_stat = os.fstat(self._stream.fileno())
        except OSError:
            return True

        path = self._path_for_date(self._current_date) if self._current_date else None
        if path is None:
            return True

        try:
            path_stat = os.stat(path)
        except OSError:
            return True

        return (open_stat.st_dev, open_stat.st_ino) != (path_stat.st_dev, path_stat.st_ino)

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
    """A `Logger` that self-configures a stderr console handler plus an optional file handler.

    The stderr handler always runs (JSON by default, or human-readable with
    `console_pretty`). A date-rolling JSON file handler is additionally attached
    when `log_dir` is provided. Build from a `StandardizedLoggerConfig` via
    `from_config`, or construct directly.
    """

    def __init__(
        self,
        name: str,
        level: int = INFO,
        log_dir: Path | None = None,
        rotation_days: int = 1,
        console_pretty: bool = False,
        console_level_icons: bool = False,
    ) -> None:
        """Configure this logger's handlers based on the given options."""
        super().__init__(name, level)

        self._log_dir = log_dir
        self._rotation_days = rotation_days
        self._console_pretty = console_pretty
        self._console_level_icons = console_level_icons

        self._configure_handlers()

    @classmethod
    def from_config(cls, config: StandardizedLoggerConfig) -> StandardizedLogger:
        """Build a StandardizedLogger from a StandardizedLoggerConfig."""
        return cls(
            name=config.name,
            level=_LOG_LEVEL_MAP[config.log_level] if config.log_level else INFO,
            log_dir=Path(config.log_dir) if config.log_dir else None,
            rotation_days=config.rotation_days or 1,
            console_pretty=config.console_pretty or False,
            console_level_icons=config.console_level_icons or False,
        )

    @classmethod
    def setLoggerClass(cls) -> None:
        """Register this class as the default logging.Logger implementation."""
        setLoggerClass(cls)

    # -------------------------
    # Handler setup
    # -------------------------
    def _configure_handlers(self) -> None:
        """Attach a stderr console handler and, if log_dir is set, a file handler."""
        self.handlers.clear()

        self.addHandler(self._build_console_handler())

        if self._log_dir is not None:
            self._log_dir.mkdir(parents=True, exist_ok=True)

            file_handler = _DateRollingFileHandler(
                log_dir=self._log_dir,
                logger_name=self.name,
                level=self.level,
                rotation_days=self._rotation_days,
            )
            file_handler.setFormatter(_StructuredFormatter())
            self.addHandler(file_handler)

    def _build_console_handler(self) -> StreamHandler[IO[str]]:
        """Build the stderr handler, human-readable or JSON per console_pretty."""
        formatter: Formatter = (
            _HumanReadableFormatter(colored_dots=self._console_level_icons)
            if self._console_pretty
            else _StructuredFormatter()
        )
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
        structured_fields = dict(kwargs)

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
        exc_info: bool
        | tuple[type[BaseException], BaseException, TracebackType | None]
        | BaseException
        | None = None,
        **kwargs: Any,
    ) -> None:
        """Merge extra/kwargs fields and emit the record via the stdlib logging machinery."""
        if args:
            msg = msg % args
        # kwargs (passed explicitly to _structured_log) take precedence over same-named
        # keys already folded into extra by _log_structured.
        merged: dict[str, Any] = {**(extra or {}), **kwargs}
        self._log(
            level,
            msg,
            (),
            exc_info=exc_info,
            extra={"extra_fields": merged} if merged else None,
            stacklevel=3,
        )
