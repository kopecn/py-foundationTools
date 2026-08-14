"""
This example shows usage for SSHTransact: a thin transaction that builds an SSH
argv via `build_ssh_command` and delegates execution to CLITransact unchanged.
Like CLITransact, it never raises — connection failures surface as
`result.success is False`, not an exception.

These examples target `localhost` so the file runs unattended, but they will only
succeed if the machine has an SSH server enabled and key-based auth configured
for the current user (macOS: System Settings > General > Sharing > Remote Login).
That is intentional: SSHTransact's whole contract is "never raise, always return
a result", so failing to reach a host is just another result to print, not an
error to handle specially.
"""

import asyncio

from foundation_tools.cli_transaction.sshTransact import SSHTransact
from foundation_tools.policies.backoff_policy import BackoffPolicy
from foundation_tools.policies.retry_policy import RetryPolicy


def run_sync() -> None:
    result = SSHTransact.run_sync(host="localhost", command="echo hello-over-ssh", timeout=5)
    print(result)


async def run_async() -> None:
    result = await SSHTransact.run_async(host="localhost", command="echo hello-over-ssh", timeout=5)
    print(result)


def run_sync_with_retry() -> None:
    """An optional RetryPolicy may be supplied (SSHTransact never implements
    retry logic itself — see the Policy Ownership rule); a flaky connection
    gets a few attempts with exponential backoff before giving up."""
    retry_policy = RetryPolicy(
        max_attempts=3,
        transient_return_codes=frozenset({255}),  # ssh's "connection failed" code
        backoff=BackoffPolicy(base_delay=0.2, max_delay=1.0, jitter=True),
    )
    result = SSHTransact.run_sync(
        host="localhost",
        command="echo hello-with-retry",
        timeout=5,
        retry_policy=retry_policy,
    )
    print(result)


if __name__ == "__main__":
    run_sync()
    asyncio.run(run_async())
    run_sync_with_retry()
