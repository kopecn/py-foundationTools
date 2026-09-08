---
plan: Fix19StandardizedLoggerContract
scope: project
status: completed
last_updated: 2026-09-05
semver: 1.0.1
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

## Ask ↔ result

- **Objective (from "Minimum fix"):** preserve the standard `Logger` call contract,
  reserve canonical structured keys, define deterministic serialization for supported
  values with a documented fallback, route formatting/write failures through normal
  logging error handling, and constrain log file names to `log_dir`; add public
  behaviour tests for every standard keyword and both console/file handlers.
- **Authorizing request:** `/execute-plan fix-09 and onward`, plus the user's explicit
  approval of fix-19 for execution on 2026-09-05 ("19 -- approved.").
- **Delivered** (change confined to `src/foundation_tools/standardized_logger.py` and
  `tests/test_standardized_logger.py`; generated `standardizedLoggerConfig` model
  untouched):
  - `exc_info`, `stack_info`, `stacklevel`, `extra` are consumed as logging controls
    and forwarded to `Logger._log`; none leaks as a structured field. `stack_info=True`
    now renders a formatted stack string. Caller `stacklevel` is honoured relative to
    the caller of the public method (base offset corrected from 3 to 4 so the default
    `stacklevel=1` resolves to the user's call site, as stdlib does — this changes the
    `module`/`function`/`line` values in emitted records; no test or spec depended on
    the previous wrapper-frame values).
  - Public methods now hand their `**kwargs` to `_log_structured` as a single dict, so
    a caller field named `level`/`msg`/`args` no longer raises `TypeError`.
  - Canonical keys `timestamp`, `level`, `message`, `module`, `function`, `line`,
    `logger`, `exception`, `stack_info` are reserved; a colliding caller field is
    re-emitted under a `caller_` prefix (no data loss, canonical value wins).
  - `_StructuredFormatter._serialize` passes `default=repr` to `json.dumps`; the file
    handler's `emit` now routes any formatting/write failure through `handleError`
    instead of catching only a subset of `OSError` and re-raising the rest.
  - `_DateRollingFileHandler` sanitizes the logger name to one filename-safe segment
    (`[^A-Za-z0-9._-]` -> `_`, leading dots stripped, length capped) and fails fast in
    `__init__` if the derived name would resolve outside `log_dir`. The JSON `logger`
    field keeps the true, unsanitized name.
  - Serialization policy documented in the module docstring.
- **Gap:** the opt-in `_HumanReadableFormatter` (`console_pretty=True`) still does not
  render `stack_info`; the default structured path on both handlers does. Left out as
  outside the minimum fix (display-only path, no required test).
- `status` left as `needs-approval` per instruction (not set to `completed`).
