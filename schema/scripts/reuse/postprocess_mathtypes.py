#!/usr/bin/env python3
"""Math-domain post-processor for quicktype output (MathTypes.py).

The Math family uses a 3-tier architecture (see .claude/specs/mathTypeTiers.md):
the generated ``XxxxType`` dataclass is the Tier-1 data carrier that inherits its
hand-written Tier-2 ``XxxxLike`` abstraction. quicktype does not know about that
abstraction, so this script rewrites its raw output to fit it. It is Math-specific
on purpose (per-class distinct parents, enum extraction, literal field defaults);
the shared reuse libraries stay generic for the other generators.

Transforms applied, in order:
  1. Strip quicktype's inline helper defs; import the equivalents from
     foundationTypes.dataModelHelper.
  2. Strip the generated enum classes (NumericSign / Timescale / ReferenceFrame);
     import them from foundationTypes.mathTypes.mathEnums (single source of truth,
     also avoids a circular import with the Tier-2 modules).
  3. Reparent each ``class XxxxType:`` to ``class XxxxType(XxxxLike):`` and inject
     the matching ``from foundationTypes.mathTypes.<module> import XxxxLike``.
  4. Give every field a literal class-level default so the inherited abstract
     ``@property`` accessor is satisfied (a data descriptor otherwise blocks
     instantiation): scalars -> 0.0 / 0 / NumericSign.ZERO; lists become
     ``Sequence[...] = ()``; nested single objects become ``... | None = None``;
     fields quicktype already defaulted (Optional[...] = None) are left alone.

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

# Type (public name) -> (module basename, Like class). Module basename is the
# lowercase-first of the Like class name (the type name minus "Type", plus "Like").
TYPE_TO_LIKE = {
    "QuaternionType": ("quaternionABC", "QuaternionABC"),
    "PositionVectorType": ("positionABC", "PositionABC"),
    "SpatialPoseType": ("spatialPoseABC", "SpatialPoseABC"),
    "PrecisionTimeIntervalType": ("precisionTimeIntervalABC", "PrecisionTimeIntervalABC"),
    "PrecisionTimestampType": ("precisionTimestampABC", "PrecisionTimestampABC"),
    "UnitSphericalArcType": ("unitSphericalArcABC", "UnitSphericalArcABC"),
    "UnitSphericalSmallCircleType": (
        "unitSphericalSmallCircleABC",
        "UnitSphericalSmallCircleABC",
    ),
    "PositionWaveformType": ("positionWaveformABC", "PositionWaveformABC"),
    "QuaternionWaveformType": ("quaternionWaveformABC", "QuaternionWaveformABC"),
    "SpatialPoseWaveformType": ("waveformSpatialABC", "WaveformSpatialABC"),
    "ScalarWaveformType": ("waveform1dABC", "Waveform1dABC"),
    "UnitSphericalArcWaveformType": (
        "waveformUnitSphericalArcABC",
        "WaveformUnitSphericalArcABC",
    ),
    "UnitSphericalSmallCircleWaveformType": (
        "waveformUnitSphericalSmallCircleABC",
        "WaveformUnitSphericalSmallCircleABC",
    ),
}

# Scalar field types -> literal default that clears the inherited abstract accessor.
SCALAR_DEFAULTS = {"float": "0.0", "int": "0", "NumericSign": "NumericSign.ZERO"}


def strip_block(content: str, header_regex: str) -> str:
    """Remove a top-level ``def``/``class`` block and its indented/blank body."""
    pattern = re.compile(rf"(?m)^{header_regex}[^\n]*\n(?:[ \t][^\n]*\n|\n)*")
    return pattern.sub("", content)


def field_default(field_type: str) -> str:
    """Return the ``  = ...`` (or ``| None = None`` / ``Sequence[...] = ()``)
    suffix/rewrite for a required field of ``field_type``."""
    field_type = field_type.strip()
    if field_type in SCALAR_DEFAULTS:
        return f"{field_type} = {SCALAR_DEFAULTS[field_type]}"
    list_match = re.fullmatch(r"List\[(.+)\]", field_type)
    if list_match:
        return f"Sequence[{list_match.group(1)}] = ()"
    # Nested single-object carrier (e.g. PositionVectorType). A literal `None`
    # default is the only thing that clears the inherited abstract `@property`
    # accessor (default_factory does not), but it makes the field Optional, which
    # is an incompatible override of the non-Optional Tier-2 accessor. That
    # Optionality is a codegen-only tax (from_dict always supplies the value), so
    # silence the override check here rather than pollute the Tier-2 contract.
    return f"{field_type} | None = None  # type: ignore[assignment]"


def inject_defaults(content: str) -> str:
    """Add a literal default to every required field of every XxxxType dataclass."""
    lines = content.split("\n")
    out: list[str] = []
    in_fields = False
    for line in lines:
        if re.match(r"^class \w+Type\(", line) or re.match(r"^class \w+Type:", line):
            in_fields = True
            out.append(line)
            continue
        if in_fields:
            # field section ends at the first method / decorator / dedent.
            if re.match(r"^    (@|def )", line) or (line and not line.startswith(" ")):
                in_fields = False
            else:
                m = re.match(r"^    (\w+): (.+)$", line)
                if m and " = " not in line and not m.group(2).lstrip().startswith('"'):
                    name, ftype = m.group(1), m.group(2)
                    out.append(f"    {name}: {field_default(ftype)}")
                    continue
        out.append(line)
    return "\n".join(out)


def main(path: str) -> None:
    with open(path, encoding="utf-8") as fh:
        content = fh.read()

    present_helpers = [h for h in HELPERS if re.search(rf"(?m)^def {h}\(", content)]
    for h in present_helpers:
        content = strip_block(content, rf"def {h}\(")
    for e in ENUMS:
        content = strip_block(content, rf"class {e}\(Enum\):")

    # Reparent each XxxxType to its Like and collect the Like imports needed.
    like_imports: list[str] = []
    for type_name, (module, like) in TYPE_TO_LIKE.items():
        new, n = re.subn(rf"(?m)^class {type_name}:$", f"class {type_name}({like}):", content)
        if n:
            content = new
            like_imports.append(f"from foundationTypes.mathTypes.{module} import {like}")

    content = inject_defaults(content)

    # Build the import block injected right after quicktype's own import section.
    helper_block = ""
    if present_helpers:
        items = ",\n    ".join(present_helpers)
        helper_block = f"from foundationTypes.dataModelHelper import (\n    {items},\n)\n"
    enum_block = "from foundationTypes.mathTypes.mathEnums import " + ", ".join(ENUMS) + "\n"
    seq_block = "from collections.abc import Sequence\n"
    injected = seq_block + helper_block + enum_block + "\n".join(sorted(like_imports)) + "\n"

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
