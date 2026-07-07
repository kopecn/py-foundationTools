"""
This example shows the socket-transaction stack end to end: SocketTransactServer
(server role) and SocketTransact (client facade) over a real loopback TCP
connection. Unlike CLITransact, this is a long-lived, asyncio-native connection —
one process fork/exec per CLI call vs. many request/reply round trips over one
already-open socket (see exampleBenchmarkPerformance.py for the throughput
difference this makes).

The stack needs a tx_id correlation pair (injector/extractor) because the wire
format is protocol-specific — this stack defines none of its own. The example
uses the minimal "tx_id:" prefix scheme also used throughout the test suite.

Three things are demonstrated:
1. A single request/reply round trip.
2. Several concurrent requests resolving correctly out of order (the router
   correlates replies to requests by tx_id, not by send order).
3. The unsolicited channel: a server-initiated broadcast that the client reads
   as an async iterator, independent of the correlated request/reply channel.
"""

import asyncio

from foundation_tools.socket_transaction.framing_codecs import DelimiterCodec
from foundation_tools.socket_transaction.socketTransact import SocketTransact
from foundation_tools.socket_transaction.socketTransactServer import SocketTransactServer


def _stamp_tx_id(payload: bytes, tx_id: str) -> bytes:
    """Prefix `tx_id:` onto payload — the reply is correlated back to whichever
    request supplied that tx_id."""
    return f"{tx_id}:".encode() + payload


def _read_tx_id(frame: bytes) -> str | None:
    prefix, sep, _ = frame.partition(b":")
    return prefix.decode("ascii") if sep else None


def _strip_tx_id(frame: bytes) -> bytes:
    """Drop the `tx_id:` prefix — handlers see the full stamped frame but should
    return a bare reply body; the server re-stamps it with the same tx_id."""
    _prefix, sep, body = frame.partition(b":")
    return body if sep else frame


async def echo_handler(request: bytes) -> bytes | None:
    """Server-side handler: echoes the request body back as the reply."""
    return _strip_tx_id(request)


async def example_single_round_trip() -> None:
    print("=== Single Request/Reply Round Trip ===")
    async with SocketTransactServer(
        "127.0.0.1",
        0,  # ephemeral port — read back via server.address
        echo_handler,
        tx_id_injector=_stamp_tx_id,
        tx_id_extractor=_read_tx_id,
        codec_factory=DelimiterCodec,
    ) as server:
        host, port = server.address
        async with SocketTransact(
            host,
            port,
            tx_id_injector=_stamp_tx_id,
            tx_id_extractor=_read_tx_id,
            codec=DelimiterCodec(),
        ) as client:
            result = await client.request(b"hello-server", timeout=5.0)
            print(f"success={result.success} payload={result.payload!r}")
    print()


async def example_concurrent_out_of_order() -> None:
    print("=== Concurrent Requests, Resolved Out of Order ===")

    async def randomized_delay_echo(request: bytes) -> bytes | None:
        import random

        await asyncio.sleep(random.uniform(0, 0.03))  # noqa: S311 - demo jitter only
        return _strip_tx_id(request)

    async with SocketTransactServer(
        "127.0.0.1",
        0,
        randomized_delay_echo,
        tx_id_injector=_stamp_tx_id,
        tx_id_extractor=_read_tx_id,
        codec_factory=DelimiterCodec,
    ) as server:
        host, port = server.address
        async with SocketTransact(
            host,
            port,
            tx_id_injector=_stamp_tx_id,
            tx_id_extractor=_read_tx_id,
            codec=DelimiterCodec(),
            poll_timeout=0.02,
        ) as client:
            tasks = [
                asyncio.ensure_future(client.request(f"payload-{i}".encode(), timeout=2.0))
                for i in range(5)
            ]
            results = await asyncio.gather(*tasks)

    for i, result in enumerate(results):
        print(f"  request {i}: success={result.success} payload={result.payload!r}")
    print()


async def example_server_push_unsolicited() -> None:
    print("=== Server Push (Unsolicited Channel) ===")

    async def silent_handler(_request: bytes) -> bytes | None:
        return None  # this handler never replies; all traffic here is server-pushed

    async with SocketTransactServer(
        "127.0.0.1",
        0,
        silent_handler,
        tx_id_injector=_stamp_tx_id,
        tx_id_extractor=_read_tx_id,
        codec_factory=DelimiterCodec,
    ) as server:
        host, port = server.address
        async with SocketTransact(
            host,
            port,
            tx_id_injector=_stamp_tx_id,
            tx_id_extractor=_read_tx_id,
            codec=DelimiterCodec(),
        ) as client:
            await asyncio.sleep(0.05)  # let the connection register before pushing
            await server.broadcast(b"server-announcement")

            frame = await asyncio.wait_for(anext(client.unsolicited()), timeout=2.0)
            print(f"received unsolicited push: {frame!r}")
    print()


async def main() -> None:
    await example_single_round_trip()
    await example_concurrent_out_of_order()
    await example_server_push_unsolicited()


if __name__ == "__main__":
    asyncio.run(main())
