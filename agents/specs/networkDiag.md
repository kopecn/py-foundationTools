---
spec: NetworkDiag
scope: project
status: implemented
applies_to: src/foundation_tools/network_diag/
last_updated: 2026-10-03
semver: 0.3.0
author: Nicholas Bergantz
---

# Network Diagnostics Collector Specification

## Overview

`network_diag` is a read-only, collect-only diagnostics suite that captures the
network state of a Linux host and emits a structured report. It exists to freeze
ground-truth evidence **at the time of a failure, before any remediation**, so a
later analysis (human or LLM) reasons about the actual failed state rather than a
state already perturbed by trial-and-error fixes.

Its intended habitat is a host whose network may be broken. It therefore depends
on nothing beyond the Python standard library and the host's own system tools,
and attempts no installation, no configuration, and no network of its own.

## Scope

It is responsible for:

- running a declarative suite of read-only probe commands, each modeled as a
  schema-generated command model (the DiskUsage wire pattern, scaled per command)
- running those probes concurrently, each bounded by its own timeout
- containing every probe failure (missing tool, non-zero exit, timeout)
- assembling a typed, serializable report that carries both the parsed command
  model and the verbatim captured stdout
- rendering that report as JSON (for machine/LLM ingestion) and as human text
- writing the report to disk and relaying it to stdout
- collecting from the local host or, with `--host`, from a remote host over SSH

It is **not** responsible for:

- changing any host state (never mutates — see [Collect-only](#collect-only))
- remediating faults
- uploading the report (a separate, later step once connectivity is restored)
- interpreting or diagnosing the collected evidence

Execution, timeout, and exception containment are delegated entirely to the
transport layer — `CLITransact` locally, `SSHTransact` for `--host` (see
[cliTransact.md](cliTransact.md), [sshTransact.md](sshTransact.md)).

---

# System Role

```
network-diag (CLI)
      │
      ▼
run_probes  ──►  Probe (declarative) ──► command model (wire_invoke = read-only argv,
      │                                   from_wire = stdout parser)
      │  asyncio.gather (concurrent, per-probe timeout)
      ▼
CLITransact.run_async_with_model(Model)         (local; argv + parser from the model)
  or SSHTransact.run_async_with_model(          (remote; command + output_parser passed)
        command=Model.wire_invoke, output_parser=Model.from_wire, host=...)
      │   (no shell, argv-direct, total containment)
      ▼
subprocess / ssh  ──►  host system tools (ip, nmcli, iw, ss, ping, ...)
```

---

# Command Models

Each probe command is a schema-generated `DataModelHelper` model, scaling the
DiskUsage wire pattern (see [dataModelHelper.md](dataModelHelper.md),
[schemaCodegen.md](schemaCodegen.md)) to every command:

- Each command is fully self-contained — its own schema, codegen script, generated
  module, and wire binding — so commands have no interdependence:
  - Per-command JSON Schemas live under `schema/schemas/CLITools/` (which also holds
    `DiskUsage-schema.json`).
  - One per-command codegen script under `schema/scripts/CLITools/` (modeled on the
    golden `generateDiskUsage.sh`) generates that command's model into its own package
    `src/foundationTypes/commonTypes/cli_types/<command>/<Model>.py`. `DiskUsage`
    (`df -h`) is the original exemplar of this shape and lives alongside at
    `commonTypes/cli_types/disk_usage/`.
  - The hand-written sibling `<command>/wire_config.py` binds that model's
    `wire_invoke` (the read-only argv) and `wire_decode` (the stdout parser); the
    package `__init__.py` imports it for its side effect, so importing the command's
    package activates the binding.
- `make codegen-all` discovers and runs every script under `schema/scripts/`
  recursively (excluding `reuse/`).
- Parser fidelity: tabular/stable formats (`ip -brief`, `ip route`, `ip neigh`,
  `ss -tulpnH`, `lsmod`, `nmcli device status`, the `key: value`/`KEY=VALUE` status
  reports, and `ping`) are parsed into structured fields and unit-tested against
  representative fixtures. Freeform or highly variable output is captured verbatim
  into a `raw` field so the report preserves exact ground-truth evidence.

---

# Collect-only

Every probe in the suite MUST be read-only. The collector constructs no mutating
command and executes only the `argv` declared on a `Probe`. Probes run as
argv vectors with no shell, so there is no shell interpretation of probe strings.
Running the collector MUST NOT change host network state.

Elevated capture (some probes, e.g. `dmesg`, `nft`, process owners in `ss`,
require root) is obtained only by the caller choosing to invoke the tool under
`sudo`. The tool never escalates privilege on its own; absent privilege it
records the probe's non-zero result and continues.

---

# Probe Model

A `Probe` is a declarative description of one read-only command:

| field         | meaning                                                      |
| ------------- | ------------------------------------------------------------ |
| `name`        | stable identifier, unique within the suite                   |
| `category`    | grouping key for the report (e.g. `wifi`, `dns`)             |
| `description` | one line on what the probe answers                           |
| `model`       | the command model; its `wire_invoke` holds the read-only argv |
| `timeout_s`   | per-probe wall-clock budget (default 10s)                    |

The `model`'s `wire_invoke` MUST be a non-empty `list[str]` argv (enforced at
`Probe` construction); `Probe.argv`/`Probe.binary` read from it. The suite is
**extended by adding a command model** (author a schema under
`schema/schemas/CLITools/`, regenerate, bind it in `wire_config.py`) and
appending a `Probe` that references it; no control-flow change is required.
(Runtime JSON probe-file loading, present in the first MVP, is removed — an
arbitrary raw-argv command has no typed model and no parser.)

---

# Execution Contract

Probes run **concurrently** (`asyncio.gather`), each bounded by its own timeout.
For each selected probe:

1. On a **local** run, if `argv[0]` is not found on `PATH` the probe is **skipped**
   — recorded as `ProbeStatus.SKIPPED` with an explanatory stderr and no execution.
   On an **SSH** run the remote `PATH` cannot be inspected, so a missing remote tool
   surfaces as `ERROR` rather than `SKIPPED`.
2. Otherwise the probe runs via `run_async_with_model` — locally
   `CLITransact.run_async_with_model(model)` (the bare-model form, pulling the argv
   from `wire_invoke` and parsing with `from_wire`), or remotely
   `SSHTransact.run_async_with_model(command=model.wire_invoke,
   output_parser=model.from_wire, host=...)`. Execution is argv-direct, no shell.
3. The outcome maps to `ProbeStatus.OK` on success (exit 0), `ProbeStatus.TIMEOUT`
   when the transport reports a timeout, else `ProbeStatus.ERROR`. On success the
   parsed command model is attached (as a plain dict); parsing is advisory and never
   changes the execution outcome. Timeouts and framework errors are contained by the
   transport and surface with their captured stderr.

A probe failure or timeout never aborts the run. Collection always completes over
the full selected set, and result order matches suite order regardless of
completion order.

---

# Report

`DiagnosticReport` carries host identity (`hostname`), UTC `generated_at`, the
collector `tool_version`, and the ordered `ProbeResult`s. Each `ProbeResult` carries
its `status`, `return_code`, the parsed command model (`model`, a dict, or `null`),
the verbatim `stdout`, `stderr`, and `duration_s`. The report serializes to a stable
JSON shape tagged `"schema": "network-diag/2"` (bumped from `/1`: results now carry
the parsed `model` and the argv is derived from the model). The text rendering groups
results by category in first-seen order.

---

# Output

The CLI writes a timestamped JSON artifact and a human-readable text artifact to
the output directory (default: the current directory) and relays the text to
stdout. `--no-file` suppresses the files; `--json` relays JSON to stdout instead
of text. `--category NAME` (repeatable) restricts the suite; `--list` prints the
selected probes and exits. `--host HOST` (with optional `--user`, `--port`,
`--identity-file`) collects from a remote host over SSH instead of locally. File
writes are the durable, time-of-failure artifact.

The process exits 0 on a completed collection regardless of individual probe
outcomes; a non-zero exit indicates a usage error only.

---

# Compliance Requirements

A compliant `network_diag` MUST:

1. execute only read-only commands and never mutate host state
2. run each probe through its command model's `wire_invoke` argv as an argv vector
   with no shell
3. delegate all execution, timeout, and exception handling to the transport layer
   (`CLITransact` locally, `SSHTransact` for `--host`) via `run_async_with_model`
4. on a local run, skip (not fail) a probe whose tool is absent from `PATH`
5. bound each probe by its own timeout and record a timed-out probe as `TIMEOUT`
6. let no single probe failure or timeout abort the overall run
7. complete collection over the full selected probe set
8. produce a JSON report with a stable, versioned schema tag that carries each
   probe's parsed command model alongside its verbatim stdout
9. write the report to disk and relay it to stdout
10. allow the suite to be extended declaratively (new command model + registry
    entry) without control-flow changes
11. exit 0 on a completed collection irrespective of probe outcomes
