# =============================================================================
# AUTO-GENERATED FILE — DO NOT EDIT
# Generated from JSON Schema via quicktype. Any manual edits will be
# overwritten the next time codegen runs (make codegen-all).
# To modify, update the source schema in schema/schemas/ and re-run codegen.
# =============================================================================

from dataclasses import dataclass
from enum import Enum
from typing import Any, TypeVar

from foundationTypes.dataModelHelper import (
    DataModelHelper,
    from_bool,
    from_int,
    from_none,
    from_str,
    from_union,
    to_class,
    to_enum,
)

T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


class LogLevel(Enum):
    """Minimum severity level that will be emitted. Log events below this threshold are ignored."""

    CRITICAL = "CRITICAL"
    DEBUG = "DEBUG"
    ERROR = "ERROR"
    INFO = "INFO"
    WARNING = "WARNING"


@dataclass
class StandardizedLoggerConfig(DataModelHelper):
    """Configuration object for initializing an AutomationLogger. Defines output destinations,
    formatting modes, and log level behavior.
    """

    name: str
    """Unique logger identifier used as the logging namespace and tag across all outputs."""

    console_level_icons: bool | None = None
    """Adds visual severity indicators to console logs. Applies only to human-readable output."""

    console_pretty: bool | None = None
    """Enables human-readable log output to standard error for interactive and development use."""

    file_path: str | None = None
    """Base filesystem path for writing persistent log files. Enables file logging when set."""

    log_level: LogLevel | None = None
    """Minimum severity level that will be emitted. Log events below this threshold are ignored."""

    rotation_days: int | None = None
    """Number of UTC calendar days before a new log file is created. Rotation occurs at day
    boundaries.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "StandardizedLoggerConfig":
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        console_level_icons = from_union([from_bool, from_none], obj.get("console_level_icons"))
        console_pretty = from_union([from_bool, from_none], obj.get("console_pretty"))
        file_path = from_union([from_str, from_none], obj.get("file_path"))
        log_level = from_union([LogLevel, from_none], obj.get("log_level"))
        rotation_days = from_union([from_int, from_none], obj.get("rotation_days"))
        return StandardizedLoggerConfig(
            name, console_level_icons, console_pretty, file_path, log_level, rotation_days
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        if self.console_level_icons is not None:
            result["console_level_icons"] = from_union(
                [from_bool, from_none], self.console_level_icons
            )
        if self.console_pretty is not None:
            result["console_pretty"] = from_union([from_bool, from_none], self.console_pretty)
        if self.file_path is not None:
            result["file_path"] = from_union([from_str, from_none], self.file_path)
        if self.log_level is not None:
            result["log_level"] = from_union(
                [lambda x: to_enum(LogLevel, x), from_none], self.log_level
            )
        if self.rotation_days is not None:
            result["rotation_days"] = from_union([from_int, from_none], self.rotation_days)
        return result


def standardized_logger_config_from_dict(s: Any) -> StandardizedLoggerConfig:
    return StandardizedLoggerConfig.from_dict(s)


def standardized_logger_config_to_dict(x: StandardizedLoggerConfig) -> Any:
    return to_class(StandardizedLoggerConfig, x)
