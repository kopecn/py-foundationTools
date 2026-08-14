# History

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
-

## [0.0.4] - 2026-08-14

### Added
- `foundation_tools` package — the transaction/transport stack: `CLITransact` kernel, `SSHTransact`, `RsyncTransact`, command builders (`ssh_builder`, `rsync_builder`), execution policies (`retry_policy`, `backoff_policy`), and the asyncio socket family (`socket_byte_transport`, `framing_codecs`, `transaction_router`, `socketTransact`, `socketTransactServer`).
- `StandardizedLogger` (`foundation_tools/standardized_logger.py`) — JSON/pretty stderr handler plus optional date-rolling JSON file handler, built from the schema-generated `StandardizedLoggerConfig` model.
- `foundation_abc` package — `PeripheralByteTransport` ABC for async byte-only device transports, and the stdlib-only Math-domain `XxxxLike` ABCs (`spatialABCs`, `sphericalABCs`, `waveformABCs`, `precisionTimeABC`) with their `mathEnums`.
- `foundation_physics.constants.thermodynamics` — SI physical constants with explicit provenance notes.
- Wire-protocol layer on `DataModelHelper`: `to_wire`/`from_wire`, the `wire_encode`/`wire_decode`/`wire_invoke` ClassVars, `to_bytes`/`from_bytes`, and `from_env`/`_env_mapping` environment-backed construction.
- Math type tier: `Position`, `Quaternion`, `SpatialTransform`, `ReferenceFrame`, `PrecisionTimestamp`, `PrecisionTimeInterval`, `Timescale`, `NumericSign`, and the waveform variants — all schema-generated into `foundationTypes/mathTypes/MathTypes.py`.
- ChArUco computer-vision types (`foundationTypes/cvTypes/ChArUcoConfig.py`) from new `schema/schemas/ComputerVisions/` schemas.
- `foundationTypes/commonTypes/disk_usage/` — generated `DiskUsage.py` alongside a hand-written `wire_config.py` sibling, establishing the pattern for models needing custom wire behavior.
- Codegen pipeline rework — shared `schema/scripts/reuse/` libraries (`codegen.sh`, `add_datamodelhelper.sh`, `normalize_generated.sh`, `postprocess_mathtypes.py`), per-domain generate scripts, and a `make codegen-all` one-pass target.
- CI/CD — `.github/workflows/ci.yml` (quality gate on PRs into `dev`/`prod`), `publish.yml`, `tag-on-prod.yml`, and `CODEOWNERS`.
- uv-based Makefile lifecycle: `uv-bootstrap`, `uv-sync{,-dev,-release,-local}`, `uv-lint`, `uv-format`, `uv-typecheck`, `uv-test{,-all,-matrix}`, `uv-fullCheck`, and the `uv-flush-*` cleanup family, with the pip targets retained as a fallback path.
- `requirements.txt`, `.python-version`, and `.editorconfig`.
- PEP 561 `py.typed` markers across the published packages.
- `.claude` spec model — `CLAUDE.md` plus specs for `cliTransact`, `dataModelHelper`, `mathTypeTiers`, `rsyncTransact`, `schemaCodegen`, `socketTransact`, `sshTransact`, and `transport_transaction_architecture`, with the executed action plans archived.
- Examples for the socket client/server, retry policy, SSH, rsync, and performance benchmarking.
- Test suite covering builders, policies, framing codecs, the transaction router, socket/SSH/rsync transacts, the wire-parser bridge, package layering and restructure, and the math tier contract.
- `docs/FAs/` failure-analysis reports.

### Changed
- Restructured into four independently-importable top-level packages (`foundationTypes`, `foundation_math`, `foundation_abc`, `foundation_tools`): `foundationCLIHelpers` → `foundation_tools/cli_transaction`, `foundationMath` → `foundation_math`, and `foundationTypes/dataModelHelper.py` → `foundationTypes/data_model_helper.py`.
- Migrated linting and formatting from pylint/black to **ruff** (line length 100, rule set E/F/I/UP/B) and made `mypy --strict` the type gate over `src/` and `tests/`; `ty` is installed as a dev dependency but intentionally not wired into the gate yet.
- `pyproject.toml`: renamed the `develop` optional-dependency extra to `dev`, populated keywords and trove classifiers, documented the names-only runtime-dependency rule, and inlined the ruff, mypy, and pytest configuration (including `pythonpath = ["src"]` so a bare `pytest` works on a fresh checkout).
- `.bumpversion.cfg`: `tag = false` — tagging is now performed by the `tag-on-prod` workflow rather than by the local bump.
- Rewrote the Makefile around `uv run --no-project` self-contained targets.

### Removed
- `.pylintrc`, the pylint and black dev dependencies, and the empty `personal_repos` extra.
- `src/pyFoundationTools/` — `pyFoundationTools` is the distribution name only, not an import path; `foundationTools.py` was deleted with it.
- Per-model `generateUnitSphericalArc.sh` and `generateUnitSphericalSmallCircle.sh`, superseded by `generateMathTypes.sh`.
- Standalone `UnitSphericalArc.py` and `UnitSphericalSmallCircle.py` modules, folded into the consolidated `MathTypes.py`.

### Fixed
- Editable `pip install -e .` failing in a clean environment from a half-bootstrapped pip; see [docs/FAs/2026-07-28-pip-install-editable-fails-clean-environment.md](docs/FAs/2026-07-28-pip-install-editable-fails-clean-environment.md).
- Async timeout escalation in `CLITransact` (`terminate` → `kill`) and non-blocking behavior in the socket byte transport.

## [0.0.3] - 2025-12-02

### Added
- `UnitSphericalArc` and `UnitSphericalSmallCircle` schema-generated math types, with their generation scripts and unit tests under `tests/typeTests/`.

### Changed
- Renamed `foundationDataModelHelpers` to `foundationTypes` for clarity; `commonTypes` models moved with it.

## [0.0.2] - 2025-09-20

### Added
- `DataModelHelper` base class and the `from_*`/`to_*` quicktype-style converters, with the schema-driven generation pipeline (`schema/scripts/`).
- `commonTypes` models: `GeoCoordinate`, `DiskUsage`, and the Model Context Protocol (2025-06-18) types.
- `foundationMath` package.
- `CLITransact` CLI transaction helper.
- Unit tests for the math, data-model, and CLI-transaction modules, plus `exampleDataModel.py` and `exampleTransactCLI.py`.
- `.bumpversion.cfg` for version management.

### Changed
- Reorganized `src/dataModelHelpers` into `foundationDataModelHelpers` and `foundationCLIHelpers`.

## [0.0.1] - 2025-09-20

### Added
- First release on PyPI.

[Unreleased]: https://github.com/kopecn/py-foundationTools/compare/v0.0.4...HEAD
[0.0.4]: https://github.com/kopecn/py-foundationTools/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/kopecn/py-foundationTools/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/kopecn/py-foundationTools/compare/70ebd16...v0.0.2
[0.0.1]: https://github.com/kopecn/py-foundationTools/commit/70ebd16
