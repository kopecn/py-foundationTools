---
plan: Fix01McpSchemaJsonRepair
scope: project
status: pending
last_updated: 2026-08-23
semver: 0.0.1
author: Nicholas Bergantz
---

# Fix 01 — MCP Schema JSON Repair

## Goal

Make every committed `*-schema.json` file valid JSON and restore the fleet-wide
codegen path before presentation codegen is introduced.

## Depends on

Nothing. Land this before presentation chunk 02 because `make codegen-all` runs the
MCP generator as part of the same fleet sweep.

## Defect

`schema/schemas/ModelContextProtocolTypes-schema.json:277` leaves a trailing comma
after the final `properties` member. Python's `json` module rejects the file, and a
strict JSON consumer cannot treat it as a JSON Schema.

## Files

Edit:

- `schema/schemas/ModelContextProtocolTypes-schema.json`

Create:

- `tests/test_schema_json.py`

Do not hand-edit `src/foundationTypes/commonTypes/ModelContextProtocol.py`.

## Design constraints

**Fleet test, not a one-file test.** The regression test SHALL recursively load every
`schema/schemas/**/*-schema.json` with `json.load`. A one-off assertion on the MCP
file would allow the same syntax defect to move elsewhere unnoticed.

**No new validator dependency.** This chunk checks JSON syntax using the standard
library. JSON Schema metaschema validation is separate work and must not add a
runtime dependency.

**Minimal schema change.** Remove only the illegal comma. Do not rename MCP
definitions or regenerate schema content as part of a syntax repair.

## Steps (TDD)

1. Add `tests/test_schema_json.py`, parameterized over every `*-schema.json`, and load
   each file through `json.load`. Run it; the MCP wrapper fails at line 277.
2. Remove the trailing comma.
3. Re-run the focused test.
4. Run `schema/scripts/generateModelContextProtocol.sh` and confirm the generated
   module either has no diff or only deterministic expected output.
5. Run `make codegen-all` twice; the second run must produce no diff.
6. Run `make uv-fullCheck`.

## Acceptance criteria

- [ ] Every `schema/schemas/**/*-schema.json` loads with the stdlib `json` module.
- [ ] The regression test reports the offending path when a schema cannot be parsed.
- [ ] MCP codegen succeeds without a hand edit to generated Python.
- [ ] Two consecutive `make codegen-all` runs are idempotent.
- [ ] `make uv-fullCheck` passes.

## Out of scope

- Updating the vendored MCP protocol version.
- Changing any MCP definition or generated model API.
- Adding `jsonschema` or another validator dependency.
- Presentation schema linking; that remains presentation chunk 01.

