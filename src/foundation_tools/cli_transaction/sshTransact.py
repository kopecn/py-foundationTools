"""
SSHTransact — thin SSH transport transaction.

Builds an SSH command via :func:`foundation_tools.builders.build_ssh_command` and
delegates execution entirely to :class:`CLITransact`, returning its result
unchanged. SSHTransact performs no retries, no parsing, and no result mutation —
see ``.claude/specs/sshTransact.md`` for the full contract. An optional
``retry_policy`` may be supplied per the policy-ownership rule (the transaction may
*select* a policy but never implements retry logic itself).
"""

from collections.abc import Callable
from typing import TypeVar

from foundation_tools.builders.ssh_builder import build_ssh_command
from foundation_tools.cli_transaction.cliTransact import (
    CLITransact,
    CLITransactResult,
    CLITransactResultModel,
)
from foundation_tools.policies.retry_policy import RetryPolicy
from foundationTypes.data_model_helper import DataModelHelper

T = TypeVar("T", bound=DataModelHelper)


class SSHTransact:
    """Stateless SSH transport transaction. Mirrors CLITransact's public surface.

    Every method builds the SSH argv, then delegates directly to the matching
    CLITransact method (optionally wrapped in ``retry_policy``) and returns its
    result unmodified.
    """

    @classmethod
    def run_sync(
        cls,
        *,
        host: str,
        user: str | None = None,
        port: int | None = None,
        identity_file: str | None = None,
        command: str | list[str] | None = None,
        timeout: int | None = None,
        success_marker: str | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> CLITransactResult:
        """Execute ``command`` on ``host`` synchronously via SSH."""
        ssh_command = build_ssh_command(
            host=host, user=user, port=port, identity_file=identity_file, command=command
        )

        def _execute() -> CLITransactResult:
            return CLITransact.run_sync(ssh_command, timeout=timeout, success_marker=success_marker)

        if retry_policy is not None:
            return retry_policy.run_sync(_execute)
        return _execute()

    @classmethod
    async def run_async(
        cls,
        *,
        host: str,
        user: str | None = None,
        port: int | None = None,
        identity_file: str | None = None,
        command: str | list[str] | None = None,
        timeout: int | None = None,
        success_marker: str | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> CLITransactResult:
        """Execute ``command`` on ``host`` asynchronously via SSH."""
        ssh_command = build_ssh_command(
            host=host, user=user, port=port, identity_file=identity_file, command=command
        )

        async def _execute() -> CLITransactResult:
            return await CLITransact.run_async(
                ssh_command, timeout=timeout, success_marker=success_marker
            )

        if retry_policy is not None:
            return await retry_policy.run_async(_execute)
        return await _execute()

    @classmethod
    def run_sync_with_model(
        cls,
        *,
        host: str,
        output_parser: Callable[[str], T],
        user: str | None = None,
        port: int | None = None,
        identity_file: str | None = None,
        command: str | list[str] | None = None,
        timeout: int | None = None,
        success_marker: str | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> CLITransactResultModel[T]:
        """Execute ``command`` on ``host`` synchronously and parse stdout into a model."""
        ssh_command = build_ssh_command(
            host=host, user=user, port=port, identity_file=identity_file, command=command
        )

        def _execute() -> CLITransactResultModel[T]:
            return CLITransact.run_sync_with_model(
                ssh_command, output_parser, timeout=timeout, success_marker=success_marker
            )

        if retry_policy is not None:
            return retry_policy.run_sync(_execute)
        return _execute()

    @classmethod
    async def run_async_with_model(
        cls,
        *,
        host: str,
        output_parser: Callable[[str], T],
        user: str | None = None,
        port: int | None = None,
        identity_file: str | None = None,
        command: str | list[str] | None = None,
        timeout: int | None = None,
        success_marker: str | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> CLITransactResultModel[T]:
        """Execute ``command`` on ``host`` asynchronously and parse stdout into a model."""
        ssh_command = build_ssh_command(
            host=host, user=user, port=port, identity_file=identity_file, command=command
        )

        async def _execute() -> CLITransactResultModel[T]:
            return await CLITransact.run_async_with_model(
                ssh_command, output_parser, timeout=timeout, success_marker=success_marker
            )

        if retry_policy is not None:
            return await retry_policy.run_async(_execute)
        return await _execute()
