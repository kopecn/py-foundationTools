---
plan: Fix05PathRootContainment
scope: project
status: complete
last_updated: 2026-09-04
semver: 1.0.0
author: Nicholas Bergantz
---

# Fix candidate 05 — lexical path containment

Evidence: absolute patterns and patterns containing a `..` component can escape the
declared `root` in `expand_glob_patterns`.

Minimum fix: reject those pattern shapes before expansion in both rooted and pure
modes; test valid nested and recursive patterns remain unchanged.

This is lexical containment only. Do not change symlink policy, glob semantics,
extension handling, or exclusions.

## Ask ↔ result

- **Objective:** reject glob patterns that can lexically escape `root` (absolute, or containing `..`).
- **Authorized by:** `/execute-plan please proceed` (user approved all of fix-01–07).
- **Delivered:** `_reject_unsafe_pattern` raises `ValueError` (module convention) for absolute patterns and any `..` component, called before expansion so both pure and rooted modes reject identically. 14 tests in `tests/test_path_tools.py` (10 rejection across both modes, 4 acceptance for nested + `**` recursive), confirmed failing pre-fix.
- **Gate:** `make uv-fullCheck` — ruff/mypy clean, 516 passed.
- **Gap:** none. Symlink policy, glob semantics, extensions, and exclusions untouched.
