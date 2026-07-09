"""
Tests for RsyncTransact (Action Plan 07): the thin rsync transport transaction.

Covers the 12 Compliance Requirements in `.claude/specs/rsyncTransact.md`: exactly
four stateless classmethods, deterministic argv construction (local/pull/push,
option precedence, SSH injection, blocking-io opt-in, Windows preset re-export),
exclusive delegation to CLITransact, zero retries/parsing/result-mutation of its
own, and optional policy pass-through.
"""

import inspect
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from foundation_tools.cli_transaction import (
    RSYNC_PERMANENT_RETURN_CODES,
    RSYNC_TRANSIENT_RETURN_CODES,
    WINDOWS_SAFE_RSYNC_OPTIONS,
    CLITransact,
    CLITransactResult,
    RsyncTransact,
)
from foundation_tools.policies import RetryPolicy
from foundationTypes.data_model_helper import DataModelHelper

RSYNC_AVAILABLE = shutil.which("rsync") is not None


class TestRsyncTransactPublicSurface:
    def test_exactly_four_stateless_classmethods(self) -> None:
        for name in ("run_sync", "run_async", "run_sync_with_model", "run_async_with_model"):
            assert isinstance(inspect.getattr_static(RsyncTransact, name), classmethod)


class TestRsyncTransactCommandConstruction:
    def test_run_sync_builds_command_and_delegates(self) -> None:
        sentinel = CLITransactResult(return_code=0, stdout="ok", success=True)
        with patch.object(CLITransact, "run_sync", return_value=sentinel) as mock_run_sync:
            result = RsyncTransact.run_sync(
                src="/local/src", dst="/local/dst", timeout=5, success_marker="ok"
            )
        mock_run_sync.assert_called_once_with(
            ["rsync", "/local/src", "/local/dst"], timeout=5, success_marker="ok"
        )
        assert result is sentinel

    def test_local_mode_no_ssh_flag(self) -> None:
        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=0)
        ) as mock_run_sync:
            RsyncTransact.run_sync(src="/local/src", dst="/local/dst")
        assert "-e" not in mock_run_sync.call_args.args[0]

    def test_push_mode_remote_destination(self) -> None:
        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=0)
        ) as mock_run_sync:
            RsyncTransact.run_sync(src="/local/src", dst="/remote/dst", ssh_host="example.com")
        argv = mock_run_sync.call_args.args[0]
        assert argv[-1] == "example.com:/remote/dst"
        assert argv[-2] == "/local/src"

    def test_pull_mode_remote_source(self) -> None:
        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=0)
        ) as mock_run_sync:
            RsyncTransact.run_sync(
                src="/remote/src",
                dst="/local/dst",
                ssh_host="example.com",
                remote_side="src",
            )
        argv = mock_run_sync.call_args.args[0]
        assert argv[-2] == "example.com:/remote/src"
        assert argv[-1] == "/local/dst"

    def test_pathlib_paths_accepted(self) -> None:
        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=0)
        ) as mock_run_sync:
            RsyncTransact.run_sync(src=Path("/local/src"), dst=Path("/local/dst"))
        argv = mock_run_sync.call_args.args[0]
        assert argv[-2:] == ["/local/src", "/local/dst"]


class TestRsyncTransactOptionPrecedence:
    def test_options_supplied_used_exactly(self) -> None:
        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=0)
        ) as mock_run_sync:
            RsyncTransact.run_sync(
                src="/local/src", dst="/local/dst", options=["-z"], default_options=["-avz"]
            )
        argv = mock_run_sync.call_args.args[0]
        assert argv == ["rsync", "-z", "/local/src", "/local/dst"]

    def test_options_empty_list_disables_defaults(self) -> None:
        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=0)
        ) as mock_run_sync:
            RsyncTransact.run_sync(
                src="/local/src", dst="/local/dst", options=[], default_options=["-avz"]
            )
        argv = mock_run_sync.call_args.args[0]
        assert argv == ["rsync", "/local/src", "/local/dst"]

    def test_options_none_uses_default_options(self) -> None:
        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=0)
        ) as mock_run_sync:
            RsyncTransact.run_sync(
                src="/local/src", dst="/local/dst", default_options=["-avz", "--partial"]
            )
        argv = mock_run_sync.call_args.args[0]
        assert argv == ["rsync", "-avz", "--partial", "/local/src", "/local/dst"]


class TestRsyncTransactSshInjection:
    def test_injected_when_ssh_host_supplied(self) -> None:
        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=0)
        ) as mock_run_sync:
            RsyncTransact.run_sync(src="/local", dst="/remote", ssh_host="example.com")
        argv = mock_run_sync.call_args.args[0]
        assert argv[argv.index("-e") + 1] == "ssh"

    def test_ssh_port_and_identity_reuse_ssh_formatting(self) -> None:
        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=0)
        ) as mock_run_sync:
            RsyncTransact.run_sync(
                src="/local",
                dst="/remote",
                ssh_host="example.com",
                ssh_port=2222,
                ssh_identity_file="/keys/id_rsa",
            )
        argv = mock_run_sync.call_args.args[0]
        assert argv[argv.index("-e") + 1] == "ssh -p 2222 -i /keys/id_rsa"

    def test_no_injection_without_ssh_parameters(self) -> None:
        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=0)
        ) as mock_run_sync:
            RsyncTransact.run_sync(src="/local", dst="/remote")
        assert "-e" not in mock_run_sync.call_args.args[0]


class TestRsyncTransactHostlessSshGuardPropagation:
    """Corrective (Action Plan 15): the builder's ValueError for host-less SSH
    injection (ssh_port/ssh_identity_file without ssh_host) must propagate out of
    RsyncTransact.run_sync before any subprocess is spawned — the never-raise
    containment rule applies to execution, not to invalid build-time arguments."""

    def test_run_sync_raises_before_kernel_invoked(self) -> None:
        with patch.object(CLITransact, "run_sync") as mock_run_sync:
            with pytest.raises(ValueError):
                RsyncTransact.run_sync(src="/local", dst="/remote", ssh_port=2222)
        mock_run_sync.assert_not_called()

    @pytest.mark.asyncio
    async def test_run_async_raises_before_kernel_invoked(self) -> None:
        mock_run_async = AsyncMock()
        with patch.object(CLITransact, "run_async", mock_run_async):
            with pytest.raises(ValueError):
                await RsyncTransact.run_async(src="/local", dst="/remote", ssh_port=2222)
        mock_run_async.assert_not_called()

    def test_run_sync_with_model_raises_before_kernel_invoked(self) -> None:
        def parser(_stdout: str) -> DataModelHelper:
            raise AssertionError("parser should not be invoked by RsyncTransact itself")

        with patch.object(CLITransact, "run_sync_with_model") as mock_run_sync_with_model:
            with pytest.raises(ValueError):
                RsyncTransact.run_sync_with_model(
                    src="/local", dst="/remote", ssh_port=2222, output_parser=parser
                )
        mock_run_sync_with_model.assert_not_called()

    @pytest.mark.asyncio
    async def test_run_async_with_model_raises_before_kernel_invoked(self) -> None:
        def parser(_stdout: str) -> DataModelHelper:
            raise AssertionError("parser should not be invoked by RsyncTransact itself")

        mock_run_async_with_model = AsyncMock()
        with patch.object(CLITransact, "run_async_with_model", mock_run_async_with_model):
            with pytest.raises(ValueError):
                await RsyncTransact.run_async_with_model(
                    src="/local", dst="/remote", ssh_port=2222, output_parser=parser
                )
        mock_run_async_with_model.assert_not_called()


class TestRsyncTransactBlockingIoAndPreset:
    def test_blocking_io_opt_in(self) -> None:
        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=0)
        ) as mock_run_sync:
            RsyncTransact.run_sync(src="/local", dst="/remote", blocking_io=True)
        assert "--blocking-io" in mock_run_sync.call_args.args[0]

    def test_blocking_io_off_by_default(self) -> None:
        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=0)
        ) as mock_run_sync:
            RsyncTransact.run_sync(src="/local", dst="/remote")
        assert "--blocking-io" not in mock_run_sync.call_args.args[0]

    def test_windows_safe_preset_reexported(self) -> None:
        assert WINDOWS_SAFE_RSYNC_OPTIONS == [
            "-avz",
            "--partial",
            "--append-verify",
            "--timeout=30",
            "--contimeout=15",
        ]

    def test_windows_safe_preset_never_applied_automatically(self) -> None:
        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=0)
        ) as mock_run_sync:
            RsyncTransact.run_sync(src="/local", dst="/remote")
        argv = mock_run_sync.call_args.args[0]
        for option in WINDOWS_SAFE_RSYNC_OPTIONS:
            assert option not in argv


class TestRsyncTransactAsync:
    @pytest.mark.asyncio
    async def test_run_async_builds_command_and_delegates(self) -> None:
        sentinel = CLITransactResult(return_code=0, success=True)
        mock_run_async = AsyncMock(return_value=sentinel)
        with patch.object(CLITransact, "run_async", mock_run_async):
            result = await RsyncTransact.run_async(src="/local/src", dst="/local/dst")
        mock_run_async.assert_called_once_with(
            ["rsync", "/local/src", "/local/dst"], timeout=None, success_marker=None
        )
        assert result is sentinel


class TestRsyncTransactWithModel:
    def test_run_sync_with_model_forwards_parser_unchanged(self) -> None:
        def parser(_stdout: str) -> DataModelHelper:
            raise AssertionError("parser should not be invoked by RsyncTransact itself")

        sentinel = MagicMock()
        with patch.object(
            CLITransact, "run_sync_with_model", return_value=sentinel
        ) as mock_run_sync_with_model:
            result = RsyncTransact.run_sync_with_model(
                src="/local/src", dst="/local/dst", output_parser=parser
            )
        mock_run_sync_with_model.assert_called_once_with(
            ["rsync", "/local/src", "/local/dst"], parser, timeout=None, success_marker=None
        )
        assert result is sentinel

    @pytest.mark.asyncio
    async def test_run_async_with_model_forwards_parser_unchanged(self) -> None:
        def parser(_stdout: str) -> DataModelHelper:
            raise AssertionError("parser should not be invoked by RsyncTransact itself")

        sentinel = MagicMock()
        mock_run_async_with_model = AsyncMock(return_value=sentinel)
        with patch.object(CLITransact, "run_async_with_model", mock_run_async_with_model):
            result = await RsyncTransact.run_async_with_model(
                src="/local/src", dst="/local/dst", output_parser=parser
            )
        mock_run_async_with_model.assert_called_once_with(
            ["rsync", "/local/src", "/local/dst"], parser, timeout=None, success_marker=None
        )
        assert result is sentinel


class TestRsyncTransactNoRetryOfItsOwn:
    def test_run_sync_calls_kernel_exactly_once_without_policy(self) -> None:
        with patch.object(
            CLITransact, "run_sync", return_value=CLITransactResult(return_code=1)
        ) as mock_run_sync:
            RsyncTransact.run_sync(src="/local", dst="/remote")
        assert mock_run_sync.call_count == 1

    @pytest.mark.asyncio
    async def test_run_async_calls_kernel_exactly_once_without_policy(self) -> None:
        mock_run_async = AsyncMock(return_value=CLITransactResult(return_code=1))
        with patch.object(CLITransact, "run_async", mock_run_async):
            await RsyncTransact.run_async(src="/local", dst="/remote")
        assert mock_run_async.call_count == 1


class TestRsyncTransactRetryPolicyPassThrough:
    def test_run_sync_routes_through_supplied_policy(self) -> None:
        policy = MagicMock(spec=RetryPolicy)
        policy.run_sync.return_value = CLITransactResult(return_code=0, success=True)
        with patch.object(CLITransact, "run_sync", return_value=CLITransactResult(return_code=10)):
            result = RsyncTransact.run_sync(src="/local", dst="/remote", retry_policy=policy)
        policy.run_sync.assert_called_once()
        assert result is policy.run_sync.return_value

    @pytest.mark.asyncio
    async def test_run_async_routes_through_supplied_policy(self) -> None:
        policy = MagicMock(spec=RetryPolicy)
        policy.run_async = AsyncMock(return_value=CLITransactResult(return_code=0, success=True))
        mock_run_async = AsyncMock(return_value=CLITransactResult(return_code=10))
        with patch.object(CLITransact, "run_async", mock_run_async):
            result = await RsyncTransact.run_async(src="/local", dst="/remote", retry_policy=policy)
        policy.run_async.assert_called_once()
        assert result is policy.run_async.return_value

    def test_transient_and_permanent_code_constants_match_spec(self) -> None:
        assert RSYNC_TRANSIENT_RETURN_CODES == frozenset({10, 12, 30, 35, -1})
        assert RSYNC_PERMANENT_RETURN_CODES == frozenset({2, 4, 23, 24})


class TestRsyncTransactResultIdentity:
    def test_result_is_returned_unmodified(self) -> None:
        sentinel = CLITransactResult(return_code=0, stdout="unchanged", success=True)
        with patch.object(CLITransact, "run_sync", return_value=sentinel):
            result = RsyncTransact.run_sync(src="/local", dst="/remote")
        assert result is sentinel
        assert result.stdout == "unchanged"


@pytest.mark.skipif(not RSYNC_AVAILABLE, reason="rsync binary not present on this host")
class TestRsyncTransactLocalSmoke:
    def test_local_to_local_copy(self, tmp_path: Path) -> None:
        src_dir = tmp_path / "src"
        dst_dir = tmp_path / "dst"
        src_dir.mkdir()
        dst_dir.mkdir()
        (src_dir / "hello.txt").write_text("hello rsync")

        result = RsyncTransact.run_sync(src=f"{src_dir}/", dst=str(dst_dir), options=["-a"])

        assert result.success is True
        assert (dst_dir / "hello.txt").read_text() == "hello rsync"
