---
plan: Fix01McpSchemaJsonRepair
scope: project
status: complete
last_updated: 2026-09-04
semver: 1.0.0
author: Nicholas Bergantz
---

# Fix candidate 01 — invalid MCP schema JSON

Evidence: `schema/schemas/ModelContextProtocolTypes-schema.json` has a trailing comma
at line 277 and fails `json.load`.

Minimum fix: remove that comma and add one stdlib test that loads every committed
`*-schema.json`, reporting the path on failure. Regenerate only the affected model if
needed, then run the normal gate.

Do not update protocol definitions, add a schema-validator dependency, or change any
presentation schema in this task.

## Ask ↔ result

- **Objective:** repair the invalid MCP schema JSON so it parses, and guard against recurrence.
- **Authorized by:** `/execute-plan please proceed` (user approved all of fix-01–07).
- **Delivered:** removed the trailing comma at line 277 of `ModelContextProtocolTypes-schema.json`; added `tests/test_schema_json_validity.py`, which `json.load`s all 27 committed `*-schema.json` files and reports the offending path on failure (confirmed failing pre-fix, passing after). Regeneration confirmed a no-op (quicktype tolerated the comma; generated `.py` byte-identical).
- **Gate:** `make uv-fullCheck` — ruff/mypy clean, 487 passed.
- **Gap:** none.
