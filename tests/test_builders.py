"""
Tests for the command-builder layer (Action Plan 04): ssh_builder + rsync_builder.

All assertions are golden-argv comparisons: given fixed inputs, the builder must
produce an exact, deterministic ``list[str]``.
"""

import itertools

import pytest

from foundation_tools.builders import (
    WINDOWS_SAFE_RSYNC_OPTIONS,
    build_rsync_command,
    build_ssh_command,
)


class TestBuildSshCommand:
    def test_host_only(self) -> None:
        assert build_ssh_command(host="example.com") == ["ssh", "example.com"]

    def test_user_and_host(self) -> None:
        assert build_ssh_command(host="example.com", user="alice") == [
            "ssh",
            "alice@example.com",
        ]

    def test_port_supplied(self) -> None:
        assert build_ssh_command(host="example.com", port=2222) == [
            "ssh",
            "-p",
            "2222",
            "example.com",
        ]

    def test_port_omitted_by_default(self) -> None:
        command = build_ssh_command(host="example.com")
        assert "-p" not in command

    def test_identity_file_supplied(self) -> None:
        assert build_ssh_command(host="example.com", identity_file="/keys/id_rsa") == [
            "ssh",
            "-i",
            "/keys/id_rsa",
            "example.com",
        ]

    def test_identity_file_omitted_by_default(self) -> None:
        command = build_ssh_command(host="example.com")
        assert "-i" not in command

    def test_full_transport_parameters(self) -> None:
        assert build_ssh_command(
            host="example.com", user="alice", port=2222, identity_file="/keys/id_rsa"
        ) == ["ssh", "-p", "2222", "-i", "/keys/id_rsa", "alice@example.com"]

    def test_string_remote_command_is_single_argument(self) -> None:
        assert build_ssh_command(host="example.com", command="cd /tmp && ls *.txt") == [
            "ssh",
            "example.com",
            "cd /tmp && ls *.txt",
        ]

    def test_list_remote_command_is_argv_segments(self) -> None:
        assert build_ssh_command(host="example.com", command=["python3", "--version"]) == [
            "ssh",
            "example.com",
            "python3",
            "--version",
        ]

    def test_no_remote_command_is_omitted(self) -> None:
        assert build_ssh_command(host="example.com") == ["ssh", "example.com"]

    def test_determinism(self) -> None:
        kwargs = {
            "host": "example.com",
            "user": "alice",
            "port": 2222,
            "identity_file": "/keys/id_rsa",
            "command": ["python3", "--version"],
        }
        assert build_ssh_command(**kwargs) == build_ssh_command(**kwargs)  # type: ignore[arg-type]


class TestBuildRsyncCommandOptionPrecedence:
    def test_options_supplied_used_exactly(self) -> None:
        command = build_rsync_command(
            src="/local", dst="/remote", options=["-z"], default_options=["-avz"]
        )
        assert command == ["rsync", "-z", "/local", "/remote"]

    def test_options_empty_list_disables_defaults(self) -> None:
        command = build_rsync_command(
            src="/local", dst="/remote", options=[], default_options=["-avz"]
        )
        assert command == ["rsync", "/local", "/remote"]

    def test_options_none_uses_default_options(self) -> None:
        command = build_rsync_command(
            src="/local", dst="/remote", options=None, default_options=["-avz", "--partial"]
        )
        assert command == ["rsync", "-avz", "--partial", "/local", "/remote"]

    def test_options_none_and_no_default_options(self) -> None:
        command = build_rsync_command(src="/local", dst="/remote")
        assert command == ["rsync", "/local", "/remote"]

    def test_caller_order_preserved_no_dedup(self) -> None:
        command = build_rsync_command(
            src="/local",
            dst="/remote",
            options=["--timeout=30", "-avz", "--timeout=30"],
        )
        assert command == [
            "rsync",
            "--timeout=30",
            "-avz",
            "--timeout=30",
            "/local",
            "/remote",
        ]


class TestBuildRsyncCommandModes:
    def test_local_mode_no_ssh_transport(self) -> None:
        command = build_rsync_command(src="/local/src", dst="/local/dst")
        assert command == ["rsync", "/local/src", "/local/dst"]
        assert "-e" not in command

    def test_pull_mode_remote_source(self) -> None:
        command = build_rsync_command(
            src="/remote/path",
            dst="/local/path",
            ssh_host="example.com",
            remote_side="src",
        )
        assert command == [
            "rsync",
            "-e",
            "ssh",
            "example.com:/remote/path",
            "/local/path",
        ]

    def test_push_mode_remote_destination(self) -> None:
        command = build_rsync_command(src="/local/path", dst="/remote/path", ssh_host="example.com")
        assert command == [
            "rsync",
            "-e",
            "ssh",
            "/local/path",
            "example.com:/remote/path",
        ]

    def test_remote_user_formatting(self) -> None:
        command = build_rsync_command(
            src="/local/path",
            dst="/remote/path",
            ssh_host="example.com",
            ssh_user="alice",
        )
        assert command[-1] == "alice@example.com:/remote/path"

    def test_path_accepts_pathlib_path(self) -> None:
        from pathlib import Path

        command = build_rsync_command(src=Path("/local/src"), dst=Path("/local/dst"))
        assert command == ["rsync", "/local/src", "/local/dst"]


class TestBuildRsyncCommandSshInjection:
    def test_injected_when_ssh_host_supplied(self) -> None:
        command = build_rsync_command(src="/local", dst="/remote", ssh_host="example.com")
        assert "-e" in command
        assert command[command.index("-e") + 1] == "ssh"

    def test_injected_when_only_ssh_port_supplied_but_host_missing_raises(self) -> None:
        # Corrective (Action Plan 15): ssh_port alone (no ssh_host) is a build-time
        # caller bug, not a valid injection — see TestBuildRsyncCommandHostlessSshGuard.
        with pytest.raises(ValueError):
            build_rsync_command(src="/local", dst="/remote", ssh_port=2222)

    def test_injected_when_only_ssh_identity_file_supplied_but_host_missing_raises(self) -> None:
        # Corrective (Action Plan 15): ssh_identity_file alone (no ssh_host) is a
        # build-time caller bug — see TestBuildRsyncCommandHostlessSshGuard.
        with pytest.raises(ValueError):
            build_rsync_command(src="/local", dst="/remote", ssh_identity_file="/k")

    def test_ssh_port_omitted_by_default(self) -> None:
        command = build_rsync_command(src="/local", dst="/remote", ssh_host="example.com")
        assert command[command.index("-e") + 1] == "ssh"

    def test_ssh_full_transport_reuses_ssh_formatting(self) -> None:
        command = build_rsync_command(
            src="/local",
            dst="/remote",
            ssh_host="example.com",
            ssh_port=2222,
            ssh_identity_file="/keys/id_rsa",
        )
        assert command[command.index("-e") + 1] == "ssh -p 2222 -i /keys/id_rsa"

    def test_no_injection_when_no_ssh_parameters(self) -> None:
        command = build_rsync_command(src="/local", dst="/remote")
        assert "-e" not in command


class TestBuildRsyncCommandHostlessSshGuard:
    """Corrective (Action Plan 15): ssh_port/ssh_identity_file alone (no ssh_host)
    must raise ValueError at build time rather than emit an invalid ``None:/path``
    argv. ssh_user alone must NOT trigger injection (unchanged rule)."""

    def test_ssh_port_alone_raises(self) -> None:
        with pytest.raises(ValueError):
            build_rsync_command(src="/local", dst="/remote", ssh_port=2222)

    def test_ssh_identity_file_alone_raises(self) -> None:
        with pytest.raises(ValueError):
            build_rsync_command(src="/local", dst="/remote", ssh_identity_file="/k")

    def test_ssh_port_and_identity_file_without_host_raises(self) -> None:
        with pytest.raises(ValueError):
            build_rsync_command(src="/local", dst="/remote", ssh_port=2222, ssh_identity_file="/k")

    def test_ssh_user_alone_does_not_trigger_injection(self) -> None:
        command = build_rsync_command(src="/local", dst="/remote", ssh_user="alice")
        assert "-e" not in command
        assert command == ["rsync", "/local", "/remote"]

    def test_valid_combinations_still_raise_no_error(self) -> None:
        # sanity: ssh_host present with port/identity is still valid.
        build_rsync_command(
            src="/local",
            dst="/remote",
            ssh_host="example.com",
            ssh_port=2222,
            ssh_identity_file="/k",
        )


class TestBuildRsyncCommandGoldenArgvNoneSweep:
    """Sweeps every combination of the SSH-related kwargs; any combination that
    does not raise must produce an argv with no ``"None"`` substring anywhere."""

    def test_no_valid_command_contains_none_substring(self) -> None:
        hosts: list[str | None] = [None, "example.com"]
        users: list[str | None] = [None, "alice"]
        ports: list[int | None] = [None, 2222]
        identity_files: list[str | None] = [None, "/keys/id_rsa"]
        remote_sides = ["src", "dst"]

        checked_at_least_one = False
        for ssh_host, ssh_user, ssh_port, ssh_identity_file, remote_side in itertools.product(
            hosts, users, ports, identity_files, remote_sides
        ):
            try:
                command = build_rsync_command(
                    src="/local",
                    dst="/remote",
                    ssh_host=ssh_host,
                    ssh_user=ssh_user,
                    ssh_port=ssh_port,
                    ssh_identity_file=ssh_identity_file,
                    remote_side=remote_side,  # type: ignore[arg-type]
                )
            except ValueError:
                continue
            checked_at_least_one = True
            for part in command:
                assert "None" not in part
        assert checked_at_least_one


class TestBuildRsyncCommandBlockingIo:
    def test_blocking_io_opt_in(self) -> None:
        command = build_rsync_command(src="/local", dst="/remote", blocking_io=True)
        assert command == ["rsync", "--blocking-io", "/local", "/remote"]

    def test_blocking_io_off_by_default(self) -> None:
        command = build_rsync_command(src="/local", dst="/remote")
        assert "--blocking-io" not in command

    def test_blocking_io_never_in_windows_preset(self) -> None:
        assert "--blocking-io" not in WINDOWS_SAFE_RSYNC_OPTIONS


class TestWindowsSafeRsyncOptionsPreset:
    def test_preset_content(self) -> None:
        assert WINDOWS_SAFE_RSYNC_OPTIONS == [
            "-avz",
            "--partial",
            "--append-verify",
            "--timeout=30",
            "--contimeout=15",
        ]

    def test_preset_never_applied_automatically(self) -> None:
        command = build_rsync_command(src="/local", dst="/remote")
        for option in WINDOWS_SAFE_RSYNC_OPTIONS:
            assert option not in command


class TestBuildRsyncCommandReturnType:
    def test_always_returns_list_never_str(self) -> None:
        command = build_rsync_command(src="/local", dst="/remote", ssh_host="example.com")
        assert isinstance(command, list)
        assert all(isinstance(part, str) for part in command)


class TestBuildRsyncCommandDeterminism:
    def test_same_input_identical_output(self) -> None:
        kwargs = {
            "src": "/local/path",
            "dst": "/remote/path",
            "ssh_host": "example.com",
            "ssh_user": "alice",
            "ssh_port": 2222,
            "ssh_identity_file": "/keys/id_rsa",
            "options": ["-avz", "--partial"],
        }
        assert build_rsync_command(**kwargs) == build_rsync_command(**kwargs)  # type: ignore[arg-type]
