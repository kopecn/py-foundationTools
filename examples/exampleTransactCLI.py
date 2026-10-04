"""Usage examples for CLITransact: never raises — every call returns a CLITransactResult."""

import asyncio

from foundation_tools.cli_transaction.cliTransact import CLITransact

print("---- sync ----")
print(CLITransact.run_sync("echo hello", timeout=5, success_marker="hello"))

print("\n---- async ----")
print(asyncio.run(CLITransact.run_async("echo hello", timeout=5, success_marker="hello")))

print("\n---- list argv (no shell, preferred) ----")
print(CLITransact.run_sync(["echo", "hello, argv"], timeout=5))

print("\n---- failure never raises ----")
result = CLITransact.run_sync("exit 7", timeout=5)
print(f"success={result.success} return_code={result.return_code}")
