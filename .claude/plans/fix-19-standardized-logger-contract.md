---
plan: Fix19StandardizedLoggerContract
scope: project
status: needs-approval
last_updated: 2026-09-04
semver: 1.0.0
author: Nicholas Bergantz
---

# Fix candidate 19 — StandardizedLogger compatibility and safety

Evidence: `StandardizedLogger` subclasses `logging.Logger` but consumes standard keywords
such as `stack_info` and `stacklevel` as structured fields. Caller fields can overwrite
canonical JSON fields, arbitrary non-JSON values can escape the custom file handler, and
unsanitized logger names participate in file paths. The 423-line implementation has only
three tests, all for private inode-rollover behavior.

Minimum fix: preserve the standard `Logger` call contract, reserve canonical structured
keys, define deterministic serialization for supported values, route formatting/write
failures through normal logging error handling, and constrain file names to `log_dir`.
Add public behavior tests for every standard keyword and both console/file handlers.

Do not silently stringify everything without a documented policy, allow structured fields
to replace canonical metadata, or use the global `setLoggerClass` side effect as a shortcut
for explicit construction.
