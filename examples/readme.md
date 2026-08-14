# Examples

Runnable scripts demonstrating how to use `pyFoundationTools`. Each file is
self-contained and runs standalone: `python examples/<file>.py`. Install the
package first (`make devInstall` / `make e`, or `uv-sync`).

| File | Demonstrates |
| --- | --- |
| [`exampleDataModel.py`](exampleDataModel.py) | `DataModelHelper`: file save/load round-trip, `CLITransact.run_sync_with_model` parsing `df -h` into a `DiskUsage` model, dict/JSON round-trip. |
| [`exampleTransactCLI.py`](exampleTransactCLI.py) | `CLITransact`: sync/async execution, string vs. list argv, and that failures return a result rather than raising. |
| [`exampleTransactSSH.py`](exampleTransactSSH.py) | `SSHTransact`: sync/async execution over SSH, composed with a `RetryPolicy`. Targets `localhost`; requires a local SSH server to actually succeed, but demonstrates the never-raise contract either way. |
| [`exampleTransactRsync.py`](exampleTransactRsync.py) | `RsyncTransact`: a local-to-local sync (no SSH needed to run), plus the build-time `ValueError` guard against host-less SSH injection. |
| [`exampleRetryPolicy.py`](exampleRetryPolicy.py) | `BackoffPolicy` + `RetryPolicy` composed over a simulated transiently-failing `CLITransact` call, and non-transient failures stopping immediately. |
| [`exampleSocketClientServer.py`](exampleSocketClientServer.py) | `SocketTransact` + `SocketTransactServer`: a single request/reply round trip, concurrent out-of-order requests, and the server-push (unsolicited) channel. |
| [`exampleBenchmarkPerformance.py`](exampleBenchmarkPerformance.py) | Transaction frequency/latency benchmark comparing `CLITransact` (subprocess per call) against `SocketTransact` (persistent connection), sequential and concurrent. Accepts an optional iteration count: `python examples/exampleBenchmarkPerformance.py 500`. |

## Which transport should I use?

- **One-off or scripted commands** (deploys, health checks, file transfers) →
  `CLITransact` / `SSHTransact` / `RsyncTransact`. No server process to manage;
  each call is an independent subprocess.
- **Frequent, low-latency request/reply, or a server pushing data to clients** →
  `SocketTransact` / `SocketTransactServer`. Pays for a persistent connection in
  exchange for much higher round-trip frequency — see
  `exampleBenchmarkPerformance.py` for measured numbers.

See `.claude/specs/transport_transaction_architecture.md` for the full layer
model behind both families.
