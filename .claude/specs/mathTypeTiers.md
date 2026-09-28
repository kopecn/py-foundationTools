---
spec: MathTypeTiers
scope: project
status: implemented
applies_to: schema/schemas/Math/, schema/schemas/Robot/, schema/scripts/generateMathTypes.sh, schema/scripts/generateRobotConfig.sh, schema/scripts/reuse/postprocess_mathtypes.py, schema/scripts/reuse/postprocess_robotconfig.py, src/foundationTypes/mathTypes/, src/foundationTypes/automationTypes/, src/foundation_abc/math/, tests/typeTests/test_math_tier_contract.py, tests/typeTests/testRobotConfigGeometry.py
last_updated: 2026-09-28
semver: 1.2.0
author: Nicholas Bergantz
---

# Math data and interface boundaries

## Purpose

The Math domain needs two independent things:

1. schema-backed values for validation, serialization, file IO, and transport; and
2. storage-independent interfaces that algorithms can accept without depending on
   a particular concrete representation.

Those concerns interoperate through structural typing. They do not share a class
hierarchy.

```text
JSON Schema -> XxxxType(DataModelHelper)  ── structurally satisfies ──> XxxxABC Protocol
                      ^                                              ^
                      |                                              |
             generated storage                            alternate math storage
```

The existing `XxxxABC` names are retained as public API names. Their implementation
is `typing.Protocol`, because the contract describes readable shape rather than a
required storage base class.

## Schema-backed carriers

`src/foundationTypes/mathTypes/MathTypes.py` is generated from the Math JSON schemas.
Each non-enum model is an ordinary dataclass with one concrete parent:
`DataModelHelper`.

- JSON Schema is authoritative for field names and requiredness.
- A schema-required field is a non-optional constructor argument with no default.
- A schema-optional field may use `None`; currently these are the optional
  `PrecisionTimestampType` metadata fields.
- Generated `from_dict` and `to_dict` own the wire representation.
- `DataModelHelper` supplies the shared file, JSON, byte, wire, and environment IO
  extensions.

## Structural interfaces

`src/foundation_abc/math/` contains stdlib-only protocols for positions,
quaternions, transforms, spherical geometry, precision time, and waveforms.
They declare readable properties plus the `from_dict` / `to_dict` serialization
surface, but they do not implement wire mappings or math operations.

A generated carrier conforms because its fields and methods have compatible types;
it does not inherit a protocol. An alternate implementation can use properties,
native arrays, SIMD/GPU storage, or another representation and satisfy the same
protocol. Concrete IO behavior is opt-in: implementations that need
`DataModelHelper` inherit it directly or convert through a generated carrier.

Enums (`NumericSign`, `Timescale`, and `ReferenceFrame`) remain concrete shared
values in `foundation_abc/math/mathEnums.py`. Generated carriers import them so the
schema and protocol layers use the same enum identities.

## Cross-domain reuse (dependency inversion)

Other domains reuse the Math geometry contracts by **typing their fields to the
protocols**, not to the concrete carriers. The `automationTypes` (Robot) domain is
the reference case:

- A Robot schema that needs a position or pose `$ref`s the canonical Math schema
  (`Math/Position-schema.json`, `Math/Quaternion-schema.json`,
  `Math/SpatialTransform-schema.json`) rather than defining a parallel primitive.
- quicktype inlines the concrete Math carriers into `RobotConfig.py`. The
  Robot post-processor (`schema/scripts/reuse/postprocess_robotconfig.py`) then
  strips those inlined copies, imports the canonical carriers from
  `foundationTypes.mathTypes.MathTypes`, and **retypes the fields to the protocols**
  (`position: PositionType` → `position: PositionABC`, etc.).
- The field type is therefore the interface — it accepts any conforming
  implementation. A protocol cannot be instantiated, so deserialization resolves a
  concrete implementation through a single **user-overridable `ClassVar` knob** on
  the domain's root class (`RobotConfig.SPATIAL_TRANSFORM_IMPL`), defaulting to the
  Math carrier (which already conforms). A downstream caller injects their own type
  with `RobotConfig.SPATIAL_TRANSFORM_IMPL = MyTransform`; every geometry `from_dict`
  reads the current knob. Serialization goes through `to_class_abc` (in
  `data_model_helper.py`), which accepts any value satisfying the protocol.
- The protocols are made `@runtime_checkable` so `to_class_abc`'s isinstance guard
  works. That decorator adds no wire mapping, IO, or math — invariant 3 holds.

**Canonical rotation.** Orientation is a unit quaternion. Alternate rotation
representations (rotation matrix, axis-angle, roll/pitch/yaw) are **not** modeled as
separate protocols or carriers; they are derivatives of the quaternion and convert
to it, because a single canonical representation is more numerically robust.

**Isolated cases.** Concepts that are neither a position nor a pose are not forced
onto these protocols: a unit **direction** axis (a joint's rotation/translation/screw
axis) and an se(3) **twist** (`[wx,wy,wz,vx,vy,vz]` screw axis) stay as plain array
primitives. `spatialABCs.py` explicitly scopes se(3) twists out. A `DirectionABC`/
twist protocol is a possible future addition, addressed individually if needed.

## Invariants

1. **Generated carriers inherit `DataModelHelper`, not field protocols.** Abstract
   property descriptors must never be injected into generated dataclass MROs.
2. **Schema requiredness reaches Python unchanged.** Codegen must not add fabricated
   scalar, collection, nested-object, or `None` defaults to required fields.
3. **Math shape interfaces are structural.** They subclass `typing.Protocol` and
   must remain free of concrete wire mappings, IO behavior, and math operations.
4. **Read-only collection accessors use `Sequence`.** This permits carriers backed
   by `list` and alternate implementations backed by other sequence types.
5. **The postprocessor is narrow.** It extracts shared enums, imports the common
   serialization helpers, and adds `DataModelHelper`; it does not rewrite field
   annotations or defaults.

## Code generation

`schema/scripts/generateMathTypes.sh` passes the connected Math schema graph to one
quicktype invocation. `schema/scripts/reuse/postprocess_mathtypes.py` then:

1. replaces quicktype's local helper functions with the shared
   `foundationTypes.data_model_helper` helpers;
2. replaces quicktype's generated enum copies with the shared Math enums; and
3. makes each generated `XxxxType` a direct `DataModelHelper` subclass.

The shared normalization pass converts `from_dict` to the project classmethod
contract, replaces assertion-only input guards, and formats the result.

## Compliance

A new Math object type must:

1. declare its public type name and required fields in JSON Schema;
2. be included in `generateMathTypes.sh`;
3. have a compatible structural protocol when algorithms need a representation-
   independent contract;
4. add representative payload and required-field entries to
   `tests/typeTests/test_math_tier_contract.py`;
5. pass regeneration, strict type checking, and the full test suite; and
6. keep `foundation_abc` free of imports from `foundationTypes`, `foundation_math`,
   and `foundation_tools`.
