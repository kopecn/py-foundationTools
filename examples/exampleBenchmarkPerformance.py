"""
Benchmark: transaction frequency and round-trip latency across the two transport
families this library ships.

- CLITransact  — a subprocess is forked/exec'd for every single call. Simple and
  universal, but process creation dominates the cost of each round trip.
- TransactingSocketHandlerClient/Server — one persistent, synchronous threaded
  TCP connection; each transaction is just a framed byte round trip over an
  already-open socket.

Running both side by side makes the trade-off concrete: sockets buy roundtrip
frequency at the cost of a stateful, long-lived connection to manage; CLI buys
simplicity (any shell command, no server to run) at the cost of per-call process
overhead. Neither is "faster" in the abstract — this script measures which is
faster *for repeated small round trips*, which is the case a persistent-transport
layer exists to address.

Run:
    python examples/exampleBenchmarkPerformance.py [iterations]

``iterations`` (default 200) governs the socket benchmark; the CLI benchmarks use
iterations // 10 (minimum 10) since process-spawn cost makes the full count slow.
Uses only the standard library — no plotting/analysis dependency, consistent with
this project's zero-runtime-dependency rule.
"""

import asyncio
import logging
import queue
import statistics
import sys
import threading
import time
from dataclasses import dataclass

from foundation_tools.cli_transaction.cliTransact import CLITransact
from foundation_tools.socket_transaction import (
    InboundTransaction,
    JsonTransactionCodec,
    TransactingSocketHandlerClient,
    TransactingSocketHandlerServer,
    TransactionOutcome,
)

DEFAULT_ITERATIONS = 200
MIN_CLI_ITERATIONS = 10
CLI_ITERATION_FRACTION = 10
_TIMEOUT = 10.0
_LOGGER = logging.getLogger("examples.benchmark_performance")


@dataclass
class BenchmarkResult:
    label: str
    iterations: int
    total_seconds: float
    latencies_ms: list[float]

    @property
    def transactions_per_second(self) -> float:
        return self.iterations / self.total_seconds if self.total_seconds > 0 else float("inf")


def _percentile(ordered_samples: list[float], fraction: float) -> float:
    index = min(len(ordered_samples) - 1, int(len(ordered_samples) * fraction))
    return ordered_samples[index]


def _print_result(result: BenchmarkResult) -> None:
    ordered = sorted(result.latencies_ms)
    print(f"\n{result.label}")
    print(f"  iterations       : {result.iterations}")
    print(f"  throughput       : {result.transactions_per_second:,.1f} transactions/sec")
    print(f"  latency mean     : {statistics.fmean(ordered):.3f} ms")
    p50, p95 = _percentile(ordered, 0.50), _percentile(ordered, 0.95)
    print(f"  latency p50/p95  : {p50:.3f} / {p95:.3f} ms")
    print(f"  latency min/max  : {ordered[0]:.3f} / {ordered[-1]:.3f} ms")


def benchmark_cli_sync(iterations: int) -> BenchmarkResult:
    latencies_ms: list[float] = []
    start = time.perf_counter()
    for _ in range(iterations):
        t0 = time.perf_counter()
        result = CLITransact.run_sync("echo ping", timeout=5, success_marker="ping")
        latencies_ms.append((time.perf_counter() - t0) * 1000)
        assert result.success
    total = time.perf_counter() - start
    return BenchmarkResult(
        "CLITransact.run_sync — one subprocess per call", iterations, total, latencies_ms
    )


async def benchmark_cli_async(iterations: int) -> BenchmarkResult:
    latencies_ms: list[float] = []
    start = time.perf_counter()
    for _ in range(iterations):
        t0 = time.perf_counter()
        result = await CLITransact.run_async("echo ping", timeout=5, success_marker="ping")
        latencies_ms.append((time.perf_counter() - t0) * 1000)
        assert result.success
    total = time.perf_counter() - start
    return BenchmarkResult(
        "CLITransact.run_async — one subprocess per call", iterations, total, latencies_ms
    )


def _echo_handler(inbound: InboundTransaction) -> None:
    inbound.reply("ack", 0)
    inbound.reply("res", 0, payload=inbound.frame.payload)


def benchmark_socket_roundtrip(iterations: int) -> BenchmarkResult:
    server = TransactingSocketHandlerServer(_LOGGER, JsonTransactionCodec())
    server.set_inbound_transaction_handler(_echo_handler)
    server.listen(0)
    try:
        address = server.listening_address
        assert address is not None
        client = TransactingSocketHandlerClient(_LOGGER, JsonTransactionCodec())
        try:
            client.connect(*address, timeout=_TIMEOUT)
            assert server.wait_for_connection(_TIMEOUT) is True

            latencies_ms: list[float] = []
            start = time.perf_counter()
            for i in range(iterations):
                t0 = time.perf_counter()
                outcome = client.send_transaction(
                    "request", 0, f"payload-{i}", wait_ack=True, wait_result=True, timeout=_TIMEOUT
                )
                latencies_ms.append((time.perf_counter() - t0) * 1000)
                assert outcome.success
            total = time.perf_counter() - start
        finally:
            client.disconnect()
    finally:
        server.stop()

    return BenchmarkResult(
        "TransactingSocketHandlerClient.send_transaction — persistent TCP connection",
        iterations,
        total,
        latencies_ms,
    )


def benchmark_socket_concurrent(iterations: int, concurrency: int = 20) -> BenchmarkResult:
    """Same round trip, but fired with `concurrency` requests in flight at once —
    the shape a persistent connection is built for (CLITransact has no analogous
    mode: each call is already a fresh, independent process). Each in-flight
    request runs on its own worker thread; the transacting client serializes
    outbound wire bytes internally, so concurrent callers never interleave."""
    server = TransactingSocketHandlerServer(_LOGGER, JsonTransactionCodec())
    server.set_inbound_transaction_handler(_echo_handler)
    server.listen(0)
    try:
        address = server.listening_address
        assert address is not None
        client = TransactingSocketHandlerClient(_LOGGER, JsonTransactionCodec())
        try:
            client.connect(*address, timeout=_TIMEOUT)
            assert server.wait_for_connection(_TIMEOUT) is True

            latencies: queue.Queue[float] = queue.Queue()
            pending = queue.Queue()
            for i in range(iterations):
                pending.put(i)
            semaphore = threading.Semaphore(concurrency)

            def one_request(i: int) -> None:
                t0 = time.perf_counter()
                outcome = client.send_transaction(
                    "request",
                    0,
                    f"payload-{i}",
                    wait_ack=True,
                    wait_result=True,
                    timeout=_TIMEOUT,
                )
                assert outcome.success
                latencies.put((time.perf_counter() - t0) * 1000)
                semaphore.release()

            start = time.perf_counter()
            workers: list[threading.Thread] = []
            for i in range(iterations):
                semaphore.acquire()
                worker = threading.Thread(target=one_request, args=(i,))
                worker.start()
                workers.append(worker)
            for worker in workers:
                worker.join(timeout=_TIMEOUT)
            total = time.perf_counter() - start

            latencies_ms = [latencies.get_nowait() for _ in range(iterations)]
        finally:
            client.disconnect()
    finally:
        server.stop()

    return BenchmarkResult(
        f"TransactingSocketHandlerClient.send_transaction — {concurrency} concurrent in flight",
        iterations,
        total,
        latencies_ms,
    )


async def main() -> None:
    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_ITERATIONS
    cli_iterations = max(MIN_CLI_ITERATIONS, iterations // CLI_ITERATION_FRACTION)

    print("Benchmarking pyFoundationTools transaction round trips")
    print(f"(socket iterations={iterations}, CLI iterations={cli_iterations} — see docstring)")

    cli_sync = benchmark_cli_sync(cli_iterations)
    _print_result(cli_sync)

    cli_async = await benchmark_cli_async(cli_iterations)
    _print_result(cli_async)

    socket_sequential = benchmark_socket_roundtrip(iterations)
    _print_result(socket_sequential)

    socket_concurrent = benchmark_socket_concurrent(iterations)
    _print_result(socket_concurrent)

    print("\nSummary:")
    speedup = socket_sequential.transactions_per_second / cli_sync.transactions_per_second
    print(
        f"  Sequential socket round trips ran ~{speedup:,.0f}x more frequently per second"
        " than CLI subprocess round trips — expected: a socket transaction reuses one"
        " open connection, a CLI transaction forks+execs a new process every call."
    )
    concurrent_speedup = (
        socket_concurrent.transactions_per_second / socket_sequential.transactions_per_second
    )
    print(
        f"  Concurrent in-flight socket requests raised throughput a further"
        f" ~{concurrent_speedup:,.1f}x over one-at-a-time requests on the same connection."
    )


if __name__ == "__main__":
    asyncio.run(main())
