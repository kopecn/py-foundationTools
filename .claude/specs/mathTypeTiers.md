---
spec: MathTypeTiers
scope: project
status: implemented
applies_to: schema/schemas/Math/, schema/scripts/generateMathTypes.sh, schema/scripts/reuse/postprocess_mathtypes.py, src/foundationTypes/mathTypes/, src/foundation_abc/math/, tests/typeTests/test_math_tier_contract.py
last_updated: 2026-09-07
semver: 1.0.0
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
