import asyncio
from foundationCLIHelpers.cliTransact import CLITransact, CLITransactResult


cli = CLITransact(success_string="hello")
result: CLITransactResult = cli.run_sync("echo hello", timeout=5)
print(result)


async def main():
    cli = CLITransact(success_string="hello")
    result: CLITransactResult = await cli.run_async("echo hello", timeout=5)
    print(result)


asyncio.run(main())
