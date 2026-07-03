# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`pyFoundationTools` is a zero-dependency Python library (>= 3.10) that extends the standard library with reusable utilities. The **zero external runtime dependencies** rule is a core design constraint: `[project].dependencies` must stay empty. Anything added there breaks the project's stated purpose. Tooling-only deps go under `[project.optional-dependencies].dev`.

## Commands

All workflows go through the Makefile (`make help` lists them). Key ones:

- `make test` — run pytest in the current environment
- `pytest tests/testfoundation_math.py` — run a single test file
- `pytest tests/testfoundation_math.py::test_clamp` — run a single test
- `make testInEnv` — run tests in an isolated throwaway venv (installs from pyproject, validates packaging path)
- `make fullCheck` — CI gate: `lintCheck` + `formatCheck` + `typecheck` + `test`. Run this before considering work done.
- `make lint` / `make format` — ruff with autofix; `make lintCheck` / `make formatCheck` are the non-mutating CI variants
- `make typecheck` — runs **both** `mypy src/` and `ty check src/`; both must pass
- `make devInstall` or `make e` — editable install for development

Linting/formatting is **ruff** (line-length 100, double quotes; rule set E/F/I/UP/B). The README references `pylint`/`black`/`make docs` (Sphinx) but the Makefile has migrated to ruff and has no working docs target — trust the Makefile, not the README, for tooling.

## Package Architecture

Source uses a `src/` layout with **five independently-importable top-level packages** (not nested under one namespace, auto-discovered by setuptools under `package-dir = {"" = "src"}`). `pyFoundationTools` is the distribution name in `pyproject.toml`, not a package directory.

- `foundationTypes` — data models + the serialization base class (the heart of the library)
- `foundationCLIHelpers` — subprocess transaction wrapper
- `foundation_math` — pure-Python math utilities (e.g. `clamp`)
- `foundation_abc` — abstract base interfaces shared across device/transport implementations
- `foundation_tools` — standalone runtime utilities (currently the structured logger)

Import paths are the package name directly, e.g. `from foundationTypes.data_model_helper import DataModelHelper`, **not** `from pyFoundationTools.foundationTypes...`.

### The DataModelHelper serialization pattern

`foundationTypes/data_model_helper.py` defines the central contract. Every data model is a `@dataclass` subclassing `DataModelHelper` and implementing two methods:

- `from_dict(obj) -> Self` (classmethod, raises `NotImplementedError` on the base — quicktype-generated subclasses implement it as a `@staticmethod`) — type-validated construction from a plain dict
- `to_dict(self) -> dict` — plain-dict serialization

On top of those two, the base class fully implements: JSON file I/O (`save_to_file`/`load_from_file`, snake_case), `to_bytes`/`from_bytes` (JSON-encoded bytes), `to_wire`/`from_wire` (pluggable protocol encode/decode via the `wire_encode`/`wire_decode` ClassVars), `from_env`/`_resolve_from_env` (construction with environment-variable-backed defaults via the `_env_mapping` ClassVar), and structured logging (start/success/failure with `exc_info=True`) on every public method. The module also exports a family of `from_*`/`to_*` assert-based converters (`from_float`, `from_union`, `from_list`, etc.) — these mirror **quicktype's** generated helpers, because models are intended to be generated, not hand-written (see below).

The full contract for this class is specified in [`.claude/specs/data_model_helper.md`](specs/data_model_helper.md). Consult it before extending the class.

### Schema-driven model generation (do not hand-edit generated models)

Models under `foundationTypes/commonTypes/`, `foundationTypes/mathTypes/`, and `foundationTypes/StandardizedLoggerConfig/` are generated from JSON Schema, not written by hand. The pipeline lives in `schema/`:

1. JSON Schema in `schema/schemas/`
2. A per-model shell script in `schema/scripts/` (e.g. `generateGeoCoordinate.sh`) runs `quicktype` (`--lang py --src-lang schema --no-pydantic-base-model`), then `sed`-injects the `DataModelHelper` base class and import, then formats.
3. Output overwrites the `.py` in the corresponding package.

Requires `quicktype` (npm global) and a formatter. **To change a model's shape, edit its schema and regenerate** — editing the generated `.py` directly will be lost on the next run. The generation scripts assume they're run from anywhere (they `cd` to repo root) and use BSD-`sed` syntax for macOS.

The full codegen contract — the golden script template (`generateUnitSphericalSmallCircle.sh`), the required pipeline order, the shared libraries, and the strict-typing requirement — is specified in [`.claude/specs/schemaCodegen.md`](specs/schemaCodegen.md). Consult it before adding or modifying a schema, codegen script, or generated type. Run `make codegen-all` to regenerate all models in one pass.

### CLITransact pattern

`foundationCLIHelpers/cliTransact.py` wraps `subprocess`/`asyncio` subprocess execution. The public API is four **stateless classmethods** — `CLITransact.run_sync` / `run_async` / `run_sync_with_model` / `run_async_with_model` — each taking a keyword-only `timeout` and optional `success_marker`. It never raises — all failures (timeouts, exceptions, non-zero exit) are captured into a `CLITransactResult` dataclass (`return_code`, `stdout`, `stderr`, `success`). `success` is `return_code == 0` AND (if a `success_marker` was passed) that string appearing in stdout. The `*_with_model` variants take an `output_parser` callable and return a `CLITransactResultModel[T]` where `T` is bound to `DataModelHelper` — this is the bridge between CLI output and the data-model layer (e.g. `df -h` → `DiskUsage`). String commands run via `shell=True` (injection risk); list commands are preferred.

The full behavioral contract — the stateless classmethod surface, execution-mode selection, semantic success evaluation, total exception containment, the corrected async timeout escalation (`terminate → kill`), the model-extension layer, the formalized "learned behaviors", and the planned sibling layers (`SSHTransact`, `RsyncTransact`, retry/backoff, Windows/MSYS2) — is specified in [`.claude/specs/cliTransact.md`](specs/cliTransact.md). The CLITransact kernel is implemented; the sibling layers are planned. Consult the spec before extending the module.

### PeripheralByteTransport ABC

`foundation_abc/peripheralByteTransport.py` defines `PeripheralByteTransport`, an `ABC` for fully-asynchronous, byte-only device transports (`connect`/`disconnect`/`send`/`receive`/`is_connected`, plus an async context-manager `__aenter__`/`__aexit__`). It intentionally knows nothing about protocol framing (STX/ETX, checksums, BCC) — that belongs to device handlers layered on top. A serial (RS485/USB) implementation exists elsewhere on top of this interface; an EtherCAT adapter (translating PDO process-image offsets to this byte-stream contract) is planned. No dedicated spec exists yet for this module.

### StandardizedLogger

`foundation_tools/standardized_logger.py` defines `StandardizedLogger`, a `logging.Logger` subclass that self-configures a stderr handler (JSON by default, human-readable via `console_pretty`) plus an optional date-rolling JSON file handler when `log_dir` is set. Build one from a `StandardizedLoggerConfig` (`foundationTypes/StandardizedLoggerConfig/`, itself a schema-generated `DataModelHelper` model) via `StandardizedLogger.from_config(...)`, or construct directly. `debug`/`info`/`warning`/`error`/`critical` accept arbitrary keyword args, which become structured JSON fields on file output. No dedicated spec exists yet for this module.

## Tests

Tests live in `tests/` (and `tests/typeTests/`), discovered via pyproject config: files `test*.py`, functions `test*`. Async tests use `pytest-asyncio`.
