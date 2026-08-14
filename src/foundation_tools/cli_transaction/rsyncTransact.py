"""
RsyncTransact — thin rsync transport transaction.

Builds an rsync command via :func:`foundation_tools.builders.build_rsync_command`
and delegates execution entirely to :class:`CLITransact`, returning its result
unchanged. RsyncTransact performs no retries, no parsing, and no result mutation —
see ``.claude/specs/rsyncTransact.md`` for the full contract. An optional
``retry_policy`` may be supplied per the policy-ownership rule (the transaction may
*select* a policy but never implements retry logic itself).
"""

from collections.abc import Callable
from pathlib import Path
from typing import Literal, TypeVar

from foundation_tools.builders.rsync_builder import (
    WINDOWS_SAFE_RSYNC_OPTIONS,
    build_rsync_command,
)
from foundation_tools.cli_transaction.cliTransact import (
    CLITransact,
    CLITransactResult,
    CLITransactResultModel,
)
from foundation_tools.policies.retry_policy import RetryPolicy
from foundationTypes.data_model_helper import DataModelHelper

T = TypeVar("T", bound=DataModelHelper)

__all__ = [
    "RSYNC_PERMANENT_RETURN_CODES",
    "RSYNC_TRANSIENT_RETURN_CODES",
    "WINDOWS_SAFE_RSYNC_OPTIONS",
    "RsyncTransact",
]

RSYNC_TRANSIENT_RETURN_CODES: frozenset[int] = frozenset({10, 12, 30, 35, -1})
"""Recommended transient-code set for a caller-supplied RetryPolicy: socket I/O,
interrupted protocol stream, timeout, daemon timeout, CLI framework timeout."""

RSYNC_PERMANENT_RETURN_CODES: frozenset[int] = frozenset({2, 4, 23, 24})
"""Recommended non-retryable set for a caller-supplied RetryPolicy."""


class RsyncTransact:
    """Stateless rsync transport transaction. Mirrors CLITransact's public surface.

    Every method builds the rsync argv, then delegates directly to the matching
    CLITransact method (optionally wrapped in ``retry_policy``) and returns its
    result unmodified.
    """

    @classmethod
    def run_sync(
        cls,
        *,
        src: str | Path,
        dst: str | Path,
        options: list[str] | None = None,
        default_options: list[str] | None = None,
        ssh_host: str | None = None,
        ssh_user: str | None = None,
        ssh_port: int | None = None,
        ssh_identity_file: str | None = None,
        remote_side: Literal["src", "dst"] = "dst",
        blocking_io: bool = False,
        timeout: int | None = None,
        success_marker: str | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> CLITransactResult:
        """Transfer ``src`` to ``dst`` synchronously via rsync."""
        rsync_command = cls._build(
            src,
            dst,
            options,
            default_options,
            ssh_host,
            ssh_user,
            ssh_port,
            ssh_identity_file,
            remote_side,
            blocking_io,
        )

        def _execute() -> CLITransactResult:
            return CLITransact.run_sync(
                rsync_command, timeout=timeout, success_marker=success_marker
            )

        if retry_policy is not None:
            return retry_policy.run_sync(_execute)
        return _execute()

    @classmethod
    async def run_async(
        cls,
        *,
        src: str | Path,
        dst: str | Path,
        options: list[str] | None = None,
        default_options: list[str] | None = None,
        ssh_host: str | None = None,
        ssh_user: str | None = None,
        ssh_port: int | None = None,
        ssh_identity_file: str | None = None,
        remote_side: Literal["src", "dst"] = "dst",
        blocking_io: bool = False,
        timeout: int | None = None,
        success_marker: str | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> CLITransactResult:
        """Transfer ``src`` to ``dst`` asynchronously via rsync."""
        rsync_command = cls._build(
            src,
            dst,
            options,
            default_options,
            ssh_host,
            ssh_user,
            ssh_port,
            ssh_identity_file,
            remote_side,
            blocking_io,
        )

        async def _execute() -> CLITransactResult:
            return await CLITransact.run_async(
                rsync_command, timeout=timeout, success_marker=success_marker
            )

        if retry_policy is not None:
            return await retry_policy.run_async(_execute)
        return await _execute()

    @classmethod
    def run_sync_with_model(
        cls,
        *,
        src: str | Path,
        dst: str | Path,
        output_parser: Callable[[str], T],
        options: list[str] | None = None,
        default_options: list[str] | None = None,
        ssh_host: str | None = None,
        ssh_user: str | None = None,
        ssh_port: int | None = None,
        ssh_identity_file: str | None = None,
        remote_side: Literal["src", "dst"] = "dst",
        blocking_io: bool = False,
        timeout: int | None = None,
        success_marker: str | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> CLITransactResultModel[T]:
        """Transfer ``src`` to ``dst`` synchronously and parse stdout into a model."""
        rsync_command = cls._build(
            src,
            dst,
            options,
            default_options,
            ssh_host,
            ssh_user,
            ssh_port,
            ssh_identity_file,
            remote_side,
            blocking_io,
        )

        def _execute() -> CLITransactResultModel[T]:
            return CLITransact.run_sync_with_model(
                rsync_command, output_parser, timeout=timeout, success_marker=success_marker
            )

        if retry_policy is not None:
            return retry_policy.run_sync(_execute)
        return _execute()

    @classmethod
    async def run_async_with_model(
        cls,
        *,
        src: str | Path,
        dst: str | Path,
        output_parser: Callable[[str], T],
        options: list[str] | None = None,
        default_options: list[str] | None = None,
        ssh_host: str | None = None,
        ssh_user: str | None = None,
        ssh_port: int | None = None,
        ssh_identity_file: str | None = None,
        remote_side: Literal["src", "dst"] = "dst",
        blocking_io: bool = False,
        timeout: int | None = None,
        success_marker: str | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> CLITransactResultModel[T]:
        """Transfer ``src`` to ``dst`` asynchronously and parse stdout into a model."""
        rsync_command = cls._build(
            src,
            dst,
            options,
            default_options,
            ssh_host,
            ssh_user,
            ssh_port,
            ssh_identity_file,
            remote_side,
            blocking_io,
        )

        async def _execute() -> CLITransactResultModel[T]:
            return await CLITransact.run_async_with_model(
                rsync_command, output_parser, timeout=timeout, success_marker=success_marker
            )

        if retry_policy is not None:
            return await retry_policy.run_async(_execute)
        return await _execute()

    @staticmethod
    def _build(
        src: str | Path,
        dst: str | Path,
        options: list[str] | None,
        default_options: list[str] | None,
        ssh_host: str | None,
        ssh_user: str | None,
        ssh_port: int | None,
        ssh_identity_file: str | None,
        remote_side: Literal["src", "dst"],
        blocking_io: bool,
    ) -> list[str]:
        return build_rsync_command(
            src=src,
            dst=dst,
            options=options,
            default_options=default_options,
            ssh_host=ssh_host,
            ssh_user=ssh_user,
            ssh_port=ssh_port,
            ssh_identity_file=ssh_identity_file,
            remote_side=remote_side,
            blocking_io=blocking_io,
        )
