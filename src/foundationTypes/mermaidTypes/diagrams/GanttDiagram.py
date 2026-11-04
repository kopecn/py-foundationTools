# =============================================================================
# AUTO-GENERATED FILE — DO NOT EDIT
# Generated from JSON Schema via quicktype. Any manual edits will be
# overwritten the next time codegen runs (make codegen-all).
# To modify, update the source schema in schema/schemas/ and re-run codegen.
# =============================================================================

from enum import Enum
from dataclasses import dataclass
from foundationTypes.data_model_helper import (
    DataModelHelper,
    from_list,
    from_none,
    from_str,
    from_union,
    to_class,
    to_enum,
)
from typing import List, Optional, Any, TypeVar, Callable, Type, cast

T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


class TagElement(Enum):
    """A status tag on a task. `active` (Mermaid `active`); `done` (`done`); `critical` (`crit`)."""

    ACTIVE = "active"
    CRITICAL = "critical"
    DONE = "done"


class TypeEnum(Enum):
    """The kind of gantt element. `task` a normal bar; `milestone` a single instant drawn at
    startDate + duration/2 (Mermaid `milestone`); `verticalMarker` a full-height reference
    line that takes no row (Mermaid `vert`).
    """

    MILESTONE = "milestone"
    TASK = "task"
    VERTICAL_MARKER = "verticalMarker"


@dataclass
class TaskElement(DataModelHelper):
    """A gantt task. Start and end are composed from the fields below, mirroring Mermaid's task
    metadata: start is `startDate`, else `after` (the latest end of the referenced tasks),
    else the preceding task's end when both are omitted; end is `endDate`, else `duration`
    (added to the start), else `until` (the start of the referenced tasks). Set at most one
    start source and at most one end source.
    """

    title: str
    """The task label."""

    after: Optional[List[str]] = None
    """Start at the latest end of these task ids (Mermaid `after <id> ...`). Ignored if
    `startDate` is set.
    """
    duration: Optional[str] = None
    end_date: Optional[str] = None
    """An explicit end, parsed with `dateFormat`."""

    id: Optional[str] = None
    """The task id, referenced by other tasks' `after` and `until`."""

    start_date: Optional[str] = None
    """An explicit start, parsed with `dateFormat`."""

    tags: Optional[List[TagElement]] = None
    """Status tags on the task."""

    type: Optional[TypeEnum] = None
    until: Optional[List[str]] = None
    """End at the start of these task ids (Mermaid `until <id> ...`, v10.9.0+). Ignored if
    `endDate` or `duration` is set.
    """

    @classmethod
    def from_dict(cls, obj: Any) -> "TaskElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        title = from_str(obj.get("title"))
        after = from_union([lambda x: from_list(from_str, x), from_none], obj.get("after"))
        duration = from_union([from_str, from_none], obj.get("duration"))
        end_date = from_union([from_str, from_none], obj.get("endDate"))
        id = from_union([from_str, from_none], obj.get("id"))
        start_date = from_union([from_str, from_none], obj.get("startDate"))
        tags = from_union([lambda x: from_list(TagElement, x), from_none], obj.get("tags"))
        type = from_union([TypeEnum, from_none], obj.get("type"))
        until = from_union([lambda x: from_list(from_str, x), from_none], obj.get("until"))
        return TaskElement(title, after, duration, end_date, id, start_date, tags, type, until)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["title"] = from_str(self.title)
        if self.after is not None:
            result["after"] = from_union([lambda x: from_list(from_str, x), from_none], self.after)
        if self.duration is not None:
            result["duration"] = from_union([from_str, from_none], self.duration)
        if self.end_date is not None:
            result["endDate"] = from_union([from_str, from_none], self.end_date)
        if self.id is not None:
            result["id"] = from_union([from_str, from_none], self.id)
        if self.start_date is not None:
            result["startDate"] = from_union([from_str, from_none], self.start_date)
        if self.tags is not None:
            result["tags"] = from_union(
                [lambda x: from_list(lambda x: to_enum(TagElement, x), x), from_none], self.tags
            )
        if self.type is not None:
            result["type"] = from_union([lambda x: to_enum(TypeEnum, x), from_none], self.type)
        if self.until is not None:
            result["until"] = from_union([lambda x: from_list(from_str, x), from_none], self.until)
        return result


@dataclass
class SectionElement(DataModelHelper):
    """A named section grouping tasks."""

    name: str
    """The section name (required by Mermaid)."""

    tasks: Optional[List[TaskElement]] = None
    """The tasks in this section."""

    @classmethod
    def from_dict(cls, obj: Any) -> "SectionElement":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        name = from_str(obj.get("name"))
        tasks = from_union(
            [lambda x: from_list(TaskElement.from_dict, x), from_none], obj.get("tasks")
        )
        return SectionElement(name, tasks)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        result["name"] = from_str(self.name)
        if self.tasks is not None:
            result["tasks"] = from_union(
                [lambda x: from_list(lambda x: to_class(TaskElement, x), x), from_none], self.tasks
            )
        return result


class Weekday(Enum):
    """The weekday a week-based `tickInterval` starts on. Default is sunday."""

    FRIDAY = "friday"
    MONDAY = "monday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"
    THURSDAY = "thursday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"


class Weekend(Enum):
    """Which day the weekend starts on when excluding weekends (v11.0.0+). `saturday` is the
    default (Saturday and Sunday); `friday` makes the weekend Friday and Saturday.
    """

    FRIDAY = "friday"
    SATURDAY = "saturday"


@dataclass
class GanttDiagram(DataModelHelper):
    """The gantt diagram body: a time-scheduled bar chart. It carries diagram-level date and
    axis settings, excluded dates, flat sections, and tasks whose start and end are expressed
    as dates, durations, or references to other tasks. A sibling of the flowchart and class
    diagram bodies in this folder; it reuses the same method (self-contained $defs, readable
    enums, OCP-open objects) over gantt's own shape.
    """

    axis_format: Optional[str] = None
    """The output date format on the rendered axis (d3-time-format tokens, e.g. `%Y-%m-%d`).
    Default `YYYY-MM-DD`.
    """
    date_format: Optional[str] = None
    """The format of the date input of the gantt elements (dayjs tokens, e.g. `YYYY-MM-DD`, the
    default, or `X` for a Unix timestamp). Defines how `startDate`/`endDate` strings are
    parsed.
    """
    excludes: Optional[List[str]] = None
    """Dates excluded from task duration calculations. Each entry is a specific date (in
    `dateFormat`), a day of the week (e.g. `sunday`), or `weekends`. The word `weekdays` is
    not supported.
    """
    sections: Optional[List[SectionElement]] = None
    """The sections that group tasks."""

    tasks: Optional[List[TaskElement]] = None
    """Tasks not placed in a section."""

    tick_interval: Optional[str] = None
    """The axis tick spacing, a positive integer followed by a unit, e.g. `1day` or `1week`.
    Default is auto.
    """
    title: Optional[str] = None
    """An optional title displayed at the top of the chart."""

    today_marker: Optional[str] = None
    """The today marker. A style string (e.g. `stroke-width:5px,stroke:#0f0,opacity:0.5`), or
    `off` to hide it.
    """
    weekday: Optional[Weekday] = None
    weekend: Optional[Weekend] = None

    @classmethod
    def from_dict(cls, obj: Any) -> "GanttDiagram":
        if not isinstance(obj, dict):
            raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
        axis_format = from_union([from_str, from_none], obj.get("axisFormat"))
        date_format = from_union([from_str, from_none], obj.get("dateFormat"))
        excludes = from_union([lambda x: from_list(from_str, x), from_none], obj.get("excludes"))
        sections = from_union(
            [lambda x: from_list(SectionElement.from_dict, x), from_none], obj.get("sections")
        )
        tasks = from_union(
            [lambda x: from_list(TaskElement.from_dict, x), from_none], obj.get("tasks")
        )
        tick_interval = from_union([from_str, from_none], obj.get("tickInterval"))
        title = from_union([from_str, from_none], obj.get("title"))
        today_marker = from_union([from_str, from_none], obj.get("todayMarker"))
        weekday = from_union([Weekday, from_none], obj.get("weekday"))
        weekend = from_union([Weekend, from_none], obj.get("weekend"))
        return GanttDiagram(
            axis_format,
            date_format,
            excludes,
            sections,
            tasks,
            tick_interval,
            title,
            today_marker,
            weekday,
            weekend,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.axis_format is not None:
            result["axisFormat"] = from_union([from_str, from_none], self.axis_format)
        if self.date_format is not None:
            result["dateFormat"] = from_union([from_str, from_none], self.date_format)
        if self.excludes is not None:
            result["excludes"] = from_union(
                [lambda x: from_list(from_str, x), from_none], self.excludes
            )
        if self.sections is not None:
            result["sections"] = from_union(
                [lambda x: from_list(lambda x: to_class(SectionElement, x), x), from_none],
                self.sections,
            )
        if self.tasks is not None:
            result["tasks"] = from_union(
                [lambda x: from_list(lambda x: to_class(TaskElement, x), x), from_none], self.tasks
            )
        if self.tick_interval is not None:
            result["tickInterval"] = from_union([from_str, from_none], self.tick_interval)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        if self.today_marker is not None:
            result["todayMarker"] = from_union([from_str, from_none], self.today_marker)
        if self.weekday is not None:
            result["weekday"] = from_union([lambda x: to_enum(Weekday, x), from_none], self.weekday)
        if self.weekend is not None:
            result["weekend"] = from_union([lambda x: to_enum(Weekend, x), from_none], self.weekend)
        return result


def gantt_diagram_from_dict(s: Any) -> GanttDiagram:
    return GanttDiagram.from_dict(s)


def gantt_diagram_to_dict(x: GanttDiagram) -> Any:
    return to_class(GanttDiagram, x)
