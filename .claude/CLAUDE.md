# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`pyFoundationTools` is a zero-dependency Python library (>= 3.10) that extends the standard library with reusable utilities. The **zero external runtime dependencies** rule is a core design constraint: `[project].dependencies` must stay empty. Anything added there breaks the project's stated purpose. Tooling-only deps go under `[project.optional-dependencies].dev`.

## Commands

All workflows go through the Makefile (`make help` lists them). Key ones:

- `make test` — run pytest in the current environment
- `pytest tests/testfoundationMath.py` — run a single test file
- `pytest tests/testfoundationMath.py::test_clamp` — run a single test
- `make testInEnv` — run tests in an isolated throwaway venv (installs from pyproject, validates packaging path)
- `make fullCheck` — CI gate: `lintCheck` + `formatCheck` + `typecheck` + `test`. Run this before considering work done.
- `make lint` / `make format` — ruff with autofix; `make lintCheck` / `make formatCheck` are the non-mutating CI variants
- `make typecheck` — runs **both** `mypy src/` and `ty check src/`; both must pass
- `make devInstall` or `make e` — editable install for development

Linting/formatting is **ruff** (line-length 100, double quotes; rule set E/W/F/I/UP/B). The README references `pylint`/`black`/`make docs` (Sphinx) but the Makefile has migrated to ruff and has no working docs target — trust the Makefile, not the README, for tooling.

## Package Architecture

Source uses a `src/` layout with **four independently-importable top-level packages** (not nested under one namespace). `package-dir = {"" = "src"}` maps them:

- `foundationTypes` — data models + the serialization base class (the heart of the library)
- `foundationCLIHelpers` — subprocess transaction wrapper
- `foundationMath` — pure-Python math utilities (e.g. `clamp`)
- `pyFoundationTools` — the distribution/umbrella package

Import paths are the package name directly, e.g. `from foundationTypes.dataModelHelper import DataModelHelper`, **not** `from pyFoundationTools.foundationTypes...`.

### The DataModelHelper serialization pattern

`foundationTypes/dataModelHelper.py` defines the central contract. Every data model is a `@dataclass` subclassing `DataModelHelper` and implementing two methods:

- `from_dict(obj) -> Self` (staticmethod) — type-validated construction from a plain dict
- `to_dict(self) -> dict` — plain-dict serialization

The base class provides `saveToFile(Path)` / `loadFromFile(Path)` (JSON I/O) for free on top of those two. The module also exports a family of `from_*`/`to_*` assert-based converters (`from_float`, `from_union`, `from_list`, etc.) — these mirror **quicktype's** generated helpers, because models are intended to be generated, not hand-written (see below).

The full intended contract for this class — including target features not yet implemented (`from_env`, `to_bytes`/`from_bytes`, `to_wire`/`from_wire`, env-var resolution, logging, and the snake_case `save_to_file`/`load_from_file` names) — is specified in [`.claude/specs/dataModelHelper.md`](specs/dataModelHelper.md). Consult it before extending the class.

> Gotcha: `dataModelHelper.py` calls `json.dump`/`json.load` in `saveToFile`/`loadFromFile` but does **not** import `json`. Anything exercising file I/O on a model will `NameError` until `import json` is added. This file is currently modified in the working tree — verify the import before relying on save/load.

### Schema-driven model generation (do not hand-edit generated models)

Models under `foundationTypes/commonTypes/` and `foundationTypes/mathTypes/` are generated from JSON Schema, not written by hand. The pipeline lives in `schema/`:

1. JSON Schema in `schema/schemas/`
2. A per-model shell script in `schema/scripts/` (e.g. `generateGeoCoordinate.sh`) runs `quicktype` (`--lang py --src-lang schema --no-pydantic-base-model`), then `sed`-injects the `DataModelHelper` base class and import, then formats.
3. Output overwrites the `.py` in the corresponding package.

Requires `quicktype` (npm global) and a formatter. **To change a model's shape, edit its schema and regenerate** — editing the generated `.py` directly will be lost on the next run. The generation scripts assume they're run from anywhere (they `cd` to repo root) and use BSD-`sed` syntax for macOS.

### CLITransact pattern

`foundationCLIHelpers/cliTransact.py` wraps `subprocess`/`asyncio` subprocess execution. It never raises — all failures (timeouts, exceptions, non-zero exit) are captured into a `CLITransactResult` dataclass (`return_code`, `stdout`, `stderr`, `success`). `success` is `return_code == 0` AND (if a `success_string` was configured) that string appearing in stdout. The `*_with_model` variants take a serializer callable and return a `CLITransactResultWithModel[T]` where `T` is bound to `DataModelHelper` — this is the bridge between CLI output and the data-model layer (e.g. `df -h` → `DiskUsage`). String commands run via `shell=True` (injection risk); list commands are preferred.

## Tests

Tests live in `tests/` (and `tests/typeTests/`), discovered via pyproject config: files `test*.py`, functions `test*`. Async tests use `pytest-asyncio`.
