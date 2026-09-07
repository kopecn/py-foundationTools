#!/usr/bin/env python3
"""Math-domain post-processor for quicktype output (MathTypes.py).

The generated ``XxxxType`` dataclasses are schema-faithful data carriers. They
inherit ``DataModelHelper`` for the repository's common IO surface and satisfy
the storage-independent protocols in ``foundation_abc.math`` structurally; they
do not inherit those protocols. This avoids colliding dataclass fields with
abstract property descriptors.

Transforms applied, in order:
  1. Strip quicktype's inline helper defs; import the equivalents from
     foundationTypes.data_model_helper.
  2. Strip the generated enum classes (NumericSign / Timescale / ReferenceFrame);
     import them from foundation_abc.math.mathEnums (single source of truth, also
     avoids a circular import with the Tier-2 modules).
  3. Reparent each ``class XxxxType:`` to ``class XxxxType(DataModelHelper):``
     and import ``DataModelHelper``. Required fields remain exactly as quicktype
     emitted them: non-optional and without constructor defaults.

from_dict (@staticmethod -> @classmethod) and to_dict return-type widening are
left to the shared run_ruff / normalize_generated pass, as for every generator.
"""

from __future__ import annotations

import re
import sys

HELPERS = [
    "from_bool",
    "from_dict",
    "from_float",
    "from_int",
    "from_list",
    "from_none",
    "from_str",
    "from_union",
    "to_class",
    "to_enum",
    "to_float",
]
ENUMS = ["NumericSign", "ReferenceFrame", "Timescale"]

def strip_block(content: str, header_regex: str) -> str:
    """Remove a top-level ``def``/``class`` block and its indented/blank body."""
    pattern = re.compile(rf"(?m)^{header_regex}[^\n]*\n(?:[ \t][^\n]*\n|\n)*")
    return pattern.sub("", content)


def main(path: str) -> None:
    with open(path, encoding="utf-8") as fh:
        content = fh.read()

    present_helpers = [h for h in HELPERS if re.search(rf"(?m)^def {h}\(", content)]
    for h in present_helpers:
        content = strip_block(content, rf"def {h}\(")
    for e in ENUMS:
        content = strip_block(content, rf"class {e}\(Enum\):")

    content = re.sub(
        r"(?m)^class (\w+Type):$",
        r"class \1(DataModelHelper):",
        content,
    )

    # Build the import block injected right after quicktype's own import section.
    helper_block = ""
    if present_helpers:
        items = ",\n    ".join(present_helpers)
        helper_block = f"from foundationTypes.data_model_helper import (\n    {items},\n)\n"
    dmh_block = "from foundationTypes.data_model_helper import DataModelHelper\n"
    enum_block = "from foundation_abc.math.mathEnums import " + ", ".join(ENUMS) + "\n"
    injected = helper_block + dmh_block + enum_block

    # Insert after the last top-level `from ... import ...` / `import ...` line
    # in the header (quicktype groups them at the top).
    lines = content.split("\n")
    last_import = 0
    for i, line in enumerate(lines[:60]):
        if re.match(r"^(from |import )", line):
            last_import = i
    lines.insert(last_import + 1, injected)
    content = "\n".join(lines)

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: postprocess_mathtypes.py <MathTypes.py>")
    main(sys.argv[1])
