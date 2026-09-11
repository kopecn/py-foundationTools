"""
Path and filename-pattern utilities.

:func:`find_matching_paths` walks a directory tree and returns the entries that
pass a set of optional filters (pattern, extensions, exclusions, hidden). The
:class:`SuggestedPatterns`, :class:`SuggestedExtensions`, and
:class:`SuggestedExcludePatterns` enums hold ready-made values a caller can pass.
"""

from glob import glob
from enum import Enum
from pathlib import Path
from fnmatch import fnmatch
import sys
from collections.abc import Iterable

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
    """Ready-made ``exclude_patterns`` values to pass explicitly. Pull one out via its ``.value``."""

    #: The ``.build`` directory. Hidden entries are absent from the walk, so this excludes nothing as-is.
    BUILD = ("/.build/",)


def find_matching_paths(
    starting_dir: Path | None = None,
    pattern: str | None = None,
    extensions: Iterable[str] | None = None,
    exclude_patterns: Iterable[str] | None = None,
    return_hidden: bool = True,
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

    Returns:
        Matching paths, in the order the recursive walk yields them.
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

    results: list[Path] = []

    for p in paths:
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
