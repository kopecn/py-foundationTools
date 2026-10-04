"""Benchmark: CLITransact (one subprocess per call) vs the threaded socket stack (one
persistent connection) over repeated small round trips. Optional arg sets socket
iterations (default 200); CLI uses a tenth of that."""

import asyncio
import logging
import statistics
import sys
import threading
import time

from foundation_tools.cli_transaction.cliTransact import CLITransact
from foundation_tools.socket_transaction import (
    InboundTransaction,
    JsonTransactionCodec,
    TransactingSocketHandlerClient,
    TransactingSocketHandlerServer,
)

_LOGGER = logging.getLogger("examples.benchmark_performance")
_TIMEOUT = 10.0


def report(label: str, latencies_ms: list[float], total_s: float) -> None:
    tps = len(latencies_ms) / total_s if total_s else float("inf")
    mean = statistics.fmean(latencies_ms)
    print(f"{label}: {tps:,.0f} tx/s, mean {mean:.3f} ms ({len(latencies_ms)} iters)")


def echo_handler(inbound: InboundTransaction) -> None:
    inbound.reply("ack", 0)
    inbound.reply("res", 0, payload=inbound.frame.payload)


def bench_cli_sync(iterations: int) -> None:
    latencies, start = [], time.perf_counter()
    for _ in range(iterations):
        t0 = time.perf_counter()
        assert CLITransact.run_sync("echo ping", timeout=5, success_marker="ping").success
        latencies.append((time.perf_counter() - t0) * 1000)
    report("CLITransact.run_sync (subprocess per call)", latencies, time.perf_counter() - start)


async def bench_cli_async(iterations: int) -> None:
    latencies, start = [], time.perf_counter()
    for _ in range(iterations):
        t0 = time.perf_counter()
        result = await CLITransact.run_async("echo ping", timeout=5, success_marker="ping")
        assert result.success
        latencies.append((time.perf_counter() - t0) * 1000)
    report("CLITransact.run_async (subprocess per call)", latencies, time.perf_counter() - start)


def bench_socket_sequential(iterations: int) -> None:
    server = TransactingSocketHandlerServer(_LOGGER, JsonTransactionCodec())
    server.set_inbound_transaction_handler(echo_handler)
    server.listen(0)
    host, port = server.listening_address
    client = TransactingSocketHandlerClient(_LOGGER, JsonTransactionCodec())
    client.connect(host, port, timeout=_TIMEOUT)
    server.wait_for_connection(_TIMEOUT)

    latencies, start = [], time.perf_counter()
    for i in range(iterations):
        t0 = time.perf_counter()
        outcome = client.send_transaction(
            "request", 0, f"p-{i}", wait_ack=True, wait_result=True, timeout=_TIMEOUT
        )
        assert outcome.success
        latencies.append((time.perf_counter() - t0) * 1000)
    report("socket send_transaction (persistent conn)", latencies, time.perf_counter() - start)

    client.disconnect()
    server.stop()


def bench_socket_concurrent(iterations: int, concurrency: int = 20) -> None:
    server = TransactingSocketHandlerServer(_LOGGER, JsonTransactionCodec())
    server.set_inbound_transaction_handler(echo_handler)
    server.listen(0)
    host, port = server.listening_address
    client = TransactingSocketHandlerClient(_LOGGER, JsonTransactionCodec())
    client.connect(host, port, timeout=_TIMEOUT)
    server.wait_for_connection(_TIMEOUT)

    latencies: list[float] = []
    lock = threading.Lock()
    semaphore = threading.Semaphore(concurrency)

    def one_request(i: int) -> None:
        t0 = time.perf_counter()
        outcome = client.send_transaction(
            "request", 0, f"p-{i}", wait_ack=True, wait_result=True, timeout=_TIMEOUT
        )
        assert outcome.success
        with lock:
            latencies.append((time.perf_counter() - t0) * 1000)
        semaphore.release()

    start = time.perf_counter()
    workers = []
    for i in range(iterations):
        semaphore.acquire()
        worker = threading.Thread(target=one_request, args=(i,))
        worker.start()
        workers.append(worker)
    for worker in workers:
        worker.join(timeout=_TIMEOUT)
    label = f"socket send_transaction ({concurrency} concurrent)"
    report(label, latencies, time.perf_counter() - start)

    client.disconnect()
    server.stop()


if __name__ == "__main__":
    socket_iters = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    cli_iters = max(10, socket_iters // 10)

    bench_cli_sync(cli_iters)
    asyncio.run(bench_cli_async(cli_iters))
    bench_socket_sequential(socket_iters)
    bench_socket_concurrent(socket_iters)
