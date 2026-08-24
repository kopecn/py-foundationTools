---
plan: ActionPlan02PresentationCodegen
scope: project
status: complete
last_updated: 2026-08-23
semver: 0.0.2
author: Nicholas Bergantz
---

# 02 — Presentation Codegen

## Goal

Generate `presentationTypes/Presentations.py` from the four linked schemas via one conforming script.

Contract: [presentationSchema.md](../specs/presentationSchema.md) R10, governed by [schemaCodegen.md](../specs/schemaCodegen.md).

## Depends on

Chunk 01 — the schemas must be linked before quicktype can resolve the `$ref` graph.

## Files

Create:
- `schema/scripts/generatePresentations.sh`
- `src/foundationTypes/presentationTypes/Presentations.py` (generated output — do not author by hand)
- `src/foundationTypes/presentationTypes/__init__.py`

No Makefile edit. `codegen-all` globs `schema/scripts/*.sh`.

## Design constraints

**Chamber match is a hard rule.** `schemaCodegen.md:38-45`: a diff of any two conforming scripts with model names filtered out must be empty. Copy `generateDiskUsage.sh` and change only the variable block. Do not copy `generateStandardizedLoggerConfig.sh` or `generateModelContextProtocol.sh` — both carry a stale `UnitSphericalArc` banner comment.

The script, in full:

```bash
#!/bin/bash

set -euo pipefail

# =============================================================================
# Generate Presentations Python types from JSON Schema.
# =============================================================================

# === Input schemas (relative to repo root) ===
INPUT_SCHEMA_FILES=(
  "schema/schemas/Presentations/PresentationColorTheme-schema.json"
  "schema/schemas/Presentations/PresentationMetadata-schema.json"
  "schema/schemas/Presentations/PresentationSlideLayouts-schema.json"
  "schema/schemas/Presentations/PresentationDeck-schema.json"
)

# === Classes that should inherit from DataModelHelper ===
CLASSES_FOR_BASE_PARENT=(
    "PresentationColorTheme"
    "PresentationMetadata"
    "PresentationSlideLayouts"
    "PresentationDeck"
)

# === Output (relative to src/foundationTypes) ===
OUTPUT_PYTHON_REL="presentationTypes/Presentations.py"

# === quicktype target. quicktype only emits up to 3.7; modern typing is
#     restored afterwards by run_ruff (UP rules) + fix_to_dict_return_type. ===
PYTHON_VERSION="3.7"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$SCRIPT_DIR/reuse/codegen.sh"
source "$SCRIPT_DIR/reuse/add_datamodelhelper.sh"

echo "Generating Python types: $OUTPUT_PYTHON_FILE"
echo "    from schemas: ${INPUT_SCHEMA_FILES[*]}"

setup_quicktype
run_quicktype
add_base_class "$OUTPUT_PYTHON_FILE" "${CLASSES_FOR_BASE_PARENT[@]}"
add_helper_imports "$OUTPUT_PYTHON_FILE"
add_autogen_header "$OUTPUT_PYTHON_FILE"
run_ruff "$OUTPUT_PYTHON_FILE"
ensure_py_typed "$OUTPUT_PYTHON_FILE"
```

Indentation is load-bearing for the chamber-match diff: `INPUT_SCHEMA_FILES` entries take 2 spaces, `CLASSES_FOR_BASE_PARENT` entries take 4. This inconsistency is uniform across all five existing scripts — reproduce it, do not tidy it.

**All four schemas in one invocation.** quicktype resolves `$ref` only within a single run and emits exactly one file. Listing order is cosmetic; leaf-dependency-first reads best.

**Flat module, no subfolder.** `schemaCodegen.md:132-142` reserves the per-model folder shape for models with hand-written wire behavior. Presentations has none — a deck is read from disk, not from a CLI transport. If `wire_invoke`/`wire_encode` is ever wanted, that is a later chunk that restructures into `presentationTypes/presentations/` with a `wire_config.py` sibling.

**`__init__.py`** re-exports the four top-level classes. Follow `commonTypes/disk_usage/__init__.py`, minus the `wire_config` side-effect import that this module does not need.

**Watch the known gap.** `schemaCodegen.md:174-184`: quicktype can emit a required field after a defaulted one, producing an import-time `TypeError` and a mypy `misc` error. `normalize_generated.sh` corrects the `data: Any` case only. If it bites, fix the schema's field order — never the generated `.py`.

## Steps (TDD)

1. Write `tests/typeTests/testPresentations.py` importing `PresentationDeck` from the not-yet-generated module. Run it — it fails on import.
2. Write the script.
3. `make codegen-all`.
4. Write `__init__.py`.
5. Re-run — import succeeds.
6. `make uv-typecheck`, then `make uv-fullCheck`.

## Acceptance criteria

- [x] `diff <(sed -E 's/DiskUsage|Presentations?//g' schema/scripts/generateDiskUsage.sh) <(sed -E 's/DiskUsage|Presentations?//g' schema/scripts/generatePresentations.sh)` differs only inside the two variable arrays (plus an explanatory comment inside that same block — see Resolution notes) and the output path.
- [x] `make codegen-all` regenerates the module with no diff on a second consecutive run (idempotent).
- [x] `src/foundationTypes/presentationTypes/Presentations.py` carries the standard six-line autogen header.
- [x] All four top-level classes subclass `DataModelHelper` (and so do the 12 nested dataclasses — see Resolution notes).
- [x] `from foundationTypes.presentationTypes import PresentationDeck` succeeds at import time (no field-ordering `TypeError`).
- [x] `make uv-fullCheck` passes.

## Out of scope

- Any schema shape change (chunk 01 owns that; if codegen forces one, fix it there and note it).
- Editing the generated `.py` for any reason.
- `wire_config.py` / wire behavior.
- Modifying the shared libraries under `schema/scripts/reuse/`.

## Resolution notes

- **`CLASSES_FOR_BASE_PARENT` needed all 16 dataclasses, not the plan's literal 4.** The literal script text in this chunk listed only the four schema-root classes (`PresentationColorTheme`, `PresentationMetadata`, `PresentationSlideLayouts`, `PresentationDeck`). Under `mypy --strict`, `data_model_helper.to_class(c: type[DMH], x)` requires its argument class to itself be a `DataModelHelper`, and every nested dataclass (`PresentationColor`, `PresentationAccent`, `RegionDefaults`, `Notes`, `LayoutDefaults`, `Region`, `SlideLayout`, `Defaults`, `File`, `Style`, `ContentBlock`, `Slide`) is passed through `to_class()` inside some parent's `to_dict()`. This is the same reasoning `generateDiskUsage.sh` already applies at a smaller scale (`DiskUsageEntry` + `DiskUsage`, not just `DiskUsage`) — Presentations just nests deeper. Listing all 16 in the variable array is filling in that same customization point the golden template reserves for per-model class names, not a deviation from pipeline structure; the chamber-match diff still isolates the change to the two variable arrays (plus the explanatory comment placed inside that same block) and the output path.
- **Cross-file fragment `$ref` resolved cleanly.** `contentBlock.style.color` refs `PresentationSlideLayouts-schema.json#/definitions/themeColorRef` (chunk 01's resolution notes flagged this as untested in this repo). quicktype 23.2.6 resolved it correctly and reused the single generated `ThemeColorRef` enum rather than duplicating it — no post-processing needed.
- No schema shape change was forced by codegen; `PresentationSlideLayouts.regions`/`slideLayout.regions` minItems and the rest of chunk 01's output generated without incident.
