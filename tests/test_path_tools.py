"""Tests for foundation_tools.file_tools.path_tools."""

from pathlib import Path

import pytest

from foundation_tools.file_tools import DEFAULT_EXTENSIONS, expand_glob_patterns


def test_omitted_extensions_uses_default_set() -> None:
    assert expand_glob_patterns("report_0001*") == [
        Path(f"report_0001*.{ext}") for ext in DEFAULT_EXTENSIONS
    ]


def test_extensions_are_appended_in_order() -> None:
    assert expand_glob_patterns("report_0001*", ["txt", "csv"]) == [
        Path("report_0001*.txt"),
        Path("report_0001*.csv"),
    ]


def test_leading_dots_are_normalized() -> None:
    assert expand_glob_patterns("report*", [".txt", " .csv "]) == [
        Path("report*.txt"),
        Path("report*.csv"),
    ]


def test_blank_extensions_are_ignored() -> None:
    assert expand_glob_patterns("report*", ["txt", "", "  ", "."]) == [
        Path("report*.txt")
    ]


def test_empty_extension_sequence_returns_pattern_unchanged() -> None:
    assert expand_glob_patterns("report*", []) == [Path("report*")]


def test_none_matches_any_extension() -> None:
    assert expand_glob_patterns("report*", None) == [Path("report*.*")]


def test_never_produces_a_recursive_glob_token() -> None:
    """``**`` is rejected by Path.glob on Python < 3.13; never emit it."""
    results = expand_glob_patterns("report*", None) + expand_glob_patterns("report*")
    assert all("**" not in str(p) for p in results)


def test_accepts_any_iterable() -> None:
    assert expand_glob_patterns("report*", (ext for ext in ("txt",))) == [
        Path("report*.txt")
    ]


def test_results_are_relative_patterns() -> None:
    results = expand_glob_patterns("report*", ["txt"])
    assert all(not p.is_absolute() for p in results)
    assert results[0].name == "report*.txt"


@pytest.mark.parametrize("pattern", ["", "   "])
def test_empty_pattern_raises(pattern: str) -> None:
    with pytest.raises(ValueError):
        expand_glob_patterns(pattern)
