---
spec: MathTypeTiers
scope: project
status: implemented
applies_to: schema/schemas/Math/, schema/scripts/generateMathTypes.sh, schema/scripts/reuse/postprocess_mathtypes.py, src/foundationTypes/mathTypes/
---

# Math Type Tiers Specification

> **Status — implemented (Tier 1 + Tier 2).** Tier 3 is planned and lives
> outside this repository. This spec governs how every non-enum type under the
> `Math` schema domain is layered. It complements
> [`schemaCodegen.md`](schemaCodegen.md) (Tier 1's codegen authority) and
> [`dataModelHelper.md`](dataModelHelper.md) (the serialization base class every
> tier transitively inherits).

## Why

A Math type has two independent concerns: a **data shape** (for IO, storage,
validation, plotting) and a **math implementation** (arithmetic, composition,
interpolation — which may want `np.quaternion`, SIMD, or GPU storage). Binding
those together — e.g. making a downstream math class inherit a concrete
`w/x/y/z: float` dataclass — freezes the storage and blocks alternative compute
backends. The Math family instead applies **dependency inversion**: one
storage-independent abstraction at the bottom, with several sibling
implementations that each choose their own storage yet "talk commonly" through
the shared abstraction.

```
        XxxxLike   (ABC + DataModelHelper)   ← shared abstraction (bottom)
        /        \
  XxxxType     XxxxMathLike   (adds the math-op contract)
 (codegen)          \
 data IO /           Xxxx   (downstream math engine: np.quaternion today,
 storage /                   a SIMD/GPU build tomorrow — interchangeable)
 validation /
 plotting
```

## Tiers

| Role | Name | Lives in | Inherits |
|---|---|---|---|
| Shared abstraction | `XxxxLike` | hand-written, this repo | `ABC`, `DataModelHelper` |
| Codegen data carrier | `XxxxType` | generated `MathTypes.py` | `XxxxLike` |
| Math-op interface | `XxxxMathLike` | hand-written, this repo | `XxxxLike` |
| Math implementation | `Xxxx` | downstream repo (e.g. `py-MathTools`) | `XxxxMathLike` |

- **`XxxxLike`** — abstract `@property` accessor per data field, a concrete
  `to_dict` built on those accessors (define serialization once), and an abstract
  `from_dict`. It declares **no math operations** (see the invariant below).
- **`XxxxType`** — the quicktype-generated dataclass. Pure data. Inherits
  `XxxxLike` and satisfies its accessors with plain fields. Directly
  instantiable; used for serialization, validation, and plotting.
- **`XxxxMathLike`** — abstract `from_components` plus the math-op signatures
  (no bodies), so alternative engines stay interchangeable. Only math
  implementations inherit it; the codegen carrier does not.
- **`Xxxx`** — implemented downstream by subclassing `XxxxMathLike`, choosing its
  own storage and exposing the accessors as computed properties.

Enums (`NumericSign`, `Timescale`, `ReferenceFrame`) get no tier split. They are
hand-written in `mathEnums.py` (a leaf module both `MathTypes.py` and the Tier-2
modules import, avoiding a circular import); the codegen post-processor strips
quicktype's inline copies and imports these instead.

## Invariants (empirically forced — do not "fix")

1. **`XxxxLike` carries accessors + serialization only, never abstract math
   ops.** A dataclass cannot inherit any abstract *method* it does not
   implement, and the codegen carrier implements no math. Ops therefore live on
   `XxxxMathLike`. Adding an abstract op to `XxxxLike` makes every `XxxxType`
   non-instantiable.
2. **Every codegen field must carry a literal class-level default.** An abstract
   `@property` is a *data descriptor*: without a shadowing class attribute it
   both keeps the class abstract and raises `property '<f>' has no setter` at
   construction. A literal default (never `field(default_factory=...)`, which
   sets no class attribute) supplies that shadow. The post-processor injects:
   scalars → `0.0` / `0` / `NumericSign.ZERO`; lists → `Sequence[...] = ()`
   (covariant, immutable); nested single-object carriers → `... | None = None`
   with `# type: ignore[assignment]` (the Optionality is a codegen-only tax —
   `from_dict` always supplies the value — kept off the Tier-2 contract).
3. **Accessor return types are covariant.** Lists use `Sequence[XxxxLike]` (not
   `list`, which is invariant); nested carriers are typed by the sibling
   `XxxxLike`, so both `XxxxType` and downstream impls satisfy the override under
   mypy strict.

## Codegen

`schema/scripts/generateMathTypes.sh` consolidates all Math schemas whose `$ref`
graph is one connected component into a single quicktype invocation → one
`MathTypes.py` (per the "one invocation, one file" constraint in
[`schemaCodegen.md`](schemaCodegen.md)). Each object schema's `title` is its
public `XxxxType` name. `schema/scripts/reuse/postprocess_mathtypes.py` then
reparents each class to its `XxxxLike`, extracts the enums, imports the
`dataModelHelper` helpers, and injects the field defaults from invariant 2;
`from_dict`/`to_dict` normalization is the shared `run_ruff` pass. This
post-processor is intentionally Math-specific — the shared reuse libraries stay
generic for the other generators.

## Compliance

A new Math object type MUST, when its schema is authored:

1. Use its public `XxxxType` name as the schema `title`.
2. Get a hand-written `XxxxLike` (accessors + serialization) and `XxxxMathLike`
   (op contract) — the latter may be an empty scaffold while Tier 3 is unwritten.
3. Be added to `generateMathTypes.sh`'s `INPUT_SCHEMA_FILES` and to the
   post-processor's `TYPE_TO_LIKE` map.
4. Pass `make uv-typecheck` after `make codegen-all`.
