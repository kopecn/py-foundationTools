#!/bin/bash
# =============================================================================
# normalize_generated.sh — fleet-wide normalization of quicktype output to the
# DataModelHelper contract.
#
# Single source of truth for post-quicktype rewrites that MUST reach every
# generated model, regardless of which generate script produced it — conforming
# (golden template), legacy/non-conforming, or not-yet-written. Both paths call
# this script:
#   - codegen.sh's run_ruff applies it per-file (correct output when a single
#     generate script is run on its own).
#   - `make codegen-all` applies it once over the whole generated tree as a final
#     guaranteed sweep (poka-yoke: a sloppy or future script cannot escape it).
#
# Normalizes two quicktype artifacts:
#
# 1. from_dict constructor. quicktype emits:
#     @staticmethod
#     def from_dict(obj: Any) -> "Foo":
# which is rewritten to a @classmethod taking cls (return annotation preserved):
#     @classmethod
#     def from_dict(cls, obj: Any) -> "Foo":
#
# 2. Required-but-untyped dataclass fields that trail a defaulted field. When
# quicktype merges a schema union (e.g. an anyOf of several notification
# "params" objects) into one Python dataclass, a field that is required in
# its source schema but has no JSON Schema "type" (so quicktype can only
# infer `Any`) is emitted as a bare
#     data: Any
# with no default. On its own this is fine — dataclass only objects when a
# defaultless field follows a defaulted one. That happens specifically when
# the merge makes some *other* field optional (default None) while `data`
# stays required, landing it after a defaulted field and tripping mypy's
# "Attributes without a default cannot follow attributes with one" / a real
# dataclass TypeError. Since `Any` already accepts None, backfilling
# `= None` is safe there. But the same bare `data: Any` also occurs in the
# single-schema (non-merged) params class, where it legitimately precedes
# another required, concretely-typed field (e.g. `level: Level`) with no
# violation — patching it unconditionally would inject a default ahead of
# that still-required field and manufacture a new ordering violation.
# So this pass is stateful per dataclass: only fields, of the exact bare
# `Any` form, seen *after* the first defaulted field in the same class are
# rewritten to `= None`. Fields that are still in the leading defaultless
# run are left untouched.
#
# Idempotent: re-running is a no-op. Safe on hand-written files — both
# patterns only match quicktype's generated forms, which hand-authored
# DataModelHelper subclasses do not use.
#
# Usage:
#   normalize_generated.sh <file-or-dir> [<file-or-dir> ...]
# Each directory is searched recursively for *.py.
# =============================================================================
set -euo pipefail

[ $# -ge 1 ] || {
    echo "usage: normalize_generated.sh <file-or-dir> [<file-or-dir> ...]" >&2
    exit 2
}

files=()
for path in "$@"; do
    if [ -d "$path" ]; then
        while IFS= read -r f; do files+=("$f"); done \
            < <(find "$path" -type f -name '*.py')
    elif [ -f "$path" ]; then
        files+=("$path")
    fi
done
[ ${#files[@]} -gt 0 ] || exit 0

python3 - "${files[@]}" <<'PYEOF'
import re
import sys

# quicktype's generated from_dict staticmethod -> DataModelHelper classmethod.
# The concrete `-> "Foo"` return annotation and the method body are preserved.
classmethod_pattern = re.compile(r"(?m)^([ \t]+)@staticmethod\n\1def from_dict\(obj: Any\) -> ")
classmethod_replacement = r"\1@classmethod\n\1def from_dict(cls, obj: Any) -> "

# Bare, defaultless `name: Any` dataclass field, but only once a preceding
# field in the same class has already introduced a default.
field_line_pattern = re.compile(r"^( +)(\w+): (.+)$")


def fix_trailing_untyped_fields(content: str) -> tuple[str, int]:
    lines = content.split("\n")
    in_dataclass = False
    in_docstring = False
    field_indent = None
    seen_default = False
    fixed = 0

    for i, line in enumerate(lines):
        # Field docstrings (`"""..."""`, possibly multi-line) sit right after
        # a field declaration; skip their content so a paragraph line like
        # "Default: false" is never mistaken for a field decl.
        if in_docstring:
            if line.count('"""') % 2 == 1:
                in_docstring = False
            continue
        stripped = line.strip()
        if stripped.startswith('"""') and stripped.count('"""') % 2 == 1:
            in_docstring = True
            continue
        if stripped == "@dataclass":
            in_dataclass = True
            field_indent = None
            seen_default = False
            continue
        if not in_dataclass:
            continue
        if stripped.startswith(("@classmethod", "@staticmethod", "def ")):
            in_dataclass = False
            continue

        m = field_line_pattern.match(line)
        if not m:
            continue
        indent, name, rest = m.group(1), m.group(2), m.group(3)
        if field_indent is None:
            field_indent = indent
        elif indent != field_indent:
            continue  # nested/continuation line, not a field declaration

        has_default = " = " in rest
        if has_default:
            seen_default = True
        elif seen_default:
            if rest == "Any":
                lines[i] = f"{indent}{name}: Any = None"
                fixed += 1
            else:
                print(
                    f"WARNING: {path}: field '{name}: {rest}' has no default but "
                    "follows a defaulted field, and is not a bare `Any` this pass "
                    "can safely default — dataclass field order needs a manual fix",
                    file=sys.stderr,
                )

    return "\n".join(lines), fixed


for path in sys.argv[1:]:
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    changed = False
    new, n = classmethod_pattern.subn(classmethod_replacement, content)
    if n:
        content = new
        changed = True
        print(f"normalized {n} from_dict staticmethod(s) -> classmethod: {path}")
    new, n = fix_trailing_untyped_fields(content)
    if n:
        content = new
        changed = True
        print(f"defaulted {n} untyped required field(s) (Any -> Any = None): {path}")
    if changed:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
PYEOF
