"""
This example shows simple usage for CLITransact
"""

import asyncio

from foundationCLIHelpers.cliTransact import CLITransact, CLITransactResult


def runSync():
    result: CLITransactResult = CLITransact.run_sync(
        "echo hello", timeout=5, success_marker="hello"
    )
    print(result)


async def run_async():
    result: CLITransactResult = await CLITransact.run_async(
        "echo hello", timeout=5, success_marker="hello"
    )
    print(result)


if __name__ == "__main__":
    runSync()
    asyncio.run(run_async())
