---
plan: Fix01McpSchemaJsonRepair
scope: project
status: needs-approval
last_updated: 2026-08-28
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
