"""Usage examples for RsyncTransact: builds an rsync argv, delegates to CLITransact. Needs rsync."""

import tempfile
from pathlib import Path

from foundation_tools.cli_transaction.rsyncTransact import RsyncTransact

print("---- local-to-local sync ----")
with tempfile.TemporaryDirectory() as tmp:
    src = Path(tmp) / "src"
    dst = Path(tmp) / "dst"
    src.mkdir()
    dst.mkdir()
    (src / "hello.txt").write_text("hello from rsync\n")

    # "-a" archive mode; rsync applies no default recursion of its own.
    print(RsyncTransact.run_sync(src=f"{src}/", dst=str(dst), options=["-a"], timeout=10))
    print(f"synced files: {[p.name for p in dst.iterdir()]}")

print("\n---- host-less ssh guard (raises at build time) ----")
try:
    RsyncTransact.run_sync(src="/local/path", dst="/remote/path", ssh_port=2222)
except ValueError as error:
    print(f"guard triggered: {error}")
