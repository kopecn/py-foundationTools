"""
Tests for the command-builder layer (Action Plan 04): ssh_builder + rsync_builder.

All assertions are golden-argv comparisons: given fixed inputs, the builder must
produce an exact, deterministic ``list[str]``.
"""

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

    def test_injected_when_only_ssh_port_supplied(self) -> None:
        command = build_rsync_command(src="/local", dst="/remote", ssh_port=2222)
        assert "-e" in command
        assert command[command.index("-e") + 1] == "ssh -p 2222"

    def test_injected_when_only_ssh_identity_file_supplied(self) -> None:
        command = build_rsync_command(src="/local", dst="/remote", ssh_identity_file="/k")
        assert "-e" in command
        assert command[command.index("-e") + 1] == "ssh -i /k"

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
