#!/bin/bash
# =============================================================================
# codegen.sh — shared functions for schema-driven Python code generation.
#
# Source this file from a per-model generate script AFTER setting:
#   SCRIPT_DIR          absolute dir of the caller (resolve via BASH_SOURCE[0])
#   INPUT_SCHEMA_FILES  array of schema paths, relative to repo root
#   OUTPUT_PYTHON_REL   output path relative to the package base, e.g.
#                       "mathTypes/UnitSphericalArc.py"
#   PYTHON_VERSION      quicktype target (quicktype supports 3.5|3.6|3.7)
#
# On source it derives:
#   OUTPUT_PYTHON_FILE = <_PYTHON_TYPES_BASE>/<OUTPUT_PYTHON_REL>
# =============================================================================

readonly _PYTHON_TYPES_BASE="src/foundationTypes"

# Absolute path to this reuse dir, resolved at source time so the shared
# normalizer can be located regardless of the caller's working directory.
_CODEGEN_REUSE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

: "${OUTPUT_PYTHON_REL:?OUTPUT_PYTHON_REL must be set before sourcing codegen.sh}"
OUTPUT_PYTHON_FILE="${_PYTHON_TYPES_BASE}/${OUTPUT_PYTHON_REL}"

# Portable in-place sed (BSD/macOS needs an explicit empty backup-suffix arg).
_sed_inplace() {
    if sed --version >/dev/null 2>&1; then
        sed -i "$@"        # GNU sed (Linux)
    else
        sed -i '' "$@"     # BSD sed (macOS)
    fi
}

# Prefer the project's `uv run ruff` runner; fall back to a bare ruff on PATH.
_ruff() {
    if command -v uv >/dev/null 2>&1; then
        uv run ruff "$@"
    elif command -v ruff >/dev/null 2>&1; then
        ruff "$@"
    else
        echo "ERROR: neither 'uv' nor 'ruff' found on PATH" >&2
        return 1
    fi
}

setup_quicktype() {
    command -v quicktype >/dev/null 2>&1 || {
        echo "ERROR: quicktype not found on PATH (npm i -g quicktype)" >&2
        return 1
    }
    cd "$SCRIPT_DIR" || return 1
    cd ../.. || return 1          # schema/scripts -> repo root
    echo "DataModel generation running from: $(pwd)"
    quicktype -v
}

run_quicktype() {
    local output_file="$OUTPUT_PYTHON_FILE"
    mkdir -p "$(dirname "$output_file")"

    quicktype \
        --lang py \
        --src-lang schema \
        --python-version "$PYTHON_VERSION" \
        --out "$output_file" \
        --telemetry disable \
        --no-pydantic-base-model \
        "${INPUT_SCHEMA_FILES[@]}"

    echo "Generated: $output_file"
}

add_autogen_header() {
    local file="$1"
    local tmp_file="${file}.tmp"
    local header='# =============================================================================
# AUTO-GENERATED FILE — DO NOT EDIT
# Generated from JSON Schema via quicktype. Any manual edits will be
# overwritten the next time codegen runs (make codegen-all).
# To modify, update the source schema in schema/schemas/ and re-run codegen.
# ============================================================================='

    {
        printf '%s\n\n' "$header"
        cat "$file"
    } > "$tmp_file" && mv "$tmp_file" "$file"
}

# Opt-in: drop a trailing "Schema" from generated identifiers (e.g.
# FooSchema -> Foo). Written without \b so it works on BSD and GNU sed.
strip_schema_suffix() {
    local file="$1"
    _sed_inplace 's/Schema\([^A-Za-z0-9_]\)/\1/g; s/Schema$//' "$file"
}

fix_to_dict_return_type() {
    local file="$1"
    _sed_inplace 's/def to_dict(self) -> dict:/def to_dict(self) -> dict[str, Any]:/g' "$file"
    _sed_inplace 's/result: dict = {}/result: dict[str, Any] = {}/g' "$file"
    echo "Fixed to_dict return type in: $file"
}

# Rewrite quicktype's from_dict @staticmethod to the DataModelHelper @classmethod
# contract. Delegates to the shared normalizer (single source of truth) so the
# per-script path and the fleet-wide `make codegen-all` sweep apply the identical
# rewrite. Idempotent.
fix_from_dict_classmethod() {
    local file="$1"
    bash "${_CODEGEN_REUSE_DIR}/normalize_generated.sh" "$file"
}

run_ruff() {
    local file="${1:-$OUTPUT_PYTHON_FILE}"
    fix_to_dict_return_type "$file"
    fix_from_dict_classmethod "$file"
    _ruff format "$file"
    # --unsafe-fixes mirrors the uv-format target (Makefile): the generated tree
    # is held to the same autofix level as hand-written source. Do NOT drop it.
    _ruff check --fix --unsafe-fixes "$file"
}

ensure_py_typed() {
    # Always the package root, regardless of how deeply OUTPUT_PYTHON_REL nests
    # (e.g. "commonTypes/disk_usage/DiskUsage.py" is still under
    # foundationTypes) -- a dirname/dirname walk from ref_file assumes exactly
    # one level of nesting and breaks on a second.
    touch "${_PYTHON_TYPES_BASE}/py.typed"
    echo "Ensured py.typed: ${_PYTHON_TYPES_BASE}/py.typed"
}
