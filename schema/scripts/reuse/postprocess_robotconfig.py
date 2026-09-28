#!/usr/bin/env python3
"""Robot-domain post-processor for quicktype output (RobotConfig.py).

Robot geometry `$ref`s the canonical Math schemas, so quicktype inlines concrete
Math carriers (``PositionType`` / ``QuaternionType`` / ``SpatialTransformType``)
into ``RobotConfig.py``. This post-processor rewires the generated module to the
two-tier model in ``.claude/specs/mathTypeTiers.md``: Robot fields are typed to the
storage-independent *protocols* in ``foundation_abc.math`` (dependency inversion),
and the concrete implementation constructed at deserialization is chosen through a
single, user-overridable ``ClassVar`` knob on ``RobotConfig`` — defaulting to the
Math carrier, which already conforms.

Transforms applied, in order:
  1. Strip the inlined concrete Math carrier class definitions (they live in
     ``foundationTypes.mathTypes.MathTypes`` — the single source of truth).
  2. Retype geometry *field annotations* from the concrete carrier to its ABC
     (``transform: SpatialTransformType`` -> ``transform: SpatialTransformABC``).
  3. Route construction through the knob: ``SpatialTransformType.from_dict`` ->
     ``RobotConfig.SPATIAL_TRANSFORM_IMPL.from_dict``. A downstream user injects
     their own implementation with ``RobotConfig.SPATIAL_TRANSFORM_IMPL = MyType``.
  4. Serialize through the protocol: ``to_class(SpatialTransformType, x)`` ->
     ``to_class_abc(SpatialTransformABC, x)`` (accepts any conforming value).
  5. Inject the ``ClassVar`` knob(s) into ``RobotConfig`` (default = Math carrier)
     and import the ABCs, the carriers (for the defaults), ``to_class_abc``, and
     ``ClassVar`` — only what is actually referenced.

DataModelHelper reparenting of the remaining Robot classes, helper-import
stripping, and the from_dict/to_dict normalization are left to the existing
add_datamodelhelper.sh + shared run_black / normalize_generated passes.
"""

from __future__ import annotations

import re
import sys

# Concrete Math carrier (as quicktype names it, from the Math schema title) ->
# (its structural protocol in foundation_abc.math, the ClassVar knob name on
# RobotConfig that selects the implementation to construct). All three protocols
# live in foundation_abc.math.spatialABCs.
GEOMETRY = {
    "PositionType": ("PositionABC", "POSITION_IMPL"),
    "QuaternionType": ("QuaternionABC", "QUATERNION_IMPL"),
    "SpatialTransformType": ("SpatialTransformABC", "SPATIAL_TRANSFORM_IMPL"),
}

_KNOB_HOST = "RobotConfig"
_CONCRETE_MODULE = "foundationTypes.mathTypes.MathTypes"
_ABC_MODULE = "foundation_abc.math.spatialABCs"
_HELPER_MODULE = "foundationTypes.data_model_helper"


def strip_class(content: str, name: str) -> str:
    """Remove a top-level ``@dataclass``/``class NAME:`` block and its body."""
    pattern = re.compile(
        rf"(?m)^@dataclass\nclass {re.escape(name)}:[^\n]*\n(?:[ \t][^\n]*\n|\n)*"
    )
    return pattern.sub("", content)


def retype_annotations(content: str, carrier: str, abc: str) -> str:
    """Replace a carrier used as a type annotation with its ABC.

    Matches the carrier when it follows ``:`` or ``[`` (a field or generic
    annotation) and is not an attribute access (``Carrier.from_dict``). Quoted
    forward references are handled too. Construction sites are left for the
    dedicated knob/serialize rewrites below.
    """
    content = re.sub(
        rf"([:\[]\s*){re.escape(carrier)}(?![\w.])",
        rf"\g<1>{abc}",
        content,
    )
    content = re.sub(
        rf"(['\"]){re.escape(carrier)}\1",
        rf"\g<1>{abc}\g<1>",
        content,
    )
    return content


def inject_knobs(content: str, decls: list[str]) -> str:
    """Insert ClassVar knob declarations into the RobotConfig class body."""
    # This runs before add_base_class, so RobotConfig may not yet have a parent;
    # tolerate an optional base-class clause.
    pattern = re.compile(
        r'(?ms)^(@dataclass\nclass ' + re.escape(_KNOB_HOST) + r"(?:\([^)]*\))?:\n)"
        r'(    (?:"""|\'\'\').*?(?:"""|\'\'\')\n)?'
    )
    match = pattern.search(content)
    if not match:
        raise SystemExit(f"postprocess_robotconfig: {_KNOB_HOST} class not found")
    at = match.end()
    return content[:at] + "".join(decls) + content[at:]


def main(path: str) -> None:
    with open(path, encoding="utf-8") as fh:
        content = fh.read()

    for carrier in GEOMETRY:
        content = strip_class(content, carrier)

    for carrier, (abc, knob) in GEOMETRY.items():
        content = retype_annotations(content, carrier, abc)
        # Construction -> user-overridable knob on RobotConfig.
        content = content.replace(
            f"{carrier}.from_dict", f"{_KNOB_HOST}.{knob}.from_dict"
        )
        # Serialization -> protocol-aware helper.
        content = content.replace(f"to_class({carrier},", f"to_class_abc({abc},")

    content = re.sub(r"\n{3,}", "\n\n", content)

    # Which protocols are actually in play (their knob is now referenced).
    in_play = [
        carrier
        for carrier, (_abc, knob) in GEOMETRY.items()
        if re.search(rf"\b{knob}\b", content)
    ]
    if not in_play:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        return

    knob_decls = [
        f"    {knob}: ClassVar[type[{abc}]] = {carrier}\n"
        for carrier in in_play
        for abc, knob in [GEOMETRY[carrier][:2]]
    ]
    content = inject_knobs(content, knob_decls)

    concrete_used = ", ".join(in_play)
    abc_used = ", ".join(GEOMETRY[c][0] for c in in_play)
    injected = (
        "from typing import ClassVar\n"
        f"from {_HELPER_MODULE} import to_class_abc\n"
        f"from {_CONCRETE_MODULE} import {concrete_used}\n"
        f"from {_ABC_MODULE} import {abc_used}\n"
    )

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
        raise SystemExit("usage: postprocess_robotconfig.py <RobotConfig.py>")
    main(sys.argv[1])
