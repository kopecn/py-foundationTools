"""
This example shows simple usage for CLITransact: the stateless, never-raising
process-transaction facade. Every call returns a CLITransactResult regardless of
outcome (timeout, non-zero exit, exception) — there is nothing to try/except.
"""

import asyncio

from foundation_tools.cli_transaction.cliTransact import CLITransact, CLITransactResult


def run_sync() -> None:
    result: CLITransactResult = CLITransact.run_sync(
        "echo hello", timeout=5, success_marker="hello"
    )
    print(result)


async def run_async() -> None:
    result: CLITransactResult = await CLITransact.run_async(
        "echo hello", timeout=5, success_marker="hello"
    )
    print(result)


def run_sync_list_argv() -> None:
    """List-argv form: executed directly (no shell), so it is preferred over a
    string command whenever the pieces aren't a shell one-liner."""
    result: CLITransactResult = CLITransact.run_sync(["echo", "hello, argv"], timeout=5)
    print(result)


def run_sync_failure_never_raises() -> None:
    """A failing command still returns a result — never an exception."""
    result: CLITransactResult = CLITransact.run_sync("exit 7", timeout=5)
    print(f"success={result.success} return_code={result.return_code}")


if __name__ == "__main__":
    run_sync()
    asyncio.run(run_async())
    run_sync_list_argv()
    run_sync_failure_never_raises()
