---
plan: Fix05PathRootContainment
scope: project
status: needs-approval
last_updated: 2026-08-28
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
