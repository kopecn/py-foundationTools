"""Usage examples for SSHTransact: builds an ssh argv, delegates to CLITransact, never raises.
Targets localhost — succeeds only with Remote Login and key-based auth for the current user."""

import asyncio

from foundation_tools.cli_transaction.sshTransact import SSHTransact
from foundation_tools.policies.backoff_policy import BackoffPolicy
from foundation_tools.policies.retry_policy import RetryPolicy

print("---- sync ----")
print(SSHTransact.run_sync(host="localhost", command="echo hello-over-ssh", timeout=5))

print("\n---- async ----")
print(asyncio.run(SSHTransact.run_async(host="localhost", command="echo hi-over-ssh", timeout=5)))

print("\n---- sync with retry policy ----")
retry_policy = RetryPolicy(
    max_attempts=3,
    transient_return_codes=frozenset({255}),  # ssh "connection failed"
    backoff=BackoffPolicy(base_delay=0.2, max_delay=1.0, jitter=True),
)
print(
    SSHTransact.run_sync(
        host="localhost", command="echo hello-with-retry", timeout=5, retry_policy=retry_policy
    )
)
