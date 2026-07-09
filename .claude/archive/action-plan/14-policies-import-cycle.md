---
plan: ActionPlan14PoliciesImportCycle
scope: project
status: complete
last_updated: 2026-07-06
semver: 0.2.0
author: Nicholas Bergantz
---

# 14 — Policy-Layer Import Cycle (corrective)

## Goal

Fix the circular import that breaks the policy layer's public surface.
`retry_policy.py` imports `CLITransactResult` from the **package**
`foundation_tools.cli_transaction`, whose `__init__` imports
`sshTransact`/`rsyncTransact`, which import back into
`foundation_tools.policies` — a cycle. Confirmed at runtime:

```
from foundation_tools.policies import RetryPolicy   # as first import
ImportError: cannot import name 'RetryPolicy' from partially initialized module
```

This violates the internal-but-importable rule of
[transport_transaction_architecture.md](../specs/transport_transaction_architecture.md)
(builders/policies/codecs must be available for composition by advanced users).
The existing suite masks the defect because `tests/test_policies.py` imports
`foundation_tools.cli_transaction` before `foundation_tools.policies`.

## Origin

Chunk 03 audit finding (corrective follow-up to plans 00–13).

## Depends on

None — independent.

## Files

- `src/foundation_tools/policies/retry_policy.py` (fix the import)
- `tests/test_policies.py` (import-health regression test)

## Design constraints

- Fix by importing the type from the **submodule**, not the package:
  `from foundation_tools.cli_transaction.cliTransact import CLITransactResult`.
  No architectural change; the layer dependency direction (transactions → policies)
  stays as specified.
- The regression test MUST run in a **fresh interpreter**
  (`subprocess.run([sys.executable, "-c", ...])`) so in-suite import order can
  never mask a cycle again. Assert exit code 0 for
  `from foundation_tools.policies import RetryPolicy` as the first import, and
  likewise for `foundation_tools.builders` and
  `foundation_tools.socket_transaction` (cheap to sweep all internal-but-importable
  layers while here).
- No spec contract change; `cliTransact.md` does not record import topology, so no
  spec edit is expected.

## Steps (TDD)

1. Write the failing fresh-interpreter import-health test (fails against the
   current cycle).
2. Fix the import in `retry_policy.py`.
3. `make uv-fullCheck`.

## Acceptance criteria

- [x] `python -c "from foundation_tools.policies import RetryPolicy"` succeeds in
      a fresh interpreter (proven by the new test, not manual verification).
- [x] All internal-but-importable subpackages import cleanly first
      (`policies`, `builders`, `socket_transaction`).
- [x] No behavior change to `RetryPolicy` itself — existing `test_policies.py`
      matrix passes untouched.
- [x] `make uv-fullCheck` passes.

## Out of scope

- Restructuring `cli_transaction/__init__.py` exports.
- Any change to retry/backoff behavior.

## Resolution notes

The literal design constraint ("import `CLITransactResult` from the submodule
`foundation_tools.cli_transaction.cliTransact` instead of the package") was tried
first and verified **not** to break the cycle: importing a submodule that has
never been imported still executes the parent package's `__init__.py` in full
before the submodule import completes. That `__init__.py` unconditionally pulls
in `rsyncTransact`, which imports `foundation_tools.policies.retry_policy` at
module level — landing back on the same partially-initialized module regardless
of whether the failing import in `retry_policy.py` names the package or the
submodule. Confirmed empirically: the new fresh-interpreter test failed with the
identical traceback before and after the literal one-line change.

`CLITransactResult` is used in `retry_policy.py` only as a `TypeVar` bound
(`R = TypeVar("R", bound=CLITransactResult)`) — never referenced at runtime
otherwise. The actual fix (still confined to `retry_policy.py`, still no change
to `cli_transaction/__init__.py` or to any other file): move the import under
`if TYPE_CHECKING:` and change the bound to the string form
`TypeVar("R", bound="CLITransactResult")`. This is resolved lazily by mypy/ty
(both pass) but performs no runtime import at all, so `foundation_tools.policies`
never touches `foundation_tools.cli_transaction` at import time and the cycle
cannot occur in either import order. This preserves every constraint in the
chunk — no export restructuring, no retry/backoff behavior change, single file
touched — while actually satisfying the acceptance criteria the literal fix did
not.

Swept `builders` and `socket_transaction` per the design constraint; both already
imported cleanly first (no cycle found there), so the new test parametrization
for them is a regression guard, not a second fix.

Gate: `make uv-fullCheck` (ruff lint + mypy + 291 pytest) passes. Note
`uv-fullCheck` intentionally excludes `ty` (Makefile decision D1, pre-existing,
unrelated to this chunk).
