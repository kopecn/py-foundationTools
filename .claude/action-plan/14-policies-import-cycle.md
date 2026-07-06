---
plan: ActionPlan14PoliciesImportCycle
scope: project
status: pending
last_updated: 2026-07-06
semver: 0.1.0
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

- [ ] `python -c "from foundation_tools.policies import RetryPolicy"` succeeds in
      a fresh interpreter (proven by the new test, not manual verification).
- [ ] All internal-but-importable subpackages import cleanly first
      (`policies`, `builders`, `socket_transaction`).
- [ ] No behavior change to `RetryPolicy` itself — existing `test_policies.py`
      matrix passes untouched.
- [ ] `make uv-fullCheck` passes.

## Out of scope

- Restructuring `cli_transaction/__init__.py` exports.
- Any change to retry/backoff behavior.
