"""
This example shows usage for RsyncTransact: a thin transaction that builds an
rsync argv via `build_rsync_command` and delegates execution to CLITransact
unchanged. Requires the `rsync` binary on PATH (preinstalled on macOS/Linux).

Two things are demonstrated:
1. A local-to-local sync (no SSH involved) so the example runs unattended.
2. The build-time validation guard added for host-less SSH injection: supplying
   `ssh_port`/`ssh_identity_file` without `ssh_host` is a caller bug (it would
   otherwise format an invalid remote address like "None:/path"), so the
   builder raises `ValueError` *before* any subprocess is spawned — this is the
   one place in the stack where an exception is the correct contract, because
   it is a construction-time error, not an execution outcome.
"""

import tempfile
from pathlib import Path

from foundation_tools.cli_transaction.rsyncTransact import RsyncTransact


def run_local_sync() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "src"
        dst = Path(tmp) / "dst"
        src.mkdir()
        dst.mkdir()
        (src / "hello.txt").write_text("hello from rsync\n")

        # "-a" (archive mode, implies recursion) — rsync applies no defaults of
        # its own, so recursion must be requested explicitly.
        result = RsyncTransact.run_sync(src=f"{src}/", dst=str(dst), options=["-a"], timeout=10)
        print(result)
        print(f"synced files: {[p.name for p in dst.iterdir()]}")


def run_host_less_ssh_guard() -> None:
    """ssh_port supplied without ssh_host raises ValueError at build time —
    caught here only to demonstrate the guard; production callers should treat
    this as a programming error to fix, not a runtime condition to handle."""
    try:
        RsyncTransact.run_sync(src="/local/path", dst="/remote/path", ssh_port=2222)
    except ValueError as error:
        print(f"build-time guard triggered as expected: {error}")


if __name__ == "__main__":
    run_local_sync()
    run_host_less_ssh_guard()
