---
plan: ActionPlan03ExecutionPolicies
scope: project
status: pending
last_updated: 2026-07-03
semver: 0.0.2
author: Nicholas Bergantz
---

# 03 — Execution Policies

## Goal

Implement the composable policy layer: `RetryPolicy` + `BackoffPolicy`. Policies
decorate kernel execution; they never build commands and never touch subprocess.

Contract: Layer 3 of
[transport_transaction_architecture.md](../specs/transport_transaction_architecture.md)
(+ the retry/backoff section of [cliTransact.md](../specs/cliTransact.md)).

## Depends on

02 (hardened kernel).

## Files

- `src/foundation_tools/policies/backoff_policy.py`
- `src/foundation_tools/policies/retry_policy.py`
- `src/foundation_tools/policies/__init__.py` (exports)
- `tests/test_policies.py`

## Design constraints

- `BackoffPolicy`: `delay = min(max_delay, base_delay * 2 ** attempt)`, optional
  full jitter `delay = random(0, delay)`. Pure delay computation — no sleeping.
- `RetryPolicy`: owns attempt count, transient-code classification, termination
  (success / non-transient failure / attempts exhausted). Sleeps between attempts
  via injected sleeper (default `time.sleep` / `asyncio.sleep`) so tests run
  instantly.
- Transient return codes are **data, not hard-code**: the policy takes a
  `transient_return_codes: frozenset[int]` parameter. The rsync recommendation
  `{10, 12, 30, 35, -1}` (and non-retryable `{2, 4, 23, 24}`) lives in
  [rsyncTransact.md](../specs/rsyncTransact.md) and is applied by chunk 07, not
  baked in here.
- Policy applies to a `Callable[[], CLITransactResult]` (sync) and
  `Callable[[], Awaitable[CLITransactResult]]` (async) — it wraps *execution*, so it
  works unchanged for any transport transaction.
- **Timeout is per-attempt** (canonical rule in
  [transport_transaction_architecture.md](../specs/transport_transaction_architecture.md)):
  the caller's `timeout` governs each attempt; the policy adds no overall deadline.
  Worst-case wall time ≈ `attempts × timeout` + sum of backoff delays.
- **Policies wrap the whole call**: for `run_*_with_model` the policy wraps the full
  callable (execution + parse). Retry classification reads only `return_code`; a
  parser failure never changes `success` and never triggers a retry — parsing runs
  at most once, on the terminal attempt.
- Stateless invocation: policy objects are immutable config; per-run state stays
  local to the call.

## Steps (TDD)

1. Tests first: backoff sequence exactness (incl. cap, jitter bounds), retry stops
   on success, retries only transient codes, exhaustion returns the last result
   (never raises), async parity, zero-sleep injection, and: a `with_model` result
   with `return_code == 0` but a failed parse is terminal success — never retried.
2. Implement `BackoffPolicy`, then `RetryPolicy`.
3. `make fullCheck`.

## Acceptance criteria

- [ ] Policies never import subprocess/asyncio-subprocess or builders.
- [ ] Sync and async application paths behave identically (same test matrix).
- [ ] Exhausted retries return the final `CLITransactResult` — no exception.
- [ ] `make fullCheck` passes.

## Out of scope

- SuccessPolicy/TimeoutPolicy (kernel already covers defaults; add only when a
  transport needs them).
- Wiring policies into any transaction (chunks 06/07).
