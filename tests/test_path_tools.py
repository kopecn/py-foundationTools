"""Tests for foundation_tools.file_tools.path_tools."""

from inspect import Parameter, signature
from pathlib import Path
from typing import Any, cast

import pytest

from foundation_tools.file_tools import DEFAULT_EXTENSIONS, find_matching_paths


def test_root_is_required() -> None:
    assert signature(find_matching_paths).parameters["root"].default is Parameter.empty


def test_omitted_extensions_uses_default_set(tmp_path: Path) -> None:
    matches = [tmp_path / f"report_0001.{ext}" for ext in DEFAULT_EXTENSIONS]
    for match in matches:
        match.write_text("")

    assert find_matching_paths(tmp_path, "report_0001") == matches


def test_extensions_are_applied_in_order(tmp_path: Path) -> None:
    txt = tmp_path / "report_0001.txt"
    csv = tmp_path / "report_0001.csv"
    txt.write_text("")
    csv.write_text("")

    assert find_matching_paths(tmp_path, "report_0001", ["txt", "csv"]) == [txt, csv]


def test_leading_dots_are_normalized(tmp_path: Path) -> None:
    txt = tmp_path / "report.txt"
    csv = tmp_path / "report.csv"
    txt.write_text("")
    csv.write_text("")

    assert find_matching_paths(tmp_path, "report", [".txt", " .csv "]) == [txt, csv]


def test_blank_extensions_are_ignored(tmp_path: Path) -> None:
    match = tmp_path / "report.txt"
    match.write_text("")

    assert find_matching_paths(tmp_path, "report", ["txt", "", "  ", "."]) == [match]


def test_empty_extension_sequence_uses_pattern_unchanged(tmp_path: Path) -> None:
    matches = [tmp_path / "report", tmp_path / "report.csv"]
    for match in matches:
        match.write_text("")

    assert find_matching_paths(tmp_path, "report*", []) == matches


def test_none_matches_any_extension(tmp_path: Path) -> None:
    matches = [tmp_path / "report.csv", tmp_path / "report.log"]
    for match in matches:
        match.write_text("")

    assert find_matching_paths(tmp_path, "report", None) == matches


def test_accepts_any_extension_iterable(tmp_path: Path) -> None:
    match = tmp_path / "report.txt"
    match.write_text("")

    assert find_matching_paths(tmp_path, "report", (ext for ext in ("txt",))) == [match]


def test_results_are_absolute_paths(tmp_path: Path) -> None:
    match = tmp_path / "report.txt"
    match.write_text("")

    results = find_matching_paths(tmp_path, "report", ["txt"])

    assert results == [match]
    assert all(result.is_absolute() for result in results)


@pytest.mark.parametrize("pattern", ["", "   "])
def test_empty_pattern_raises(tmp_path: Path, pattern: str) -> None:
    with pytest.raises(ValueError):
        find_matching_paths(tmp_path, pattern)


# --- lexical root containment --------------------------------------------------


@pytest.mark.parametrize("pattern", ["/etc/passwd*", "/absolute/report*"])
def test_absolute_pattern_rejected(tmp_path: Path, pattern: str) -> None:
    with pytest.raises(ValueError):
        find_matching_paths(tmp_path, pattern, [])


@pytest.mark.parametrize("pattern", ["../report*", "sub/../report*", "../../etc/passwd*"])
def test_dotdot_pattern_rejected(tmp_path: Path, pattern: str) -> None:
    with pytest.raises(ValueError):
        find_matching_paths(tmp_path, pattern, [])


def test_nested_relative_pattern_still_accepted(tmp_path: Path) -> None:
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "report_0001.csv").write_text("")
    assert find_matching_paths(tmp_path, "sub/report_*", ["csv"]) == [
        tmp_path / "sub" / "report_0001.csv"
    ]


def test_recursive_glob_pattern_still_accepted(tree: Path) -> None:
    assert find_matching_paths(tree, "**/proj_d", []) == []


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
    assert find_matching_paths(tmp_path, "report_*", ["csv"]) == [tmp_path / "report_0001.csv"]


def test_excluded_dir_itself_is_pruned(tree: Path) -> None:
    assert find_matching_paths(tree, "*", []) == [
        tree / ".cache",
        tree / "proj_a",
        tree / "proj_c",
    ]


def test_paths_under_an_excluded_dir_are_pruned(tree: Path) -> None:
    assert find_matching_paths(tree, "*/*", []) == []


def test_deeply_nested_excluded_dir_is_pruned(tree: Path) -> None:
    assert find_matching_paths(tree, "**/proj_d", []) == []


def test_empty_exclusions_disable_pruning(tree: Path) -> None:
    assert find_matching_paths(tree, "*/*", [], exclude_patterns=[]) == [
        tree / ".build" / "proj_b",
        tree / "proj_c" / ".build",
    ]


def test_exclusions_are_extensible(tree: Path) -> None:
    assert find_matching_paths(tree, "*", [], exclude_patterns=["/.build/", "/.cache/"]) == [
        tree / "proj_a",
        tree / "proj_c",
    ]


def test_blank_exclusions_are_ignored(tree: Path) -> None:
    assert find_matching_paths(tree, "*", [], exclude_patterns=["", "  ", "/", " /.build/ "]) == [
        tree / ".cache",
        tree / "proj_a",
        tree / "proj_c",
    ]


def test_matches_are_deduplicated_across_patterns(tmp_path: Path) -> None:
    (tmp_path / "report.csv").write_text("")
    assert find_matching_paths(tmp_path, "report*", ["csv", "csv"]) == [tmp_path / "report.csv"]


def test_root_rejects_a_string(tree: Path) -> None:
    with pytest.raises(TypeError, match="root must be a pathlib.Path"):
        find_matching_paths(cast(Any, str(tree)), "proj_a", [])


def test_relative_root_raises() -> None:
    with pytest.raises(ValueError, match="root must be absolute"):
        find_matching_paths(Path("relative-root"), "*", [])


def test_missing_root_raises(tmp_path: Path) -> None:
    with pytest.raises(NotADirectoryError):
        find_matching_paths(tmp_path / "nope", "*", [])


@pytest.mark.parametrize("entry", ["a/.build", "/a/.build/", ".", "..", "/./"])
def test_exclude_patterns_rejects_paths(tree: Path, entry: str) -> None:
    with pytest.raises(ValueError):
        find_matching_paths(tree, "*", [], exclude_patterns=[entry])


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
    assert find_matching_paths(mixed, "xyz*", [], exclude_patterns=[entry]) == [
        mixed / "xyzxyz.txt"
    ]


def test_directory_glob_prunes_the_whole_subtree(mixed: Path) -> None:
    assert find_matching_paths(mixed, "*/*", [], exclude_patterns=["/xyz*"]) == [
        mixed / "keep" / "mod.py",
        mixed / "keep" / "mod.pyc",
    ]


def test_unslashed_glob_matches_files_only(mixed: Path) -> None:
    """``xyz*`` without slashes drops the file and leaves the directory."""
    assert find_matching_paths(mixed, "xyz*", [], exclude_patterns=["xyz*"]) == [mixed / "xyzxyz"]


def test_file_glob_applies_at_any_depth(mixed: Path) -> None:
    assert find_matching_paths(mixed, "keep/*", [], exclude_patterns=["*.pyc"]) == [
        mixed / "keep" / "mod.py"
    ]


def test_file_glob_does_not_prune_a_subtree(mixed: Path) -> None:
    """A file glob matching a directory name leaves that directory alone."""
    assert find_matching_paths(mixed, "xyzxyz/*", [], exclude_patterns=["xyzxyz"]) == [
        mixed / "xyzxyz" / "nested"
    ]


def test_directory_and_file_globs_combine(mixed: Path) -> None:
    assert find_matching_paths(mixed, "**/*", [], exclude_patterns=["/xyz*/", "*.pyc"]) == [
        mixed / "keep",
        mixed / "keep" / "mod.py",
        mixed / "xyzxyz.txt",
    ]
