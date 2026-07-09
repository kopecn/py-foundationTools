---
spec: MathTypeTiers
scope: project
status: implemented
applies_to: schema/schemas/Math/, schema/scripts/generateMathTypes.sh, schema/scripts/reuse/postprocess_mathtypes.py, src/foundationTypes/mathTypes/, src/foundation_abc/math/
last_updated: 2026-07-08
semver: 0.1.0
author: Nicholas Bergantz
---

# Math Type Tiers Specification

> **Status — implemented (Tier 1 + Tier 2).** Tier 3 is planned and lives
> outside this repository. This spec governs how every non-enum type under the
> `Math` schema domain is layered. It complements
> [`schemaCodegen.md`](schemaCodegen.md) (Tier 1's codegen authority) and
> [`dataModelHelper.md`](dataModelHelper.md) (the serialization base class every
> tier transitively inherits).

## Goal — SE(3) rigid body transformations

The `Position` / `Quaternion` / `SpatialTransform` family (`spatialABCs.py`) exists to
give **SE(3), the Lie group of 3D rigid body transformations (rotation +
translation)**, a storage-independent, serializable data contract:

- `PositionABC` — the translation part, a point in `R^3`.
- `QuaternionABC` — the rotation part, a unit quaternion (the standard double
  cover of `SO(3)`, the rotation subgroup of SE(3)).
- `SpatialTransformABC` — one SE(3) group element: a translation composed with a
  rotation, i.e. a pose.
- `WaveformSpatialABC` (and its single-component siblings `PositionWaveformABC`
  / `QuaternionWaveformABC`) — a uniformly-sampled trajectory through SE(3)
  over time.

This spec's tier split (below) is *how* that contract is layered so the data
shape stays independent of the math implementation; the group-theoretic
context above is *why* the family exists. Group operations (composition,
inverse, interpolation) belong on the `XxxxMathLike` tier, never on the
`XxxxLike` accessor contracts — see Invariant 1.

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
        XxxxLike   (ABC only, stdlib-only)   ← shared abstraction (bottom)
        /        \
  XxxxType     XxxxMathLike   (adds the math-op contract)
 (codegen,          \
  XxxxLike +          Xxxx   (downstream math engine: np.quaternion today,
  DataModelHelper)     a SIMD/GPU build tomorrow — interchangeable)
 data IO /
 storage /
 validation /
 plotting
```

## Tiers

| Role | Name | Lives in | Inherits |
|---|---|---|---|
| Shared abstraction | `XxxxLike` | hand-written, `foundation_abc/math/` | `ABC` |
| Codegen data carrier | `XxxxType` | generated `MathTypes.py` (`foundationTypes/mathTypes/`) | `XxxxLike`, `DataModelHelper` |
| Math-op interface | `XxxxMathLike` | hand-written, this repo | `XxxxLike` |
| Math implementation | `Xxxx` | downstream repo (e.g. `py-MathTools`) | `XxxxMathLike` |

- **`XxxxLike`** — abstract `@property` accessor per data field, a concrete
  `to_dict` built on those accessors (define serialization once), and an abstract
  `from_dict`. It declares **no math operations** (see the invariant below) and is
  **stdlib-only** (`ABC` alone, no `DataModelHelper`) — this is what lets it live
  in `foundation_abc/math/`, a zero-dependency leaf package, without creating a
  `foundationTypes -> foundation_abc -> foundationTypes` cycle (Plan 21). Downstream
  code that needs the serialization surface gets it from `XxxxType` (or a
  `Xxxx` math implementation that separately composes it), not from `XxxxLike`
  itself.
- **`XxxxType`** — the quicktype-generated dataclass. Pure data. Inherits **both**
  `XxxxLike` and `DataModelHelper` directly (ABC first in the base list — see
  Invariant 4 for why the order is load-bearing). Directly instantiable; used for
  serialization, validation, and plotting.
- **`XxxxMathLike`** — abstract `from_components` plus the math-op signatures
  (no bodies), so alternative engines stay interchangeable. Only math
  implementations inherit it; the codegen carrier does not.
- **`Xxxx`** — implemented downstream by subclassing `XxxxMathLike`, choosing its
  own storage and exposing the accessors as computed properties.

Enums (`NumericSign`, `Timescale`, `ReferenceFrame`) get no tier split. They are
hand-written in `foundation_abc/math/mathEnums.py` (a leaf module, stdlib-only,
that both `MathTypes.py` and the Tier-2 modules import, avoiding a circular
import); the codegen post-processor strips quicktype's inline copies and imports
these instead.

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
4. **`XxxxLike` must come first in `XxxxType`'s base list.** The generated
   declaration is `class XxxxType(XxxxLike, DataModelHelper):`, never the reverse.
   `XxxxLike` supplies the concrete `to_dict` and the abstract `@property`
   accessors that invariant 2's literal defaults shadow; putting `DataModelHelper`
   first would let its own (non-`XxxxLike`-aware) methods win the MRO and break
   that interaction. This is also what keeps `foundation_abc/math/` a
   zero-dependency leaf: `XxxxLike` itself never inherits `DataModelHelper` (see
   Tiers above) — the two are combined only here, on the generated carrier.

## Codegen

`schema/scripts/generateMathTypes.sh` consolidates all Math schemas whose `$ref`
graph is one connected component into a single quicktype invocation → one
`MathTypes.py` (per the "one invocation, one file" constraint in
[`schemaCodegen.md`](schemaCodegen.md)). Each object schema's `title` is its
public `XxxxType` name. `schema/scripts/reuse/postprocess_mathtypes.py` then
reparents each class to `(XxxxLike, DataModelHelper)` — ABC first, per invariant
4 — importing `XxxxLike` from `foundation_abc.math.<module>` and injecting the
`DataModelHelper` class import directly (the `XxxxLike` ABCs no longer carry it
transitively); it also extracts the enums (imported from
`foundation_abc.math.mathEnums`), imports the `data_model_helper` `from_*`/`to_*`
helpers, and injects the field defaults from invariant 2. `from_dict`/`to_dict`
normalization is the shared `run_ruff` pass. This post-processor is intentionally
Math-specific — the shared reuse libraries stay generic for the other generators.

## Compliance

A new Math object type MUST, when its schema is authored:

1. Use its public `XxxxType` name as the schema `title`.
2. Get a hand-written `XxxxLike` (accessors + serialization, `ABC`-only, in
   `foundation_abc/math/`) and `XxxxMathLike` (op contract) — the latter may be an
   empty scaffold while Tier 3 is unwritten.
3. Be added to `generateMathTypes.sh`'s `INPUT_SCHEMA_FILES` and to the
   post-processor's `TYPE_TO_LIKE` map (module name resolves under
   `foundation_abc.math`).
4. Pass `make uv-typecheck` after `make codegen-all`.
5. Not introduce any import from `foundationTypes`, `foundation_math`, or
   `foundation_tools` into the new `XxxxLike` module — enforced by
   `tests/test_package_layering.py`.
