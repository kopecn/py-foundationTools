"""
Path and filename-pattern utilities.

:func:`find_matching_paths` walks a directory tree and returns the entries that
pass a set of optional filters (pattern, extensions, exclusions, hidden). The
:class:`SuggestedPatterns`, :class:`SuggestedExtensions`, and
:class:`SuggestedExcludePatterns` enums hold ready-made values a caller can pass.
"""

import itertools
import sys
import threading
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from fnmatch import fnmatch
from glob import glob
from pathlib import Path

__all__ = ["find_matching_paths"]


class SuggestedPatterns(str, Enum):
    """Ready-made ``pattern`` values to pass explicitly. Pull one out via its ``.value``."""

    #: Match every entry (``fnmatch`` ``*`` matches any relative path).
    ANY = "*"
    #: Match only entries nested below the top level (a relative path containing ``/``).
    ANY_RECURSIVE = "**/*"


class SuggestedExtensions(Enum):
    """Ready-made ``extensions`` values to pass explicitly. Pull one out via its ``.value``."""

    #: Normalizes to the suffix ``.*``, which no real file has, so it selects nothing.
    ANY = ("*",)
    #: Common tabular data files (``.csv``, ``.txt``).
    TABULAR = ("csv", "txt")


class SuggestedExcludePatterns(Enum):
    """Ready-made ``exclude_patterns`` values. Pull one out via its ``.value``."""

    #: The ``.build`` directory. Hidden dirs are absent from the walk, so this excludes nothing.
    BUILD = ("/.build/",)


@dataclass
class _Progress:
    """Best-effort progress the worker writes and the spinner thread reads."""

    step: str = "scanning"
    count: int = 0


_SPINNER_FRAMES = "|/-\\"


def find_matching_paths(
    starting_dir: Path | None = None,
    pattern: str | None = None,
    extensions: Iterable[str] | None = None,
    exclude_patterns: Iterable[str] | None = None,
    return_hidden: bool = True,
    indicator: bool = True,
    join_timeout: float | None = None,
) -> list[Path]:
    """Recursively collect paths under ``starting_dir`` that pass every active filter.

    Walks ``starting_dir`` recursively and returns each entry matching all of the
    filters below. A filter left as ``None`` (or empty) keeps everything.

    Args:
        starting_dir: Directory to search, resolved before use. ``None`` uses the
            folder of the running Python executable.
        pattern: ``fnmatch`` glob tested against each entry's ``starting_dir``-relative
            POSIX path and its bare name; a match on either keeps the entry.
            ``None`` keeps every entry.
        extensions: Suffixes to keep, leading dot optional (e.g. ``["csv", ".txt"]``).
            When set, only files whose suffix matches are kept and directories are
            dropped. ``None`` or empty keeps every entry.
        exclude_patterns: ``fnmatch`` globs tested against each entry's ``/``-anchored
            relative path (directories get a trailing ``/``); a match drops the entry.
            ``None`` or empty drops nothing.
        return_hidden: When ``False``, drop any entry with a dot-prefixed path component.
        indicator: When ``True`` (default), run the walk/filter on the calling thread
            while a second thread animates a step + spinner on stderr (TTY only).
            When ``False``, run synchronously with no thread and no output.
        join_timeout: Seconds to wait for the spinner thread to stop when
            ``indicator`` is ``True``. ``None`` (default) waits indefinitely; a
            number bounds the wait (the thread is a daemon, so any straggler is
            reaped at interpreter exit). Ignored when ``indicator`` is ``False``.

    Returns:
        Matching paths, in the order the recursive walk yields them.
    """
    if not indicator:
        return _collect_matches(starting_dir, pattern, extensions, exclude_patterns, return_hidden)

    progress = _Progress()
    stop = threading.Event()
    spinner = threading.Thread(target=_render_progress, args=(progress, stop), daemon=True)
    spinner.start()
    try:
        return _collect_matches(
            starting_dir, pattern, extensions, exclude_patterns, return_hidden, progress
        )
    finally:
        stop.set()
        spinner.join(timeout=join_timeout)
        _clear_line()


def _collect_matches(
    starting_dir: Path | None,
    pattern: str | None,
    extensions: Iterable[str] | None,
    exclude_patterns: Iterable[str] | None,
    return_hidden: bool,
    progress: _Progress | None = None,
) -> list[Path]:
    """Walk ``starting_dir`` recursively and return the entries passing every filter.

    Extracted verbatim from the original body; the only additions are the optional
    ``progress`` writes, which never change the returned list.
    """
    starting_dir = (starting_dir or Path(sys.executable).parent).resolve()

    extensions = {ext if ext.startswith(".") else f".{ext}" for ext in (extensions or ())}

    exclude_patterns = tuple(exclude_patterns or ())

    def is_hidden(p: Path) -> bool:
        return any(part.startswith(".") for part in p.relative_to(starting_dir).parts)

    def matches_pattern(p: Path) -> bool:
        if pattern is None:
            return True

        rel = p.relative_to(starting_dir).as_posix()
        return fnmatch(rel, pattern) or fnmatch(p.name, pattern)

    def matches_extension(p: Path) -> bool:
        if not extensions or not p.is_file():
            return not extensions

        return p.suffix in extensions

    def is_excluded(p: Path) -> bool:
        if not exclude_patterns:
            return False

        rel = "/" + p.relative_to(starting_dir).as_posix()

        if p.is_dir():
            rel += "/"

        return any(fnmatch(rel, pat) or fnmatch(rel.lstrip("/"), pat) for pat in exclude_patterns)

    paths = (Path(p) for p in glob(str(starting_dir / "**" / "*"), recursive=True))

    if progress is not None:
        progress.step = "filtering"

    results: list[Path] = []

    for p in paths:
        if progress is not None:
            progress.count += 1

        if not return_hidden and is_hidden(p):
            continue

        if is_excluded(p):
            continue

        if not matches_pattern(p):
            continue

        if not matches_extension(p):
            continue

        results.append(p)

    return results


def _render_progress(progress: _Progress, stop: threading.Event) -> None:
    """Second thread: read ``progress`` and animate a spinner on stderr (TTY only)."""
    if not sys.stderr.isatty():
        return

    for frame in itertools.cycle(_SPINNER_FRAMES):
        sys.stderr.write(f"\r{frame} {progress.step} ({progress.count})")
        sys.stderr.flush()
        if stop.wait(0.1):
            return


def _clear_line() -> None:
    """Erase the spinner line from stderr (TTY only)."""
    if sys.stderr.isatty():
        sys.stderr.write("\r\033[K")
        sys.stderr.flush()
