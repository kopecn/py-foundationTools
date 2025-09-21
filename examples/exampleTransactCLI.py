"""
This example shows simple usage for CLITransact
"""

import asyncio
from foundationCLIHelpers.cliTransact import CLITransact, CLITransactResult


def runSync():
    cli = CLITransact(success_string="hello")
    result: CLITransactResult = cli.run_sync("echo hello", timeout=5)
    print(result)


async def run_async():
    cli = CLITransact(success_string="hello")
    result: CLITransactResult = await cli.run_async("echo hello", timeout=5)
    print(result)


if __name__ == "__main__":
    runSync()
    asyncio.run(run_async())
