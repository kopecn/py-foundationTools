---
spec: SchemaCodegen
scope: project
status: implemented
applies_to: schema/, src/foundationTypes/commonTypes/, src/foundationTypes/mathTypes/, src/foundationTypes/cvTypes/, src/foundationTypes/standardizedLoggerConfig/
last_updated: 2026-09-07
semver: 0.3.0
author: Nicholas Bergantz
---

# Schema Codegen Specification

> **Status — implemented (Python only).** The pipeline described here is realized
> by `schema/scripts/reuse/codegen.sh` + `schema/scripts/reuse/add_datamodelhelper.sh`
> and the per-model scripts in `schema/scripts/`. The workflow is structured to scale
> to additional output languages later; today it emits **Python only**.

## Overview

System-interface data models follow a **schema-first** workflow. A JSON Schema is the
single source of truth for a model's shape; the `.py` is a generated artifact. To
change a model's shape you edit its schema and regenerate — never the generated file.
This spec governs schemas under `schema/schemas/`, the codegen scripts under
`schema/scripts/`, and their generated output. It complements
[`dataModelHelper.md`](dataModelHelper.md), which governs the base class every
generated model inherits.

## Golden Workflow

`schema/scripts/generateDiskUsage.sh` is the **canonical script template**. (The
former template, `generateUnitSphericalSmallCircle.sh`, was consolidated into the
Math family's `generateMathTypes.sh` — which is the sanctioned-deviation path, not
the stock one.) New and migrated codegen scripts SHALL be modeled on it: a thin,
declarative caller that sets a few variables, sources the two shared libraries, and
invokes the shared pipeline functions in order. Scripts SHALL NOT reimplement pipeline
logic inline.

**Conformance rule (Increase Quality Through Conformance / Chamber Match):** per-model
scripts SHALL be structurally identical apart from their model-specific variables — a
diff of any two conforming scripts with model names filtered out SHALL be empty. The
**only** sanctioned deviation from the stock pipeline is a family that shares
schema enums with an independent protocol package, per the Math pattern
(`generateMathTypes.sh` + `reuse/postprocess_mathtypes.py`, governed by
[`mathTypeTiers.md`](mathTypeTiers.md)).
Any other need for per-model behavior goes into the shared libraries (behind an opt-in
function) or into a `wire_config.py` sibling (below) — never into a bespoke script.

A conforming script:

1. Sets `INPUT_SCHEMA_FILES`, `CLASSES_FOR_BASE_PARENT`, `OUTPUT_PYTHON_REL`,
   `PYTHON_VERSION` (`3.7` — quicktype's ceiling), and `set -euo pipefail`.
2. Sources `reuse/codegen.sh` and `reuse/add_datamodelhelper.sh` relative to its own
   `SCRIPT_DIR`.
3. Calls the pipeline **in this order**:
   `setup_quicktype` → `run_quicktype` → `add_base_class` → `add_helper_imports`
   → `add_autogen_header` → `run_ruff` → `ensure_py_typed`.

## Shared Libraries (source of truth for behavior)

- `schema/scripts/reuse/codegen.sh` — quicktype invocation and post-processing:
  `setup_quicktype`, `run_quicktype`, `add_autogen_header`, `strip_schema_suffix`
  (opt-in), `fix_to_dict_return_type`, `run_ruff`, `ensure_py_typed`. Resolves the
  output path under `src/foundationTypes/` from `OUTPUT_PYTHON_REL`.
- `schema/scripts/reuse/add_datamodelhelper.sh` — `add_base_class` (inject
  `DataModelHelper` parent + import) and `add_helper_imports` (strip quicktype's inline
  `from_*`/`to_*` helpers and import the equivalents from
  `foundationTypes.data_model_helper` instead). The Math family
  (`schema/scripts/generateMathTypes.sh`) does not call this library — its
  post-processor (`schema/scripts/reuse/postprocess_mathtypes.py`, see
  [`mathTypeTiers.md`](mathTypeTiers.md)) injects the equivalent `DataModelHelper`
  parent + import itself and replaces quicktype's local enum copies. Math shape
  protocols remain independent and are satisfied structurally; the postprocessor
  does not inject them into generated class hierarchies.
- `schema/scripts/reuse/normalize_generated.sh` — **single source of truth** for
  post-quicktype rewrites that must reach *every* generated model regardless of which
  script produced it. Three passes:
  1. Rewrites quicktype's `from_dict` `@staticmethod`
     (`def from_dict(obj: Any) -> "Foo"`) to the `DataModelHelper` `@classmethod`
     contract (`@classmethod` / `def from_dict(cls, obj: Any) -> "Foo"`), preserving
     the concrete return annotation and body.
  2. Backfills `= None` onto a bare, defaultless `field: Any` that trails a defaulted
     field in the same merged dataclass (see the script's own header comment for the
     narrow condition).
  3. Rewrites quicktype's bare `assert isinstance(obj, dict)` dict-type guard to an
     explicit `TypeError` check (below).

  Idempotent and safe on hand-written files. Both `codegen.sh`'s `run_ruff` (per file)
  and the `make codegen-all` final sweep (whole tree) call it — neither owns the
  rewrite logic.

Pipeline mechanics SHALL live in these libraries so every model is generated by one
process, not per-script variants. Changing generation behavior means changing a shared
library, not editing one script.

## Strict-Typing Requirement

quicktype targets Python 3.7 and emits loose types (bare `dict`, `Type[T]`). Generated
output SHALL nonetheless satisfy the project's strict gate (`make uv-typecheck`, mypy
`strict = true`). The pipeline restores modern strict typing **after** quicktype:

- `fix_to_dict_return_type` (called inside `run_ruff`) rewrites `-> dict` /
  `result: dict = {}` to `dict[str, Any]`.
- `fix_from_dict_classmethod` (called inside `run_ruff`, delegating to
  `normalize_generated.sh`) converts the `from_dict` `@staticmethod` to the
  `@classmethod` contract.
- `run_ruff` applies ruff `format` + `check --fix --unsafe-fixes`, whose `UP` rules
  modernize annotations (e.g. `Type[T]` → `type[T]`, `Optional[X]` → `X | None`).
  `--unsafe-fixes` holds the generated tree to the same autofix level as hand-written
  source (mirrors the `uv-format` target). `make codegen-all` additionally runs
  `ruff format` + `ruff check --fix --unsafe-fixes` over the whole `_PYTHON_TYPES_BASE`
  tree after generation, so files from non-conforming scripts are fixed too.
- `ensure_py_typed` touches the package `py.typed` marker so the strict types are
  exported.

Adding a model SHALL be followed by `make uv-typecheck` to confirm the generated file
passes. A failure means the **pipeline or schema** is wrong — fix there, never by
hand-editing the generated `.py`.

## Generated Files Are Read-Only

Every generated file carries the `AUTO-GENERATED FILE — DO NOT EDIT` header from
`add_autogen_header`. Manual edits SHALL NOT be made to generated `.py` files; they are
overwritten on the next `make codegen-all` — hand edits made under time pressure are a
silent regression waiting for the next regen. Hand-written behavior belongs in a
`wire_config.py` sibling (below), which regeneration never touches.

## Wire Configuration Sibling (canonical)

A model needing hand-written wire behavior — any of the three wire slots
`wire_encode` / `wire_decode` / `wire_invoke` (contract in
[`dataModelHelper.md`](dataModelHelper.md)) — SHALL live in its own package subfolder
with a `wire_config.py` sibling:

```
src/foundationTypes/commonTypes/<model_folder>/
├── <Model>.py       # generated (script's OUTPUT_PYTHON_REL targets this path)
├── wire_config.py   # hand-written: assigns the wire ClassVars on the class
└── __init__.py      # imports wire_config for its side effect; re-exports the model
```

Rules:

- Wire logic SHALL NOT be baked into the generated `.py` or into a per-model codegen
  post-processing step. The generated file carries only the quicktype shape
  (`from_dict`/`to_dict`); `wire_config.py` binds the protocol at import time.
- The folder's `__init__.py` SHALL import `wire_config` for its side effect so the
  wiring activates on any import of the model.
- Regeneration overwrites only `<Model>.py`; `wire_config.py` and `__init__.py` are
  hand-maintained and never touched by the pipeline.
- Rationale: the sibling externalizes wire access — an end user can rebind the
  ClassVars to a protocol of their own without forking the model or the pipeline.

`src/foundationTypes/commonTypes/disk_usage/` is the canonical exemplar
(`DiskUsage.py` generated by `generateDiskUsage.sh`; `wire_config.py` assigns the
`df -h` codec pair and `wire_invoke = ["df", "-h"]`). Models with no hand-written
wire behavior stay flat (a single generated `.py`, no subfolder).

## Authoring Schemas

- Place schemas under `schema/schemas/` (grouped by domain subfolder, e.g. `Math/`,
  `MCP/`, `ComputerVisions/`), targeting the matching package under
  `src/foundationTypes/` (`mathTypes/`, `commonTypes/`, `cvTypes/`,
  `standardizedLoggerConfig/`). The schema filename and `title`/class name drive the generated class name.
- Keep schemas **self-contained** — avoid cross-domain `$ref`; duplicate shared fields
  rather than coupling domains.
- **Skip discriminated unions** — quicktype cannot represent them in its dataclass
  codegen.

## Running Codegen

`make codegen-all` auto-discovers and runs every `schema/scripts/*.sh` in one pass.
One script → one generated module, fed by **one or more** schemas: `INPUT_SCHEMA_FILES`
is an array, and a script SHALL list every schema its module needs
(`generateChArUcoConfig.sh` takes the three `ComputerVisions/` schemas,
`generateModelContextProtocol.sh` takes two, `generateMathTypes.sh` takes the whole
`Math/` domain). Splitting one module's schemas across several scripts is not a
supported shape — the module is the unit a script owns. After all scripts run, it applies a
**fleet-wide normalization sweep** (`normalize_generated.sh` over `_PYTHON_TYPES_BASE`)
so contract rewrites reach every generated model — including output from
non-conforming or future scripts that bypass the shared `run_ruff` pipeline. This is a
poka-yoke: a sloppy script cannot ship a model that violates the normalized contract.

## Generated `from_dict` Dict-Type Guard

quicktype emits every generated `from_dict` with a bare `assert isinstance(obj, dict)`
as its sole input-type check. This is unsafe on two counts: it raises `AssertionError`,
which sits outside `from_union`'s `(TypeError, ValueError, KeyError)` catch tuple (so a
wrongly-typed nested field escapes union dispatch instead of falling through), and
`python -O` strips assertions entirely, silently disabling the check under optimized
runtime. `normalize_generated.sh`'s third pass (above) rewrites the guard to the
statement form of the same check `data_model_helper.py`'s own `from_dict` converter
uses:

```python
if not isinstance(obj, dict):
    raise TypeError(f"Expected dict, got {obj.__class__.__name__}")
```

`obj.__class__.__name__` — not `type(obj).__name__` — deliberately, and this is the one
place the generated guard's wording departs from `data_model_helper.py`'s hand-written
converter of the same shape. Any generated `from_dict` whose JSON Schema has a field
named `"type"` assigns a same-scope local `type = ...` later in the method body;
Python's function-wide scoping rule then makes every bare `type` reference in that
function resolve to the local rather than the builtin, so `type(obj)` in the guard would
raise `UnboundLocalError` instead of `TypeError` (ruff flags this statically as F823;
several MCP reference classes and `Presentations.Region`/`ContentBlock` hit it in
practice). `obj.__class__.__name__` sidesteps the shadow and produces an identical
string for every value the guard is ever called with. `from_union` in
`data_model_helper.py` is unaffected by this pass and MUST NOT be widened to catch
`AssertionError` — see [`dataModelHelper.md`](dataModelHelper.md) for the full contract
and the reasoning against that alternative.

## Known Gaps

- **Field ordering.** quicktype can emit a required (non-default) dataclass field after
  optional ones, which is a `TypeError` at import and a mypy `misc` error. The pipeline
  does not yet auto-correct this. All current models pass the strict gate (the earlier
  `ServerResult.data` instance was resolved at the schema level), but the limitation is
  latent: a required-after-default field appearing on regen is a signal the schema or
  pipeline needs adjustment.
- **Single language.** Only the Python pipeline exists today. Additional languages,
  when added, SHALL extend the shared libraries and the per-model scripts rather than
  forking a parallel mechanism.

(Resolved: `generateGeoCoordinate.sh` previously bypassed the shared libraries; it now
conforms to the golden workflow — every script in `schema/scripts/` is structurally
identical to the template apart from model variables, except the sanctioned Math
family.)
