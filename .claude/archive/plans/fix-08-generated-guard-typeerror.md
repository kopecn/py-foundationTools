---
plan: Fix08GeneratedGuardTypeError
scope: project
status: complete
last_updated: 2026-08-28
semver: 1.0.0
author: Nicholas Bergantz
---

# Fix 08 — generated dictionary guards (completed record)

Commit `1a768d3` changed generated `from_dict` guards from bare assertions to explicit
`TypeError` checks through the shared normalizer. This preserves validation under
`python -O` and lets optional nested models fall through `from_union` correctly.

The lasting constraints are:

- the rewrite belongs in `schema/scripts/reuse/normalize_generated.sh`;
- generated modules are regenerated, never hand-edited;
- use `obj.__class__.__name__` in the generated message because a schema field named
  `type` can shadow the builtin;
- do not broaden `from_union` to catch `AssertionError`.

No further work is authorized by this completed plan.
