"""
rsync_builder — pure rsync command construction.

Builds argv-style ``rsync`` command vectors, injecting SSH transport via ``-e``
when requested. Never executes anything; execution is delegated by callers to
:mod:`foundation_tools.cli_transaction`. See ``.claude/specs/rsyncTransact.md`` for
the full construction contract.
"""

from pathlib import Path
from typing import Literal

WINDOWS_SAFE_RSYNC_OPTIONS = [
    "-avz",
    "--partial",
    "--append-verify",
    "--timeout=30",
    "--contimeout=15",
]
"""Recommended options for unreliable Windows/MSYS2 rsync hosts. Never applied
automatically — callers opt in explicitly via ``default_options`` or ``options``."""


def _build_ssh_transport_argument(ssh_port: int | None, ssh_identity_file: str | None) -> str:
    parts = ["ssh"]
    if ssh_port is not None:
        parts += ["-p", str(ssh_port)]
    if ssh_identity_file is not None:
        parts += ["-i", ssh_identity_file]
    return " ".join(parts)


def build_rsync_command(
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
) -> list[str]:
    """Construct a deterministic ``rsync`` command vector. Always returns ``list[str]``.

    Option precedence: ``options`` not ``None`` is used exactly as given; ``[]``
    disables all defaults; ``None`` falls back to ``default_options`` (or ``[]``
    if that is also ``None``). No merging, no deduplication — caller order is
    preserved exactly.

    SSH transport is injected via ``-e "ssh [-p PORT] [-i FILE]"`` whenever any of
    ``ssh_host``, ``ssh_port``, or ``ssh_identity_file`` is supplied, reusing the
    ssh_builder formatting rules (``-p`` only when a port is supplied). The remote
    side is formatted ``[user@]host:path``: ``remote_side="dst"`` (default) selects
    push mode, ``remote_side="src"`` selects pull mode. Both are ignored when no
    SSH transport is requested, giving local mode.

    ``blocking_io`` appends ``--blocking-io`` and is opt-in only; it is never part
    of :data:`WINDOWS_SAFE_RSYNC_OPTIONS`.
    """
    if options is not None:
        resolved_options = options
    elif default_options is not None:
        resolved_options = default_options
    else:
        resolved_options = []

    inject_ssh = ssh_host is not None or ssh_port is not None or ssh_identity_file is not None

    command = ["rsync", *resolved_options]
    if blocking_io:
        command.append("--blocking-io")
    if inject_ssh:
        command += ["-e", _build_ssh_transport_argument(ssh_port, ssh_identity_file)]

    remote_target = f"{ssh_user}@{ssh_host}" if ssh_user is not None else ssh_host
    src_str, dst_str = str(src), str(dst)
    if inject_ssh and remote_side == "src":
        src_str = f"{remote_target}:{src_str}"
    elif inject_ssh and remote_side == "dst":
        dst_str = f"{remote_target}:{dst_str}"
    command += [src_str, dst_str]
    return command
