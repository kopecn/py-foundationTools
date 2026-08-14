"""
Benchmark: transaction frequency and round-trip latency across the two transport
families this library ships.

- CLITransact  — a subprocess is forked/exec'd for every single call. Simple and
  universal, but process creation dominates the cost of each round trip.
- SocketTransact/SocketTransactServer — one persistent asyncio TCP connection;
  each transaction is just a framed byte round trip over an already-open socket.

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
import statistics
import sys
import time
from dataclasses import dataclass

from foundation_tools.cli_transaction.cliTransact import CLITransact
from foundation_tools.socket_transaction.framing_codecs import DelimiterCodec
from foundation_tools.socket_transaction.socketTransact import SocketTransact
from foundation_tools.socket_transaction.socketTransactServer import SocketTransactServer

DEFAULT_ITERATIONS = 200
MIN_CLI_ITERATIONS = 10
CLI_ITERATION_FRACTION = 10


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


def _stamp_tx_id(payload: bytes, tx_id: str) -> bytes:
    return f"{tx_id}:".encode() + payload


def _read_tx_id(frame: bytes) -> str | None:
    prefix, sep, _ = frame.partition(b":")
    return prefix.decode("ascii") if sep else None


def _strip_tx_id(frame: bytes) -> bytes:
    """Drop the `tx_id:` prefix — handlers return a bare reply body; the server
    re-stamps it with the same tx_id."""
    _prefix, sep, body = frame.partition(b":")
    return body if sep else frame


async def benchmark_socket_roundtrip(iterations: int) -> BenchmarkResult:
    async def echo_handler(request: bytes) -> bytes | None:
        return _strip_tx_id(request)

    async with SocketTransactServer(
        "127.0.0.1",
        0,
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
            poll_timeout=0.005,
        ) as client:
            latencies_ms: list[float] = []
            start = time.perf_counter()
            for i in range(iterations):
                t0 = time.perf_counter()
                result = await client.request(f"payload-{i}".encode(), timeout=5.0)
                latencies_ms.append((time.perf_counter() - t0) * 1000)
                assert result.success
            total = time.perf_counter() - start

    return BenchmarkResult(
        "SocketTransact.request — persistent TCP connection", iterations, total, latencies_ms
    )


async def benchmark_socket_concurrent(iterations: int, concurrency: int = 20) -> BenchmarkResult:
    """Same round trip, but fired with `concurrency` requests in flight at once —
    the shape a persistent connection is built for (CLITransact has no analogous
    mode: each call is already a fresh, independent process)."""

    async def echo_handler(request: bytes) -> bytes | None:
        return _strip_tx_id(request)

    async with SocketTransactServer(
        "127.0.0.1",
        0,
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
            poll_timeout=0.005,
        ) as client:
            latencies_ms: list[float] = []

            async def one_request(i: int) -> None:
                t0 = time.perf_counter()
                result = await client.request(f"payload-{i}".encode(), timeout=10.0)
                assert result.success
                # Single-threaded event loop between await points — no lock needed.
                latencies_ms.append((time.perf_counter() - t0) * 1000)

            start = time.perf_counter()
            semaphore = asyncio.Semaphore(concurrency)

            async def bounded(i: int) -> None:
                async with semaphore:
                    await one_request(i)

            await asyncio.gather(*(bounded(i) for i in range(iterations)))
            total = time.perf_counter() - start

    return BenchmarkResult(
        f"SocketTransact.request — {concurrency} concurrent in flight",
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

    socket_sequential = await benchmark_socket_roundtrip(iterations)
    _print_result(socket_sequential)

    socket_concurrent = await benchmark_socket_concurrent(iterations)
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
