---
plan: ActionPlan11WireParserBridge
scope: project
status: complete
last_updated: 2026-07-05
semver: 0.1.0
author: Nicholas Bergantz
---

# 11 — Wire-Parser Bridge

## Goal

Prove and document `DataModelHelper` as the canonical parser for the transaction
stack: `from_wire` / `from_bytes` / `from_dict`-based parsers feeding
`CLITransact.run_*_with_model`. Bias: **zero new API** — this chunk is tests and
docs unless a test demonstrates a genuine gap.

Contract: Wire Serialization Bridge section of
[transport_transaction_architecture.md](../specs/transport_transaction_architecture.md).

## Depends on

02 (hardened kernel). Independent of chunks 03–10.

## Files

- `tests/test_wire_parser_bridge.py`
- Docstring example in `src/foundation_tools/cli_transaction/cliTransact.py`
  (`run_sync_with_model`) showing a generated-model parser
- Only if tests prove it's needed: a tiny adapter helper in
  `src/foundation_tools/cli_transaction/` (e.g. turning a model class into an
  `output_parser`) — added to the spec in the same change if so

## Steps (TDD)

1. Tests using an existing generated model (e.g. `DiskUsage` or a
   `wire_decode`-configured model):
   - `run_sync_with_model(cmd, Model.from_wire)` round trip on real CLI output
   - `from_bytes`-based parsing where output is JSON
   - unconfigured `wire_decode` → `NotImplementedError` from the parser is
     contained by the kernel (advisory stderr, `success` unchanged)
2. Evaluate ergonomics: if every call site needs the same lambda/boilerplate,
   design the minimal adapter, test it, and update the specs; otherwise record in
   the test module docstring that no adapter is needed.
3. `make fullCheck`.

## Acceptance criteria

- [x] Round-trip tests pass with a real generated model — no ad-hoc model classes.
- [x] Adapter decision recorded (implemented + spec'd, or explicitly declined).
- [x] `make uv-fullCheck` passes (`make fullCheck` no longer exists).

## Out of scope

- Changing `DataModelHelper` itself (its spec governs; extend via
  [dataModelHelper.md](../specs/dataModelHelper.md) if ever needed).
- Socket-side wire usage (covered by chunks 08/10).

## Implementation notes

- **No adapter needed** — the ergonomics evaluation (step 2) concluded
  `Model.from_wire` already has the exact `Callable[[str], T]` shape
  `output_parser` requires, so it's usable directly:
  `CLITransact.run_sync_with_model(cmd, GeoCoordinate.from_wire)`. `from_bytes`
  takes `bytes`, so its one-line call-site adapter
  (`lambda s: Model.from_bytes(s.encode())`) is the minimal glue a caller ever
  writes — adding a library-side wrapper for a one-liner would be an
  abstraction with no isolation value, so none was added.
- `tests/test_wire_parser_bridge.py` proves the bridge against two real
  generated models, all against actual subprocess output (`echo`, `df -h`), no
  mocked `subprocess` calls:
  - `GeoCoordinate.from_wire` round trip (`wire_encode`/`wire_decode`
    monkeypatched as JSON, same pattern as chunk 08 — no `wire_config.py`
    wiring exists in the repo yet).
  - `GeoCoordinate.from_bytes` round trip needs **no** wire configuration at
    all, since `to_bytes`/`from_bytes` compose on `to_dict`/`from_dict`, which
    every `DataModelHelper` subclass already implements.
  - Unconfigured `wire_decode` (`GeoCoordinate.from_wire` with no monkeypatch)
    → `NotImplementedError` inside the parser is contained: `success` stays
    `True`, `stderr` carries "Model parsing failed" — proving the kernel's
    parser-failure containment (chunk 02) holds for the real
    `NotImplementedError` `DataModelHelper.from_wire` raises when
    unconfigured, not just a test double's exception.
  - `DiskUsage.from_df_output` against real `df -h` output — the
    domain-specific-parser-on-a-generated-model shape the spec calls the
    canonical form for CLI output that isn't wire-encoded JSON.
- Added a docstring example to `CLITransact.run_sync_with_model`
  (`src/foundation_tools/cli_transaction/cliTransact.py`) showing both the
  `from_df_output`-style and `from_wire`-style generated-model parsers — no
  code change to the classmethod itself.
