---
plan: Fix17PresentationSchemaRuntimeContract
scope: project
status: needs-approval
last_updated: 2026-09-04
semver: 1.0.0
author: Nicholas Bergantz
---

# Fix candidate 17 — presentation schema/runtime contract

Evidence: presentation JSON Schemas declare defaults and constraints that generated Python
constructors do not materialize or validate. `PresentationMetadata.file.path` defaults to
`.` in the schema but is `None` in generated Python, creating two contracts and reintroducing
ambient-current-working-directory behavior. Minimums, maximums, and `minItems` constraints
have the same boundary ambiguity.

Minimum fix: decide where schema validation and default materialization are authoritative,
provide one explicit validated construction boundary, and make output-location resolution
deterministic. Prefer a required absolute output directory or an explicitly defined path
relative to a named source/deck location.

Do not make generated dataclass construction appear validated when it is not, silently use
the process CWD, or hand-edit generated presentation modules.
