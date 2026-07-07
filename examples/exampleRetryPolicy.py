"""
This example shows composing BackoffPolicy + RetryPolicy over a CLITransact call.

Per the Policy Ownership rule, a transaction (CLITransact/SSHTransact/
RsyncTransact) never implements retry logic itself — a RetryPolicy wraps an
already-constructed callable and owns attempt count, transient-return-code
classification, and backoff between attempts. It never touches subprocess or
asyncio APIs directly, so it composes unchanged over any transaction.

A local counter simulates a transiently-failing command (fails twice, then
succeeds) so this example runs deterministically with no external dependency.
"""

import asyncio

from foundation_tools.cli_transaction.cliTransact import CLITransact, CLITransactResult
from foundation_tools.policies.backoff_policy import BackoffPolicy
from foundation_tools.policies.retry_policy import RetryPolicy

TRANSIENT_RETURN_CODE = 1


def run_sync_with_retries() -> None:
    attempts = {"n": 0}

    def flaky_command() -> CLITransactResult:
        attempts["n"] += 1
        # Fails (exit 1) on the first two attempts, succeeds on the third.
        command = "true" if attempts["n"] >= 3 else "false"
        return CLITransact.run_sync(command, timeout=5)

    retry_policy = RetryPolicy(
        max_attempts=5,
        transient_return_codes=frozenset({TRANSIENT_RETURN_CODE}),
        backoff=BackoffPolicy(base_delay=0.05, max_delay=1.0),
    )

    result = retry_policy.run_sync(flaky_command)
    print(f"succeeded after {attempts['n']} attempt(s): {result}")


async def run_async_with_retries() -> None:
    attempts = {"n": 0}

    async def flaky_command() -> CLITransactResult:
        attempts["n"] += 1
        command = "true" if attempts["n"] >= 3 else "false"
        return await CLITransact.run_async(command, timeout=5)

    retry_policy = RetryPolicy(
        max_attempts=5,
        transient_return_codes=frozenset({TRANSIENT_RETURN_CODE}),
        backoff=BackoffPolicy(base_delay=0.05, max_delay=1.0),
    )

    result = await retry_policy.run_async(flaky_command)
    print(f"succeeded after {attempts['n']} attempt(s): {result}")


def run_non_transient_failure_stops_immediately() -> None:
    """A return code outside `transient_return_codes` terminates on the first
    attempt — RetryPolicy only retries failures it was told are transient."""
    attempts = {"n": 0}

    def always_permanent_failure() -> CLITransactResult:
        attempts["n"] += 1
        return CLITransact.run_sync("exit 2", timeout=5)  # 2 is not in the transient set

    retry_policy = RetryPolicy(
        max_attempts=5,
        transient_return_codes=frozenset({TRANSIENT_RETURN_CODE}),
        backoff=BackoffPolicy(base_delay=0.05, max_delay=1.0),
    )

    result = retry_policy.run_sync(always_permanent_failure)
    print(f"stopped after {attempts['n']} attempt(s) (non-transient): success={result.success}")


if __name__ == "__main__":
    run_sync_with_retries()
    asyncio.run(run_async_with_retries())
    run_non_transient_failure_stops_immediately()
