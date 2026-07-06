"""
RetryPolicy — composable retry orchestration over a transaction callable.

Owns attempt count, transient-return-code classification, and termination
(success / non-transient failure / attempts exhausted). It never builds commands
and never touches ``subprocess`` or ``asyncio`` subprocess APIs directly — it wraps
an already-constructed ``Callable[[], R]`` (sync) or
``Callable[[], Awaitable[R]]`` (async) that performs the execution, so it works
unchanged for any transport transaction. Per the Policy Ownership rule, a transport
transaction may *select* a ``RetryPolicy`` but must not implement retry logic
itself.

Timeout composition: ``timeout`` passed to the wrapped callable governs each
attempt; this policy adds no overall deadline. Worst-case wall time is
approximately ``attempts * timeout`` plus the sum of backoff delays.
"""

import asyncio
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypeVar

from foundation_tools.policies.backoff_policy import BackoffPolicy

if TYPE_CHECKING:
    # Deferred: importing this eagerly (even from the submodule) forces
    # foundation_tools.cli_transaction's package __init__ to execute, which pulls in
    # rsyncTransact -> foundation_tools.policies.retry_policy -- a cycle when this
    # module is imported first (e.g. `from foundation_tools.policies import
    # RetryPolicy` as the first import in a fresh interpreter). The string bound
    # below is resolved by static type checkers only; no runtime import needed since
    # CLITransactResult is never referenced outside the type bound.
    from foundation_tools.cli_transaction.cliTransact import CLITransactResult

R = TypeVar("R", bound="CLITransactResult")

SyncSleeper = Callable[[float], None]
AsyncSleeper = Callable[[float], Awaitable[None]]


@dataclass(frozen=True)
class RetryPolicy:
    """Retries a transaction callable on transient failure, with injected sleepers.

    Attributes:
        max_attempts: Total attempts allowed, including the first. Must be >= 1.
        transient_return_codes: Return codes that are eligible for retry. A
            non-transient failure (return code not in this set) terminates
            immediately with the result as-is.
        backoff: Delay computation between attempts.
        sync_sleeper: Injected sleep function for the sync path (default
            ``time.sleep``); tests inject a no-op to run instantly.
        async_sleeper: Injected sleep coroutine for the async path (default
            ``asyncio.sleep``); tests inject a no-op to run instantly.
    """

    max_attempts: int
    transient_return_codes: frozenset[int]
    backoff: BackoffPolicy
    sync_sleeper: SyncSleeper = field(default=time.sleep)
    async_sleeper: AsyncSleeper = field(default=asyncio.sleep)

    def _is_terminal(self, result: R, attempt: int) -> bool:
        """Whether retrying should stop: success, non-transient failure, or exhausted."""
        if result.success:
            return True
        if result.return_code not in self.transient_return_codes:
            return True
        return attempt >= self.max_attempts - 1

    def run_sync(self, execute: Callable[[], R]) -> R:
        """Invoke ``execute`` synchronously, retrying transient failures.

        Returns the final ``CLITransactResult`` (or subtype) regardless of outcome;
        never raises.
        """
        attempt = 0
        while True:
            result = execute()
            if self._is_terminal(result, attempt):
                return result
            self.sync_sleeper(self.backoff.compute_delay(attempt))
            attempt += 1

    async def run_async(self, execute: Callable[[], Awaitable[R]]) -> R:
        """Invoke ``execute`` asynchronously, retrying transient failures.

        Returns the final ``CLITransactResult`` (or subtype) regardless of outcome;
        never raises.
        """
        attempt = 0
        while True:
            result = await execute()
            if self._is_terminal(result, attempt):
                return result
            await self.async_sleeper(self.backoff.compute_delay(attempt))
            attempt += 1
