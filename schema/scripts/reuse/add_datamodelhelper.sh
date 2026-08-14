#!/bin/bash
# =============================================================================
# add_datamodelhelper.sh — post-process quicktype output to use DataModelHelper.
#
# Source this file. Provides:
#
#   add_base_class <file> [Class1 Class2 ...]
#       Make the given classes inherit from DataModelHelper, injecting the
#       import if absent. With no class names, every parentless class is
#       converted (`class Foo:` -> `class Foo(DataModelHelper):`).
#
#   add_helper_imports <file>
#       Remove quicktype's inline helper function definitions and import the
#       equivalents from foundationTypes.data_model_helper instead.
#
# Typical call order:  add_base_class -> add_helper_imports -> run_ruff
# =============================================================================

readonly _DMH_IMPORT="from foundationTypes.data_model_helper import DataModelHelper"

_dmh_sed_inplace() {
    if sed --version >/dev/null 2>&1; then
        sed -i "$@"        # GNU sed (Linux)
    else
        sed -i '' "$@"     # BSD sed (macOS)
    fi
}

add_base_class() {
    local file="$1"; shift
    [ -f "$file" ] || return 1
    local base_class="DataModelHelper"

    if ! grep -qF "$_DMH_IMPORT" "$file"; then
        awk -v import_line="$_DMH_IMPORT" '
            /^from dataclasses import dataclass$/ { print; print import_line; next }
            { print }
        ' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
    fi

    if [ $# -eq 0 ]; then
        _dmh_sed_inplace \
            "s/^class \([A-Za-z_][A-Za-z0-9_]*\):$/class \1(${base_class}):/" "$file"
    else
        local class
        for class in "$@"; do
            _dmh_sed_inplace "s/^class ${class}:$/class ${class}(${base_class}):/" "$file"
        done
    fi
}

add_helper_imports() {
    local file="$1"
    [ -f "$file" ] || return 1

    # Helpers that DataModelHelper re-exports; mirror quicktype's generated set.
    local all_helpers=(
        from_bool from_dict from_float from_int from_list from_none
        from_str from_union to_class to_enum to_float
    )

    local found_helpers=() helper
    for helper in "${all_helpers[@]}"; do
        if grep -q "^def ${helper}(" "$file"; then
            found_helpers+=("$helper")
        fi
    done
    [ ${#found_helpers[@]} -eq 0 ] && return 0

    python3 - "$file" "${found_helpers[@]}" <<'PYEOF'
import re
import sys

file_path = sys.argv[1]
helpers = sys.argv[2:]

with open(file_path, encoding="utf-8") as f:
    content = f.read()

# Strip each inline `def helper(...):` block. The body is the run of indented
# or blank lines that follows the def line, up to the next top-level statement.
for helper in helpers:
    pattern = (
        rf"(?m)^def {re.escape(helper)}\([^\n]*\n"
        rf"(?:[ \t][^\n]*\n|\n)*"
    )
    content = re.sub(pattern, "", content)

# Collapse the blank-line runs the removals leave behind.
content = re.sub(r"\n{3,}", "\n\n", content)

old_import = "from foundationTypes.data_model_helper import DataModelHelper"
if old_import not in content:
    raise SystemExit(
        f"expected import not found in {file_path}; "
        "run add_base_class before add_helper_imports"
    )

items = ",\n    ".join(["DataModelHelper", *helpers])
new_import = (
    "from foundationTypes.data_model_helper import (\n"
    f"    {items},\n"
    ")"
)
content = content.replace(old_import, new_import)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
PYEOF
}
