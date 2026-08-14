"""
Tests for SSHTransact (Action Plan 06): the thin SSH transport transaction.

Covers the 10 Compliance Requirements in `.claude/specs/sshTransact.md`: exactly
four stateless classmethods, deterministic command construction (port/identity/user
rules delegated to build_ssh_command), str-vs-list command-type preservation,
exclusive delegation to CLITransact, zero retries/parsing/result-mutation of its
own, and optional policy pass-through.
"""

import inspect
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from foundation_tools.cli_transaction import CLITransact, CLITransactResult, SSHTransact
from foundation_tools.policies import RetryPolicy
from foundationTypes.data_model_helper import DataModelHelper


class TestSSHTransactPublicSurface:
    def test_exactly_four_stateless_classmethods(self) -> None:
        for name in ("run_sync", "run_async", "run_sync_with_model", "run_async_with_model"):
            assert isinstance(inspect.getattr_static(SSHTransact, name), classmethod)


class TestSSHTransactCommandConstruction:
    def test_run_sync_builds_command_and_delegates(self) -> None:
        sentinel = CLITransactResult(return_code=0, stdout="ok", success=True)
        with patch.object(CLITransact, "run_sync", return_value=sentinel) as mock_run_sync:
            result = SSHTransact.run_sync(
                host="example.com", command="uptime", timeout=5, success_marker="ok"
            )
        mock_run_sync.assert_called_once_with(
            ["ssh", "example.com", "uptime"], timeout=5, success_marker="ok"
        )
        assert result is sentinel

    def test_port_included_only_when_supplied(self) -> None:
        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=0)
        ) as mock_run_sync:
            SSHTransact.run_sync(host="example.com")
        assert "-p" not in mock_run_sync.call_args.args[0]

        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=0)
        ) as mock_run_sync:
            SSHTransact.run_sync(host="example.com", port=2222)
        argv = mock_run_sync.call_args.args[0]
        assert argv[argv.index("-p") + 1] == "2222"

    def test_identity_file_included_only_when_supplied(self) -> None:
        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=0)
        ) as mock_run_sync:
            SSHTransact.run_sync(host="example.com")
        assert "-i" not in mock_run_sync.call_args.args[0]

        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=0)
        ) as mock_run_sync:
            SSHTransact.run_sync(host="example.com", identity_file="/keys/id_rsa")
        argv = mock_run_sync.call_args.args[0]
        assert argv[argv.index("-i") + 1] == "/keys/id_rsa"

    def test_user_host_target_formatting(self) -> None:
        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=0)
        ) as mock_run_sync:
            SSHTransact.run_sync(host="example.com", user="alice")
        assert "alice@example.com" in mock_run_sync.call_args.args[0]

        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=0)
        ) as mock_run_sync:
            SSHTransact.run_sync(host="example.com")
        assert "example.com" in mock_run_sync.call_args.args[0]
        assert not any("@" in part for part in mock_run_sync.call_args.args[0])

    def test_string_command_is_single_argument(self) -> None:
        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=0)
        ) as mock_run_sync:
            SSHTransact.run_sync(host="example.com", command="cd /tmp && ls *.txt")
        argv = mock_run_sync.call_args.args[0]
        assert argv[-1] == "cd /tmp && ls *.txt"

    def test_list_command_is_argv_segments(self) -> None:
        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=0)
        ) as mock_run_sync:
            SSHTransact.run_sync(host="example.com", command=["python3", "--version"])
        argv = mock_run_sync.call_args.args[0]
        assert argv[-2:] == ["python3", "--version"]


class TestSSHTransactAsync:
    @pytest.mark.asyncio
    async def test_run_async_builds_command_and_delegates(self) -> None:
        sentinel = CLITransactResult(return_code=0, success=True)
        mock_run_async = AsyncMock(return_value=sentinel)
        with patch.object(CLITransact, "run_async", mock_run_async):
            result = await SSHTransact.run_async(
                host="example.com", command=["python3", "--version"]
            )
        mock_run_async.assert_called_once_with(
            ["ssh", "example.com", "python3", "--version"], timeout=None, success_marker=None
        )
        assert result is sentinel


class TestSSHTransactWithModel:
    def test_run_sync_with_model_forwards_parser_unchanged(self) -> None:
        def parser(_stdout: str) -> DataModelHelper:
            raise AssertionError("parser should not be invoked by SSHTransact itself")

        sentinel = MagicMock()
        with patch.object(
            CLITransact, "run_sync_with_model", return_value=sentinel
        ) as mock_run_sync_with_model:
            result = SSHTransact.run_sync_with_model(
                host="example.com", output_parser=parser, command="df -h"
            )
        mock_run_sync_with_model.assert_called_once_with(
            ["ssh", "example.com", "df -h"], parser, timeout=None, success_marker=None
        )
        assert result is sentinel

    @pytest.mark.asyncio
    async def test_run_async_with_model_forwards_parser_unchanged(self) -> None:
        def parser(_stdout: str) -> DataModelHelper:
            raise AssertionError("parser should not be invoked by SSHTransact itself")

        sentinel = MagicMock()
        mock_run_async_with_model = AsyncMock(return_value=sentinel)
        with patch.object(CLITransact, "run_async_with_model", mock_run_async_with_model):
            result = await SSHTransact.run_async_with_model(
                host="example.com", output_parser=parser, command="df -h"
            )
        mock_run_async_with_model.assert_called_once_with(
            ["ssh", "example.com", "df -h"], parser, timeout=None, success_marker=None
        )
        assert result is sentinel


class TestSSHTransactNoRetryOfItsOwn:
    def test_run_sync_calls_kernel_exactly_once_without_policy(self) -> None:
        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=1)
        ) as mock_run_sync:
            SSHTransact.run_sync(host="example.com")
        assert mock_run_sync.call_count == 1

    @pytest.mark.asyncio
    async def test_run_async_calls_kernel_exactly_once_without_policy(self) -> None:
        mock_run_async = AsyncMock(return_value=CLITransactResult(return_code=1))
        with patch.object(CLITransact, "run_async", mock_run_async):
            await SSHTransact.run_async(host="example.com")
        assert mock_run_async.call_count == 1


class TestSSHTransactRetryPolicyPassThrough:
    def test_run_sync_routes_through_supplied_policy(self) -> None:
        policy = MagicMock(spec=RetryPolicy)
        policy.run_sync.return_value = CLITransactResult(return_code=0, success=True)
        with patch.object(CLITransact, "run_sync", return_value=CLITransactResult(return_code=1)):
            result = SSHTransact.run_sync(host="example.com", retry_policy=policy)
        policy.run_sync.assert_called_once()
        assert result is policy.run_sync.return_value

    @pytest.mark.asyncio
    async def test_run_async_routes_through_supplied_policy(self) -> None:
        policy = MagicMock(spec=RetryPolicy)
        policy.run_async = AsyncMock(return_value=CLITransactResult(return_code=0, success=True))
        mock_run_async = AsyncMock(return_value=CLITransactResult(return_code=1))
        with patch.object(CLITransact, "run_async", mock_run_async):
            result = await SSHTransact.run_async(host="example.com", retry_policy=policy)
        policy.run_async.assert_called_once()
        assert result is policy.run_async.return_value


class TestSSHTransactResultIdentity:
    def test_result_is_returned_unmodified(self) -> None:
        sentinel = CLITransactResult(return_code=0, stdout="unchanged", success=True)
        with patch.object(CLITransact, "run_sync", return_value=sentinel):
            result = SSHTransact.run_sync(host="example.com")
        assert result is sentinel
        assert result.stdout == "unchanged"
