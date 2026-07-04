---
spec: CLITransact
scope: project
status: partial
applies_to: src/foundation_tools/cli_transaction/cliTransact.py
last_updated: 2026-07-03
semver: 0.1.0
author: Nicholas Bergantz
---

# CLI Transaction Manager Specification

> **Status — partial.** The `CLITransact` execution kernel described below is
> **implemented** in `src/foundation_tools/cli_transaction/cliTransact.py` and matches
> this spec. The sibling layers — `SSHTransact`, `RsyncTransact`, the retry/backoff
> engine, and the Windows/MSYS2 reliability layer — are **planned, not yet
> implemented**; their sections are marked accordingly and describe target behavior
> only. Keep the kernel sections in sync with the code when the class changes.
>
> **Naming note.** The canonical package home is `foundation_tools.cli_transaction`
> (module `cliTransact.py`). Earlier drafts referenced `foundationCLIHelpers` and
> `automation_foundation_utils/cli_transact/`; those names are obsolete.
>
> This module is Layer 1 of the umbrella
> [transport_transaction_architecture.md](transport_transaction_architecture.md);
> consult it for the layer model, policy-ownership rule, and package layout.

## Overview

`cliTransact.py` provides the unified execution kernel for CLI commands. It is the
single source of truth for subprocess execution: all higher-level wrappers (SSH, rsync,
deployment tooling) MUST delegate execution to `CLITransact` and MUST NOT call
`subprocess` directly.

It is responsible for:

- synchronous execution
- asynchronous execution
- timeout handling
- output normalization
- success evaluation (including semantic validation)
- optional stdout → model transformation
- consistent error containment (no exceptions escape the API)

It is **not** responsible for: retries, backoff policies, transport construction (SSH,
rsync), or domain-specific command composition. Those belong to higher layers
(see [System Role](#system-role)).

## Design Philosophy

`CLITransact` is a deterministic execution kernel, not a workflow engine. Invariants:

- All failures are captured and returned as structured results, never raised.
- Execution semantics are consistent across sync and async paths.
- Output is always normalized.
- Success is a computed semantic property, not just a return code.
- Validation and parsing are layered, not embedded in execution logic.
- The public API is minimal and symmetric (sync/async × plain/model).
- The public API is **stateless**: it is four `@classmethod`s; the optional
  `success_marker` is supplied per call, not held as instance/global state.

## Constants

```python
SUCCESS_RETURN_CODE = 0
ERROR_RETURN_CODE = -1
```

`ERROR_RETURN_CODE` (`-1`) is the framework-level sentinel — reserved for timeouts,
invalid input, and internal execution failures. It is **never** a real subprocess exit
code. The semantic layering is:

| return_code | meaning |
| --- | --- |
| `0` | command succeeded (subject to `success_marker`) |
| `> 0` | command-defined error (native exit code) |
| `-1` | framework/runtime failure (timeout, invalid input, contained exception) |

## Core Data Types

### `CLITransactResult`

```python
@dataclass
class CLITransactResult:
    return_code: int
    stdout: str | None = None
    stderr: str | None = None
    success: bool = False
```

- `return_code` — subprocess exit code OR `ERROR_RETURN_CODE`.
- `stdout` / `stderr` — normalized string or `None` (see [Normalization](#output-normalization)).
- `success` — computed field (see [Success Evaluation](#success-evaluation)).

### `CLITransactResultModel[T]`

Extends `CLITransactResult` with `model: T | None = None`, where `T` is bound to
`DataModelHelper` (see [data_model_helper.md](data_model_helper.md)). The model is populated
**only** when `success is True`, `stdout is not None`, and the parser does not raise.

## Command Input Contract

All public APIs accept `str | list[str]`. The input *type* selects the execution mode —
a deliberate, core invariant (usability over strict safety enforcement, with an
injection warning in the docstrings):

| input | sync mode | async mode |
| --- | --- | --- |
| `str` | `subprocess.run(..., shell=True)` | `bash -c "<command>"` |
| `list[str]` | direct exec, no shell | `create_subprocess_exec(*cmd)`, no shell |

The async string path uses an explicit `bash -c` rather than `shell=True` for
containment consistency.

## Public API

`CLITransact` exposes exactly four `@classmethod`s. They are **stateless**: each
constructs a short-lived instance carrying the per-call `success_marker` and delegates to
a private implementation. `timeout` and `success_marker` are keyword-only.

| method | returns | notes |
| --- | --- | --- |
| `run_sync(command, *, timeout=None, success_marker=None)` | `CLITransactResult` | `subprocess.run`; timeout supported. |
| `run_async(command, *, timeout=None, success_marker=None)` | `CLITransactResult` | `create_subprocess_exec`; timeout via `asyncio.wait_for`. |
| `run_sync_with_model(command, output_parser, *, timeout=None, success_marker=None)` | `CLITransactResultModel[T]` | `run_sync` + post-parse. |
| `run_async_with_model(command, output_parser, *, timeout=None, success_marker=None)` | `CLITransactResultModel[T]` | `run_async` + post-parse. |

No public method raises; every path returns a complete result object.

## Success Evaluation

Success is not purely return-code based:

```python
success = (
    return_code == SUCCESS_RETURN_CODE
    and (success_marker is None or success_marker in stdout)
)
```

- A non-zero return code is always a failure.
- When `success_marker` is set it becomes a **required** substring of stdout
  (case-sensitive, partial match valid). It is a semantic validator — a lightweight
  CLI contract assertion — not a parser.

## Output Normalization

All stdout/stderr pass through `_normalize_output(value)`:

- `None` → `None`
- `""` → `None`
- whitespace-only → `None`
- otherwise → `value.strip()`

Absence of data is represented uniformly as `None`, which keeps downstream
serialization and logging clean.

## Encoding

Decoding stdout/stderr uses `errors="replace"` rather than strict decoding, on both the
sync path (`subprocess.run(..., text=True, errors="replace")`) and the async path
(`bytes.decode(errors="replace")`), including the timeout partial-capture decode
fallback. Invalid byte sequences degrade to Unicode replacement characters instead of
raising — an undecodable byte in otherwise-successful output must never be
misclassified as a generic `"Command execution failed"` framework error.

## Execution Failure Handling

Every failure mode returns a `CLITransactResult`:

| failure | return_code | stderr | success |
| --- | --- | --- | --- |
| empty/invalid command | `ERROR_RETURN_CODE` | `"Empty command provided"` | `False` |
| sync timeout | `ERROR_RETURN_CODE` | `"Timeout after X seconds"` (+ partial stdout if available; partial stderr, if available, appended on a new line) | `False` |
| async timeout | `ERROR_RETURN_CODE` | `"Timeout after X seconds"` | `False` |
| any other exception | `ERROR_RETURN_CODE` | `"Command execution failed: <error>"` | `False` |

### Total exception containment

The execution handlers catch `Exception` broadly so **no exception escapes the public
API**. `BaseException` (`KeyboardInterrupt` / `SystemExit`) is intentionally allowed to
propagate. The broad catch is a required design invariant and is annotated in code with
`# noqa: BLE001 # pylint: disable=broad-exception-caught`.

### Async timeout cleanup — forceful escalation

On async timeout the process is cleaned up with a graceful-then-forceful cascade:

```text
proc.terminate()                      # SIGTERM (graceful)
wait up to a short grace period
  └─ if still alive → proc.kill()     # SIGKILL (forceful escalation)
```

> **Corrected order.** An earlier draft specified `kill → graceful shutdown → escalate
> to terminate`. That ordering is a no-op: `kill()` sends SIGKILL, which is uncatchable
> and immediate, so a subsequent `terminate()` (SIGTERM) signals an already-dead
> process. The implementation uses the corrected `terminate → kill` escalation, which
> is the only ordering that realizes the stated intent (forceful cleanup cascade).
> Cleanup is best-effort — it is always attempted but never guaranteed to succeed.

The grace window is `min(GRACE_PERIOD_CAP_SECONDS, timeout)` — capped at the caller's
own `timeout` — rather than an unconditional fixed `1.0` seconds. This keeps worst-case
total time bounded by roughly `2 × timeout` instead of `timeout + GRACE_PERIOD_CAP_SECONDS`
regardless of how small `timeout` is; a short timeout no longer pays a disproportionate
fixed overhead before escalating to SIGKILL.

## Model Extension Layer

The `*_with_model` methods run the base execution method, construct the extended result,
and attempt parsing **only** when `success is True` and `stdout` exists. Serializer
behavior:

- `model = output_parser(stdout)` on success.
- On failure: the exception is **swallowed** (broad `Exception` catch — same containment
  invariant as execution), a diagnostic `"\nModel parsing failed: <error>"` is appended
  to stderr, and `success` is **not** modified. Bad or unparseable output never produces
  a misleading structured artifact, and raw execution truth always wins over structured
  convenience.

### Wire bridge

The canonical `output_parser` is `DataModelHelper.from_wire` (or `from_bytes` / a
`from_dict`-based parser) on a schema-generated model — see the
**Wire Serialization Bridge** section of
[transport_transaction_architecture.md](transport_transaction_architecture.md).
Ad-hoc parser classes should be the exception, not the norm.

## Learned Behaviors / Design Rationale

These were previously implicit in the implementation and are now formalized as
requirements. They encode real-world automation assumptions.

1. **Success is semantic, not syntactic.** A command can exit `0` yet be a logical
   failure (no-op, skipped, partial). `success_marker` is a poor-man's contract test for
   unreliable CLI tools.
2. **Empty output normalizes to `None`.** "No output" is treated as absence-of-data, not
   a valid empty string — reduces downstream noise and ambiguity.
3. **Validation failure returns a result, not an exception.** Uniform return objects for
   all failure modes keep orchestration/pipeline layers free of `try/except`.
4. **Shell vs exec is inferred from input type.** `str ⇒ shell`, `list ⇒ exec`. A
   deliberate convenience footgun, mitigated by docstring warnings.
5. **Async timeout uses a forceful cleanup cascade.** Graceful `terminate()` first,
   escalate to `kill()` only if ignored — real subprocesses sometimes ignore signals.
6. **Timeout is a result, not control flow.** Timeouts are normal outcomes for batch /
   orchestration callers, surfaced as `ERROR_RETURN_CODE` results.
7. **stdout is a success oracle, not just data.** stdout participates in the success
   decision because CLI tools are unreliable APIs.
8. **Model parsing is conditional on success.** Parsing is skipped on failure to avoid
   interpreting corrupted or partial output.
9. **Parsing errors are advisory.** They append to stderr and never change the execution
   success flag — execution truth over structured convenience.
10. **Async forces an explicit shell (`bash -c`).** More controlled than the sync
    implicit `shell=True`; the two paths stay semantically equivalent.
11. **A result object always exists.** No `None` returns, no exceptions to the caller —
    control-flow flattening that makes pipelines composable.
12. **`-1` is the universal framework sentinel.** It distinguishes framework-level
    failures (timeout, invalid input, contained exception) from CLI-native non-zero exit
    codes.

## Key Behavioral Guarantees

- Same command → same result shape across sync/async.
- No exception ever escapes the class (`BaseException` excepted by design).
- Output is always normalized or `None`.
- Model parsing never affects execution success.
- `success_marker` is an optional semantic gate.
- Async and sync behavior are semantically equivalent.
- No retry logic exists anywhere in this module.

## System Role

`CLITransact` is the execution substrate. Higher layers build commands and policy and
delegate execution down to it:

```text
RsyncTransact  → builds rsync command, selects policies (planned)
SSHTransact    → builds ssh command                      (planned)
CLITransact    → executes command deterministically      (implemented)
subprocess     → raw system interface
```

## Planned Layers (not yet implemented)

> The following describe **target** behavior for sibling modules that do not yet exist
> in the repo. They are recorded here so the contract is stable when they are built.
> Until implemented, they impose no requirement on the current code.

### `SSHTransact` — planned

Stateless, functional, deterministic SSH command builder that delegates to
`CLITransact`. No internal state. Command construction: always include `-p <port>` (even
the default 22); include `-i <identity_file>` only when provided; format the host as
`user@host` when a user is given, else `host`. Remote command semantics mirror the input
contract (`str` → single remote-shell argument; `list` → argv segments).

### `RsyncTransact` — planned

Builds the rsync command and may **select** a retry policy (an optional parameter or
documented default — never a retry implementation of its own; see the policy-ownership
rule in [transport_transaction_architecture.md](transport_transaction_architecture.md)),
delegating execution to `CLITransact`.

- **Option precedence:** explicit `options` (if not `None`) overrides `default_options`;
  `options == []` disables all defaults; `options is None` falls back to defaults.
- **SSH injection:** `-e ssh ...` is injected when any of `ssh_host`, a non-22
  `ssh_port`, or `ssh_identity_file` is set; the SSH command is constructed inline.
- **`blocking_io`:** `blocking_io=True` adds `--blocking-io`; it MUST stay opt-in and
  out of default presets (it is a workaround for specific MSYS2/Windows rsync bugs).

### Retry / Backoff engine — planned

Applies only to transient runtime failures within a single transfer session — never
cross-run recovery or logical file repair.

- **Retryable** return codes: `{10, 12, 30, 35, -1}` (network instability, stream
  interruption, timeout, subprocess failure).
- **Non-retryable:** `23`, `24` (file-level), `2`, `4` (usage/protocol).
- **Backoff:** `delay = min(backoff_max, backoff_base * 2 ** attempt)`, with optional
  jitter `delay = random(0, delay)` to avoid synchronized retry storms.
- **Termination:** stop on success, on a non-transient failure, or when retries are
  exhausted.

### Windows / MSYS2 reliability layer — planned

Handles rsync 3.4.x socket instability (`rc=12`, `errno=11` / EAGAIN) and recoverable
partial transfers. `WINDOWS_SAFE_RSYNC_OPTIONS` MUST include `-avz`, `--partial`,
`--append-verify`, `--timeout=30`, `--contimeout=15` (resumable transfers + fail-fast on
stalled streams + connection-hang prevention). `--blocking-io` stays separate and
opt-in, never in the preset.

## Compliance Requirements

A compliant `CLITransact` MUST:

1. Return a `CLITransactResult` (or `CLITransactResultModel`) from every public
   method — never `None`, never a partial/invalid object.
2. Never let an exception escape a public method (`BaseException` excepted).
3. Normalize all stdout/stderr to a stripped string or `None`.
4. Compute `success` as `return_code == 0 AND (success_marker is None OR success_marker
   in stdout)`.
5. Reserve `ERROR_RETURN_CODE` (`-1`) for framework-level failures only.
6. Parse a model only when `success is True` and `stdout` exists, and never let parsing
   change `success`.
7. Implement no retry, backoff, or transport-construction logic.
