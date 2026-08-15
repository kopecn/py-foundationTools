"""
Path and filename-pattern utilities.

:func:`expand_glob_patterns` is the public entry point. Called without ``root`` it
never touches the filesystem — it only builds the pattern strings that a caller
passes to a glob, ``ls``, or transport layer. Called *with* ``root`` it resolves
those patterns against disk and prunes matches that hit an exclusion pattern
(``/.build/`` by default).
"""

from collections.abc import Iterable
from fnmatch import fnmatch
from pathlib import Path
from typing import Final, NamedTuple

__all__ = [
    "ANY_EXTENSION",
    "DEFAULT_EXCLUDED_PATTERNS",
    "DEFAULT_EXTENSIONS",
    "expand_glob_patterns",
]

#: Extensions applied when a caller does not specify any. Override per call site by
#: passing an explicit sequence; pass ``None`` to match any extension.
DEFAULT_EXTENSIONS: Final[tuple[str, ...]] = ("csv", "txt")

#: Extension wildcard substituted when a caller passes ``extensions=None``.
ANY_EXTENSION: Final[str] = "*"

#: Name globs never returned when globbing against a ``root``. A leading and/or
#: trailing ``/`` marks the entry as a *directory* glob (``/.build/``, ``/build*``,
#: ``*cache/``), which prunes the whole subtree; an entry with no slash is a *file*
#: glob (``*.pyc``). Pass an explicit sequence to extend it or ``[]`` to disable
#: pruning entirely.
DEFAULT_EXCLUDED_PATTERNS: Final[tuple[str, ...]] = ("/.build/",)


class _Exclusions(NamedTuple):
    """Exclusion globs split by what they match, with the ``/`` markers stripped."""

    directories: tuple[str, ...]
    files: tuple[str, ...]

    def __bool__(self) -> bool:
        return bool(self.directories or self.files)


def expand_glob_patterns(
    pattern: str,
    extensions: Iterable[str] | None = DEFAULT_EXTENSIONS,
    *,
    root: Path | str | None = None,
    exclude_patterns: Iterable[str] = DEFAULT_EXCLUDED_PATTERNS,
) -> list[Path]:
    """
    Expand a base filename glob pattern across a set of extensions.

    Args:
        pattern: Base filename glob pattern including any wildcard
            (e.g. ``xyz.*waveform.*``).
        extensions: Extensions to append, with or without a leading dot
            (e.g. ``["txt", ".csv"]``). Blank entries are ignored. Defaults to
            :data:`DEFAULT_EXTENSIONS`. ``None`` matches any extension
            (``{pattern}.*``); an empty sequence expands nothing and uses
            the pattern unchanged.
        root: Directory to resolve the patterns against. ``None`` (the default)
            keeps the call pure — the patterns are returned unresolved and
            ``exclude_patterns`` is not consulted.
        exclude_patterns: Name globs (never paths) to prune when ``root`` is
            given. A leading and/or trailing ``/`` marks a **directory** glob —
            ``/.build/``, ``/build*``, ``*cache/``, ``/xyz*xyz/`` are all
            equivalent in effect — which matches any directory between ``root``
            and the match, so the whole subtree is pruned and never dug through.
            An entry with no slash is a **file** glob (``*.pyc``) and is matched
            only against the final component, and only when that component is
            not a directory. Defaults to :data:`DEFAULT_EXCLUDED_PATTERNS`; pass
            ``[]`` to disable pruning.

    Returns:
        Without ``root``: one relative :class:`~pathlib.Path` pattern per
        extension, in input order, built as ``{pattern}.{ext}``; a single
        ``{pattern}.*`` when ``extensions`` is ``None``; or ``[Path(pattern)]``
        when no extensions remain after normalization. The paths are relative
        patterns — they name nothing on disk until a caller anchors them.

        With ``root``: the paths under ``root`` that those patterns match,
        sorted within each pattern and de-duplicated across patterns, with
        every ``exclude_patterns`` hit pruned.

    Raises:
        ValueError: If ``pattern`` is empty or whitespace-only, or if an entry in
            ``exclude_patterns`` is a path rather than a bare name glob.
        NotADirectoryError: If ``root`` is given and is not an existing directory.
    """
    if not pattern.strip():
        raise ValueError("pattern must be a non-empty string")

    patterns = _extension_patterns(pattern, extensions)

    if root is None:
        return patterns

    return _resolve_patterns(Path(root), patterns, exclude_patterns)


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
    if not root.is_dir():
        raise NotADirectoryError(f"root must be an existing directory: {root}")

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
            raise ValueError(
                f"exclude_patterns takes bare name globs, not paths: {entry!r}"
            )

        (directories if is_directory else files).append(glob)

    return _Exclusions(tuple(directories), tuple(files))


def _is_excluded(match: Path, root: Path, excluded: _Exclusions) -> bool:
    """Report whether ``match`` hits a directory glob on its way down, or a file glob."""
    *ancestors, name = match.relative_to(root).parts

    if any(fnmatch(part, glob) for part in ancestors for glob in excluded.directories):
        return True

    globs = excluded.directories if match.is_dir() else excluded.files
    return any(fnmatch(name, glob) for glob in globs)
