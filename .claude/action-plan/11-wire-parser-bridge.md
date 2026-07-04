---
plan: ActionPlan11WireParserBridge
scope: project
status: pending
last_updated: 2026-07-03
semver: 0.0.1
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

- [ ] Round-trip tests pass with a real generated model — no ad-hoc model classes.
- [ ] Adapter decision recorded (implemented + spec'd, or explicitly declined).
- [ ] `make fullCheck` passes.

## Out of scope

- Changing `DataModelHelper` itself (its spec governs; extend via
  [dataModelHelper.md](../specs/dataModelHelper.md) if ever needed).
- Socket-side wire usage (covered by chunks 08/10).
