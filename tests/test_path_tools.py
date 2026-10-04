"""Tests for foundation_tools.file_tools.path_tools.

Covers the current implementation: a single recursive walk under ``starting_dir``
followed by four independent, opt-in filters (pattern, extensions, exclusions,
hidden), plus the threaded progress indicator. Results are returned in glob order,
so every assertion compares sorted relative paths rather than raw order.
"""

import sys
from pathlib import Path

import pytest

from foundation_tools.file_tools import find_matching_paths
from foundation_tools.file_tools.path_tools import (
    SuggestedExcludePatterns,
    SuggestedExtensions,
    SuggestedPatterns,
)


def rels(results: list[Path], root: Path) -> list[str]:
    """Sorted, ``root``-relative POSIX strings for order-independent comparison."""
    base = root.resolve()
    return sorted(p.relative_to(base).as_posix() for p in results)


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """A root with files, a nested dir, and a hidden dir/file."""
    (tmp_path / "a.csv").write_text("")
    (tmp_path / "a.txt").write_text("")
    (tmp_path / "a.log").write_text("")
    (tmp_path / "README").write_text("")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.csv").write_text("")
    (tmp_path / ".hidden").mkdir()
    (tmp_path / ".hidden" / "h.csv").write_text("")
    (tmp_path / ".dotfile").write_text("")
    return tmp_path


# --- defaults / recursion -----------------------------------------------------


def test_no_arguments_returns_every_visible_entry(tree: Path) -> None:
    assert rels(find_matching_paths(tree), tree) == [
        "README",
        "a.csv",
        "a.log",
        "a.txt",
        "sub",
        "sub/b.csv",
    ]


def test_walk_is_recursive(tree: Path) -> None:
    assert "sub/b.csv" in rels(find_matching_paths(tree), tree)


def test_starting_dir_none_defaults_to_executable_dir() -> None:
    here = Path(sys.executable).parent
    assert find_matching_paths(None, indicator=False) == find_matching_paths(here, indicator=False)


# --- hidden entries -----------------------------------------------------------


def test_hidden_entries_are_never_returned(tree: Path) -> None:
    # The walk itself omits dot-prefixed entries, so hidden files/dirs never appear.
    result = rels(find_matching_paths(tree), tree)
    assert ".hidden" not in result
    assert ".hidden/h.csv" not in result
    assert ".dotfile" not in result


def test_return_hidden_false_is_a_noop(tree: Path) -> None:
    # Hidden entries are already absent, so the flag changes nothing observable.
    assert rels(find_matching_paths(tree, return_hidden=False), tree) == rels(
        find_matching_paths(tree, return_hidden=True), tree
    )


# --- pattern ------------------------------------------------------------------


def test_pattern_none_keeps_everything(tree: Path) -> None:
    assert rels(find_matching_paths(tree, None), tree) == rels(find_matching_paths(tree), tree)


def test_pattern_matches_extension_at_any_depth(tree: Path) -> None:
    assert rels(find_matching_paths(tree, "*.csv"), tree) == ["a.csv", "sub/b.csv"]


def test_pattern_matches_bare_name(tree: Path) -> None:
    assert rels(find_matching_paths(tree, "a.*"), tree) == ["a.csv", "a.log", "a.txt"]


def test_pattern_matches_exact_name(tree: Path) -> None:
    assert rels(find_matching_paths(tree, "sub"), tree) == ["sub"]


# --- extensions ---------------------------------------------------------------


def test_extensions_keep_matching_files_and_drop_directories(tree: Path) -> None:
    assert rels(find_matching_paths(tree, None, ["csv"]), tree) == ["a.csv", "sub/b.csv"]


def test_extensions_dotted_and_bare_are_equivalent(tree: Path) -> None:
    assert rels(find_matching_paths(tree, None, [".csv", "txt"]), tree) == [
        "a.csv",
        "a.txt",
        "sub/b.csv",
    ]


def test_none_extensions_apply_no_filter(tree: Path) -> None:
    everything = rels(find_matching_paths(tree), tree)
    assert rels(find_matching_paths(tree, None, None), tree) == everything


def test_empty_extensions_apply_no_filter(tree: Path) -> None:
    assert rels(find_matching_paths(tree, None, []), tree) == rels(find_matching_paths(tree), tree)


def test_extensions_accepts_any_iterable(tree: Path) -> None:
    gen = (ext for ext in ("csv",))
    assert rels(find_matching_paths(tree, None, gen), tree) == ["a.csv", "sub/b.csv"]


# --- exclude_patterns ---------------------------------------------------------


def test_exclude_file_glob(tree: Path) -> None:
    assert "a.log" not in rels(find_matching_paths(tree, None, None, ["*.log"]), tree)


def test_exclude_directory_subtree(tree: Path) -> None:
    result = rels(find_matching_paths(tree, None, None, ["/sub/*"]), tree)
    assert "sub/b.csv" not in result
    assert "sub" not in result


def test_exclude_directory_entry_keeps_its_children(tree: Path) -> None:
    # A trailing-slash dir glob drops the directory entry only, not its subtree.
    result = rels(find_matching_paths(tree, None, None, ["/sub/"]), tree)
    assert "sub" not in result
    assert "sub/b.csv" in result


def test_none_exclusions_drop_nothing(tree: Path) -> None:
    assert rels(find_matching_paths(tree, None, None, None), tree) == rels(
        find_matching_paths(tree), tree
    )


# --- results ------------------------------------------------------------------


def test_results_are_absolute_paths(tree: Path) -> None:
    assert all(p.is_absolute() for p in find_matching_paths(tree))


# --- indicator / threading ----------------------------------------------------


def test_indicator_true_and_false_return_identical_results(tree: Path) -> None:
    assert rels(find_matching_paths(tree, indicator=True), tree) == rels(
        find_matching_paths(tree, indicator=False), tree
    )


def test_indicator_writes_nothing_when_not_a_tty(
    tree: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    result = find_matching_paths(tree, indicator=True)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
    assert result  # work still happened


def test_join_timeout_is_optional_and_does_not_change_results(tree: Path) -> None:
    baseline = rels(find_matching_paths(tree, indicator=False), tree)
    assert rels(find_matching_paths(tree, join_timeout=None), tree) == baseline
    assert rels(find_matching_paths(tree, join_timeout=1.0), tree) == baseline
    assert rels(find_matching_paths(tree, join_timeout=0.0), tree) == baseline


# --- suggestion enums ---------------------------------------------------------


def test_suggested_patterns_values() -> None:
    assert SuggestedPatterns.ANY.value == "*"
    assert SuggestedPatterns.ANY_RECURSIVE.value == "**/*"


def test_suggested_extensions_tabular_filters_to_csv_and_txt(tree: Path) -> None:
    assert rels(find_matching_paths(tree, None, SuggestedExtensions.TABULAR.value), tree) == [
        "a.csv",
        "a.txt",
        "sub/b.csv",
    ]


def test_suggested_extensions_any_matches_nothing(tree: Path) -> None:
    # ("*",) normalizes to the suffix ".*", which no real file has.
    assert find_matching_paths(tree, None, SuggestedExtensions.ANY.value) == []


def test_suggested_exclude_patterns_value() -> None:
    assert SuggestedExcludePatterns.BUILD.value == ("/.build/",)
