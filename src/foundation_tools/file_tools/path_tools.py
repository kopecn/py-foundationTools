"""
Path and filename-pattern utilities.

Pure, stdlib-only helpers for constructing filename glob patterns. These functions
never touch the filesystem or a remote host — they only build the pattern strings
that a caller passes to a glob, ``ls``, or transport layer.
"""

from collections.abc import Iterable
from pathlib import Path
from typing import Final

__all__ = ["ANY_EXTENSION", "DEFAULT_EXTENSIONS", "expand_glob_patterns"]

#: Extensions applied when a caller does not specify any. Override per call site by
#: passing an explicit sequence; pass ``None`` to match any extension.
DEFAULT_EXTENSIONS: Final[tuple[str, ...]] = ("csv", "txt")

#: Extension wildcard substituted when a caller passes ``extensions=None``.
ANY_EXTENSION: Final[str] = "*"


def expand_glob_patterns(
    pattern: str,
    extensions: Iterable[str] | None = DEFAULT_EXTENSIONS,
) -> list[Path]:
    """
    Expand a base filename glob pattern across a set of extensions.

    Args:
        pattern: Base filename glob pattern including any wildcard
            (e.g. ``xyz.*waveform.*``).
        extensions: Extensions to append, with or without a leading dot
            (e.g. ``["txt", ".csv"]``). Blank entries are ignored. Defaults to
            :data:`DEFAULT_EXTENSIONS`. ``None`` matches any extension
            (``{pattern}.*``); an empty sequence expands nothing and returns
            the pattern unchanged.

    Returns:
        One :class:`~pathlib.Path` per extension, in input order, built as
        ``{pattern}.{ext}``; a single ``{pattern}.*`` when ``extensions`` is
        ``None``; or ``[Path(pattern)]`` when no extensions remain after
        normalization. The paths are relative patterns — they name nothing on
        disk until a caller anchors them to a directory.

    Raises:
        ValueError: If ``pattern`` is empty or whitespace-only.
    """
    if not pattern.strip():
        raise ValueError("pattern must be a non-empty string")

    if extensions is None:
        return [Path(f"{pattern}.{ANY_EXTENSION}")]

    suffixes = [ext.strip().lstrip(".") for ext in extensions]
    suffixes = [ext for ext in suffixes if ext]

    if not suffixes:
        return [Path(pattern)]

    return [Path(f"{pattern}.{ext}") for ext in suffixes]
