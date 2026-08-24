---
plan: Fix05PathRootContainment
scope: project
status: pending
last_updated: 2026-08-23
semver: 0.0.1
author: Nicholas Bergantz
---

# Fix 05 — Path Root Containment

## Goal

Guarantee that `expand_glob_patterns(..., root=...)` cannot return a lexical path
outside the declared root.

## Depends on

Fix 04 only in preferred landing order. There is no code dependency.

## Defect

A pattern such as `../outside` is passed directly to `Path.glob`. With exclusions
disabled—or even with an unrelated exclusion configured—the helper can return
`root/../outside.txt`, contradicting its documented promise to return paths under
`root`.

## Files

Edit:

- `src/foundation_tools/file_tools/path_tools.py`
- `tests/test_path_tools.py`
- `HISTORY.md`

## Design constraints

**Validate lexical pattern scope before globbing.** Reject:

- absolute patterns;
- any pattern component equal to `..`.

Raise `ValueError` naming the rejected pattern. Wildcards, nested relative directories,
and recursive `**` remain valid.

**Apply the documented relative-pattern contract consistently.** Validation should
also protect the pure `root=None` mode, whose return contract says it produces relative
patterns. Do not preserve undocumented absolute/parent traversal merely because no I/O
occurs in that mode.

**Do not resolve matched symlinks.** This fix is lexical root containment. Changing
whether an explicitly matched symlink may point elsewhere is a separate filesystem
policy with compatibility consequences.

**Keep exclusion semantics unchanged.** Directory/file exclusion classification and
match ordering are not part of this fix.

## Steps (TDD)

1. Add pure-mode and rooted tests for `../outside`, nested `a/../../outside`, and an
   absolute pattern. Assert `ValueError` before any match is returned.
2. Add regression tests proving `subdir/*.csv` and `**/*` still work.
3. Implement a small pattern-scope validator called before `_extension_patterns`.
4. Update the public docstring's `Raises` section.
5. Add an `[Unreleased]` `Fixed` bullet.
6. Run `tests/test_path_tools.py`, then `make uv-fullCheck`.

## Acceptance criteria

- [ ] Parent traversal is rejected in pure and rooted modes.
- [ ] Absolute patterns are rejected in pure and rooted modes.
- [ ] Every rooted result is lexically beneath `root`.
- [ ] Valid nested and recursive patterns retain ordering, deduplication, and pruning.
- [ ] No filesystem access occurs when `root=None`.
- [ ] `make uv-fullCheck` passes.

## Out of scope

- Following or forbidding symlinks.
- Case-normalization across filesystems.
- Replacing `pathlib` glob semantics.
- Changing extension normalization or exclusion syntax.

