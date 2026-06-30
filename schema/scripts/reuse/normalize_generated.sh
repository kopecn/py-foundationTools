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
# Currently normalizes the from_dict constructor. quicktype emits:
#     @staticmethod
#     def from_dict(obj: Any) -> "Foo":
# which is rewritten to a @classmethod taking cls (return annotation preserved):
#     @classmethod
#     def from_dict(cls, obj: Any) -> "Foo":
#
# Idempotent: re-running is a no-op. Safe on hand-written files — the pattern
# only matches quicktype's generated staticmethod form, which hand-authored
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
pattern = re.compile(r"(?m)^([ \t]+)@staticmethod\n\1def from_dict\(obj: Any\) -> ")
replacement = r"\1@classmethod\n\1def from_dict(cls, obj: Any) -> "

for path in sys.argv[1:]:
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    new, n = pattern.subn(replacement, content)
    if n:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(new)
        print(f"normalized {n} from_dict staticmethod(s) -> classmethod: {path}")
PYEOF
