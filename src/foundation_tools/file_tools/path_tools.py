"""
Path and filename-pattern utilities.

:func:`find_matching_paths` expands a relative filename pattern across a set of
extensions, resolves the resulting globs beneath an explicit absolute root, and
prunes matches that hit an exclusion pattern (``/.build/`` by default).
"""

from collections.abc import Iterable
from fnmatch import fnmatch
from pathlib import Path
from typing import Final, NamedTuple

__all__ = [
    "ANY_EXTENSION",
    "DEFAULT_EXCLUDED_PATTERNS",
    "DEFAULT_EXTENSIONS",
    "find_matching_paths",
]

#: Extensions applied when a caller does not specify any. Override per call site by
#: passing an explicit sequence; pass ``None`` to match any extension.
DEFAULT_EXTENSIONS: Final[tuple[str, ...]] = ("csv", "txt")

#: Extension wildcard substituted when a caller passes ``extensions=None``.
ANY_EXTENSION: Final[str] = "*"

#: Name globs excluded from results. A leading and/or
#: trailing ``/`` marks the entry as a *directory* glob (``/.build/``, ``/build*``,
#: ``*cache/``), which excludes the whole subtree; an entry with no slash is a *file*
#: glob (``*.pyc``). Pass an explicit sequence to extend it or ``[]`` to disable
#: pruning entirely.
DEFAULT_EXCLUDED_PATTERNS: Final[tuple[str, ...]] = ("/.build/",)


class _Exclusions(NamedTuple):
    """Exclusion globs split by what they match, with the ``/`` markers stripped."""

    directories: tuple[str, ...]
    files: tuple[str, ...]

    def __bool__(self) -> bool:
        return bool(self.directories or self.files)


def find_matching_paths(
    root: Path,
    pattern: str,
    extensions: Iterable[str] | None = DEFAULT_EXTENSIONS,
    *,
    exclude_patterns: Iterable[str] = DEFAULT_EXCLUDED_PATTERNS,
) -> list[Path]:
    """
    Find paths beneath ``root`` matching a pattern and set of extensions.

    Args:
        root: Existing absolute directory against which to resolve the patterns.
            Requiring an absolute path makes resolution independent of the process
            working directory.
        pattern: Base filename glob pattern including any wildcard
            (e.g. ``xyz.*waveform.*``).
        extensions: Extensions to append, with or without a leading dot
            (e.g. ``["txt", ".csv"]``). Blank entries are ignored. Defaults to
            :data:`DEFAULT_EXTENSIONS`. ``None`` matches any extension
            (``{pattern}.*``); an empty sequence expands nothing and uses
            the pattern unchanged.
        exclude_patterns: Name globs (never paths) to prune. A leading and/or
            trailing ``/`` marks a **directory** glob —
            ``/.build/``, ``/build*``, ``*cache/``, ``/xyz*xyz/`` are all
            equivalent in effect — which matches any directory between ``root``
            and the match, so the whole subtree is excluded from the result.
            An entry with no slash is a **file** glob (``*.pyc``) and is matched
            only against the final component, and only when that component is
            not a directory. Defaults to :data:`DEFAULT_EXCLUDED_PATTERNS`; pass
            ``[]`` to disable pruning.

    Returns:
        The paths under ``root`` that the expanded patterns match, sorted within
        each pattern and de-duplicated across patterns, with every
        ``exclude_patterns`` hit removed.

    Raises:
        TypeError: If ``root`` is not a :class:`~pathlib.Path`.
        ValueError: If ``root`` is relative; if ``pattern`` is empty or
            whitespace-only, is absolute, or contains a ``..`` component; or if
            an entry in ``exclude_patterns`` is a path rather than a bare name glob.
        NotADirectoryError: If ``root`` is not an existing directory.
    """
    _validate_root(root)

    if not pattern.strip():
        raise ValueError("pattern must be a non-empty string")

    _reject_unsafe_pattern(pattern)

    patterns = _extension_patterns(pattern, extensions)
    return _resolve_patterns(root, patterns, exclude_patterns)


def _validate_root(root: Path) -> None:
    """Require an explicit absolute directory rather than consulting the CWD."""
    if not isinstance(root, Path):
        raise TypeError(f"root must be a pathlib.Path, not {type(root).__name__}")
    if not root.is_absolute():
        raise ValueError(f"root must be absolute: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"root must be an existing directory: {root}")


def _reject_unsafe_pattern(pattern: str) -> None:
    """Reject a ``pattern`` that could lexically escape ``root``: an absolute
    path, or one with a ``..`` component."""
    candidate = Path(pattern)

    if candidate.is_absolute():
        raise ValueError(f"pattern must be relative, not absolute: {pattern!r}")
    if ".." in candidate.parts:
        raise ValueError(f"pattern must not contain '..' components: {pattern!r}")


def _extension_patterns(
    pattern: str,
    extensions: Iterable[str] | None,
) -> list[Path]:
    """Build the ``{pattern}.{ext}`` variants; see ``extensions`` in the caller."""
    if extensions is None:
        return [Path(f"{pattern}.{ANY_EXTENSION}")]

    suffixes = [ext.strip().lstrip(".") for ext in extensions]
    suffixes = [ext for ext in suffixes if ext]

    if not suffixes:
        return [Path(pattern)]

    return [Path(f"{pattern}.{ext}") for ext in suffixes]


def _resolve_patterns(
    root: Path,
    patterns: Iterable[Path],
    exclude_patterns: Iterable[str],
) -> list[Path]:
    """Glob ``patterns`` under ``root``, dropping every ``exclude_patterns`` hit."""
    excluded = _normalize_exclusions(exclude_patterns)
    matches: dict[Path, None] = {}

    for pattern in patterns:
        for match in sorted(root.glob(str(pattern))):
            if excluded and _is_excluded(match, root, excluded):
                continue
            matches.setdefault(match, None)

    return list(matches)


def _normalize_exclusions(exclude_patterns: Iterable[str]) -> _Exclusions:
    """Split the globs into directory/file sets, rejecting anything path-shaped."""
    directories: list[str] = []
    files: list[str] = []

    for entry in exclude_patterns:
        stripped = entry.strip()
        is_directory = stripped.startswith("/") or stripped.endswith("/")
        glob = stripped.strip("/")

        if not glob:
            continue
        if len(Path(glob).parts) > 1 or glob in (".", ".."):
            raise ValueError(f"exclude_patterns takes bare name globs, not paths: {entry!r}")

        (directories if is_directory else files).append(glob)

    return _Exclusions(tuple(directories), tuple(files))


def _is_excluded(match: Path, root: Path, excluded: _Exclusions) -> bool:
    """Report whether ``match`` hits a directory glob on its way down, or a file glob."""
    *ancestors, name = match.relative_to(root).parts

    if any(fnmatch(part, glob) for part in ancestors for glob in excluded.directories):
        return True

    globs = excluded.directories if match.is_dir() else excluded.files
    return any(fnmatch(name, glob) for glob in globs)
