"""Usage examples for RetryPolicy + BackoffPolicy over a CLITransact call.
A local counter simulates a transiently-failing command so this runs deterministically."""

import asyncio

from foundation_tools.cli_transaction.cliTransact import CLITransact, CLITransactResult
from foundation_tools.policies.backoff_policy import BackoffPolicy
from foundation_tools.policies.retry_policy import RetryPolicy

TRANSIENT_RETURN_CODE = 1
retry_policy = RetryPolicy(
    max_attempts=5,
    transient_return_codes=frozenset({TRANSIENT_RETURN_CODE}),
    backoff=BackoffPolicy(base_delay=0.05, max_delay=1.0),
)

print("---- sync: fails twice, then succeeds ----")
attempts = {"n": 0}


def flaky_sync() -> CLITransactResult:
    attempts["n"] += 1
    return CLITransact.run_sync("true" if attempts["n"] >= 3 else "false", timeout=5)


print(f"succeeded after {attempts['n']} attempt(s): {retry_policy.run_sync(flaky_sync)}")

print("\n---- async: fails twice, then succeeds ----")
attempts = {"n": 0}


async def flaky_async() -> CLITransactResult:
    attempts["n"] += 1
    return await CLITransact.run_async("true" if attempts["n"] >= 3 else "false", timeout=5)


result = asyncio.run(retry_policy.run_async(flaky_async))
print(f"succeeded after {attempts['n']} attempt(s): {result}")

print("\n---- non-transient failure stops immediately ----")
attempts = {"n": 0}


def permanent_failure() -> CLITransactResult:
    attempts["n"] += 1
    return CLITransact.run_sync("exit 2", timeout=5)  # 2 is not in the transient set


result = retry_policy.run_sync(permanent_failure)
print(f"stopped after {attempts['n']} attempt(s): success={result.success}")
