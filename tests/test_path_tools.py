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


# --- root-anchored globbing + exclusion pruning -------------------------------


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """A root holding a normal dir, a ``.build`` dir, and a dir nested inside it."""
    (tmp_path / "proj_a").mkdir()
    (tmp_path / ".build" / "proj_b").mkdir(parents=True)
    (tmp_path / "proj_c" / ".build" / "proj_d").mkdir(parents=True)
    (tmp_path / ".cache").mkdir()
    return tmp_path


def test_root_resolves_patterns_against_disk(tmp_path: Path) -> None:
    (tmp_path / "report_0001.csv").write_text("")
    (tmp_path / "report_0001.log").write_text("")
    assert expand_glob_patterns("report_*", ["csv"], root=tmp_path) == [
        tmp_path / "report_0001.csv"
    ]


def test_excluded_dir_itself_is_pruned(tree: Path) -> None:
    assert expand_glob_patterns("*", [], root=tree) == [
        tree / ".cache",
        tree / "proj_a",
        tree / "proj_c",
    ]


def test_paths_under_an_excluded_dir_are_pruned(tree: Path) -> None:
    assert expand_glob_patterns("*/*", [], root=tree) == []


def test_deeply_nested_excluded_dir_is_pruned(tree: Path) -> None:
    assert expand_glob_patterns("**/proj_d", [], root=tree) == []


def test_empty_exclusions_disable_pruning(tree: Path) -> None:
    assert expand_glob_patterns("*/*", [], root=tree, exclude_patterns=[]) == [
        tree / ".build" / "proj_b",
        tree / "proj_c" / ".build",
    ]


def test_exclusions_are_extensible(tree: Path) -> None:
    assert expand_glob_patterns(
        "*", [], root=tree, exclude_patterns=["/.build/", "/.cache/"]
    ) == [tree / "proj_a", tree / "proj_c"]


def test_blank_exclusions_are_ignored(tree: Path) -> None:
    assert expand_glob_patterns(
        "*", [], root=tree, exclude_patterns=["", "  ", "/", " /.build/ "]
    ) == [tree / ".cache", tree / "proj_a", tree / "proj_c"]


def test_matches_are_deduplicated_across_patterns(tmp_path: Path) -> None:
    (tmp_path / "report.csv").write_text("")
    assert expand_glob_patterns("report*", ["csv", "csv"], root=tmp_path) == [
        tmp_path / "report.csv"
    ]


def test_root_accepts_a_string(tree: Path) -> None:
    assert expand_glob_patterns("proj_a", [], root=str(tree)) == [tree / "proj_a"]


def test_no_root_stays_pure_and_ignores_exclusions(tree: Path) -> None:
    assert expand_glob_patterns("*", ["csv"], exclude_patterns=[]) == [Path("*.csv")]


def test_missing_root_raises(tmp_path: Path) -> None:
    with pytest.raises(NotADirectoryError):
        expand_glob_patterns("*", [], root=tmp_path / "nope")


@pytest.mark.parametrize("entry", ["a/.build", "/a/.build/", ".", "..", "/./"])
def test_exclude_patterns_rejects_paths(tree: Path, entry: str) -> None:
    with pytest.raises(ValueError):
        expand_glob_patterns("*", [], root=tree, exclude_patterns=[entry])


# --- directory vs file exclusion syntax ---------------------------------------


@pytest.fixture
def mixed(tmp_path: Path) -> Path:
    """A root where the same name exists both as a directory and as a file."""
    (tmp_path / "xyzxyz" / "nested").mkdir(parents=True)
    (tmp_path / "xyzxyz.txt").write_text("")
    (tmp_path / "keep").mkdir()
    (tmp_path / "keep" / "mod.pyc").write_text("")
    (tmp_path / "keep" / "mod.py").write_text("")
    return tmp_path


@pytest.mark.parametrize("entry", ["/xyz*", "*xyz/", "/xyz*xyz/", "/xyzxyz/"])
def test_leading_or_trailing_slash_marks_a_directory(mixed: Path, entry: str) -> None:
    """All four slash forms prune the directory and leave the same-named file."""
    assert expand_glob_patterns("xyz*", [], root=mixed, exclude_patterns=[entry]) == [
        mixed / "xyzxyz.txt"
    ]


def test_directory_glob_prunes_the_whole_subtree(mixed: Path) -> None:
    assert (
        expand_glob_patterns("*/*", [], root=mixed, exclude_patterns=["/xyz*"])
        == [mixed / "keep" / "mod.py", mixed / "keep" / "mod.pyc"]
    )


def test_unslashed_glob_matches_files_only(mixed: Path) -> None:
    """``xyz*`` without slashes drops the file and leaves the directory."""
    assert expand_glob_patterns("xyz*", [], root=mixed, exclude_patterns=["xyz*"]) == [
        mixed / "xyzxyz"
    ]


def test_file_glob_applies_at_any_depth(mixed: Path) -> None:
    assert expand_glob_patterns(
        "keep/*", [], root=mixed, exclude_patterns=["*.pyc"]
    ) == [mixed / "keep" / "mod.py"]


def test_file_glob_does_not_prune_a_subtree(mixed: Path) -> None:
    """A file glob matching a directory name leaves that directory alone."""
    assert expand_glob_patterns(
        "xyzxyz/*", [], root=mixed, exclude_patterns=["xyzxyz"]
    ) == [mixed / "xyzxyz" / "nested"]


def test_directory_and_file_globs_combine(mixed: Path) -> None:
    assert expand_glob_patterns(
        "**/*", [], root=mixed, exclude_patterns=["/xyz*/", "*.pyc"]
    ) == [mixed / "keep", mixed / "keep" / "mod.py", mixed / "xyzxyz.txt"]
