---
last_updated: 2026-07-08
semver: 0.1.0
author: Nicholas Bergantz
status: complete
---

# Plan 21 — Move Math ABCs to `foundation_abc/math/` and Break the `DataModelHelper` Inheritance

## Problem

The four math ABC modules (`spatialABCs.py`, `sphericalABCs.py`, `waveformABCs.py`,
`precisionTimeABC.py`) live in `src/foundationTypes/mathTypes/` and each ABC is
declared `class XxxxABC(ABC, DataModelHelper)`. That inheritance is the only thing
keeping them out of `foundation_abc`: moving them as-is would give `foundation_abc`
a dependency on `foundationTypes`, and since the generated `MathTypes.py` (in
`foundationTypes`) inherits the ABCs, a package-level cycle
`foundationTypes → foundation_abc → foundationTypes` would result.

**Chosen approach (option 4 of the evaluated set):** break the inheritance instead
of moving the base. The ABCs drop `DataModelHelper` and become stdlib-only; they
move to a new `foundation_abc/math/` subpackage; the codegen post-processor makes
each generated `XxxxType` inherit **both** its ABC and `DataModelHelper` directly.
`foundation_abc` stays a zero-dependency leaf; the dependency arrow is strictly
`foundationTypes → foundation_abc`.

## Evidence / Investigation Findings

Investigated 2026-07-08 (two Explore passes over codegen pipeline + usage map).

**The inheritance costs nothing to break.** No code anywhere in the repo calls a
`DataModelHelper`-provided method (`save_to_file`, `to_bytes`, `to_wire`,
`from_env`, …) through an ABC-typed value — grep across `src/` and `tests/` for all
such methods near math types: zero hits. The only serialization surface exercised
through the ABCs is `to_dict`/`from_dict`, and every ABC implements `to_dict`
concretely itself (e.g. `spatialABCs.py:50-51`) and declares `from_dict` abstract.
The ABC files import `DataModelHelper` purely for the base-class list
(`spatialABCs.py:25`, `sphericalABCs.py:15`, `waveformABCs.py:17`,
`precisionTimeABC.py:14`). Consequently **no `SupportsDataModel` Protocol is
needed** — the earlier concern that APIs typed against the ABCs would lose the
serialization surface is empirically unfounded.

**Blast radius is small and codegen-centric:**

- `MathTypes.py` is the **only** module that inherits the ABCs (13 concrete
  classes, e.g. `MathTypes.py:83` `class PositionType(PositionABC):`). It is fully
  regenerated, so it is not hand-edited — the change lands in the post-processor.
- `MathTypes.py` currently does **not** import the `DataModelHelper` class at all —
  only the `from_*`/`to_*` helper functions (`MathTypes.py:13-22`).
  `DataModelHelper` reaches the generated types only transitively via the ABC.
- **The math family does not use the generic shell injector.**
  `schema/scripts/generateMathTypes.sh` sources only `reuse/codegen.sh`
  (`generateMathTypes.sh:54`) and delegates all reparenting to
  `schema/scripts/reuse/postprocess_mathtypes.py` (`generateMathTypes.sh:63`).
  `reuse/add_datamodelhelper.sh` is untouched by this plan.
- The post-processor's exact edit sites:
  - `postprocess_mathtypes.py:55-72` — `TYPE_TO_LIKE` maps each `XxxxType` to
    `(module_basename, ABC_name)`; module paths feed the import injection.
  - `postprocess_mathtypes.py:139` — the reparent substitution
    `f"class {type_name}({like}):"` (single parent today).
  - `postprocess_mathtypes.py:142` — injects
    `from foundationTypes.mathTypes.{module} import {like}` (path changes).
  - `postprocess_mathtypes.py:147-153` — injected import block (must gain the
    `DataModelHelper` class import; `mathEnums` import path at ~L151 changes).
- **`mathEnums.py` must move too.** `precisionTimeABC.py:15` imports
  `foundationTypes.mathTypes.mathEnums` — left behind, it would re-couple
  `foundation_abc` to `foundationTypes`. `mathEnums.py` is hand-written,
  stdlib-only (pure `Enum` subclasses), so it is a legitimate `foundation_abc`
  citizen. `MathTypes.py`'s import of it (`MathTypes.py:23`) is codegen-injected,
  so the path change is one post-processor edit.
- `waveformABCs.py:18-26` imports its sibling ABCs (return-type annotations only);
  these become intra-`foundation_abc.math` imports and move together.
- No `isinstance`/`issubclass`/ABC-registration anywhere; tests import only the
  concrete `XxxxType` classes (`tests/typeTests/testUnitSphericalArc.py:4`), never
  the ABCs. `foundation_math` and `foundation_tools` do not import `mathTypes` at
  all. `foundationTypes` does not import `foundation_abc` today.
- The `*MathLike` modules named in ABC docstrings (`spatialABCs.py:17-19` etc.) do
  not exist as files — docstring/spec forward-references only. No code to migrate.
- Specs asserting the current shape: `.claude/specs/mathTypeTiers.md` — frontmatter
  `applies_to` (L5), tier diagram (L53-62), tier table `XxxxLike` "Inherits `ABC`,
  `DataModelHelper`" (L66-71), codegen description (L113-122), compliance checklist
  (L126-133). `.claude/specs/schemaCodegen.md:52-55` describes `add_base_class` but
  the math family is already the documented exception (`mathTypeTiers.md:121-122`).
- Verification path: `make codegen-all` (`Makefile:501-513`) regenerates + runs the
  fleet normalizer + ruff; `make uv-fullCheck` is the CI gate.
- `py.typed` markers exist per-subpackage (`src/foundation_abc/py.typed`,
  `src/foundationTypes/mathTypes/py.typed`); wildcard
  `[tool.setuptools.package-data] "*" = ["*.*"]` ships them.

**Decisions taken (user, 2026-07-08):**

1. **Layout:** `foundation_abc/math/` subpackage (not flat) — groups the five
   modules and keeps the top level clean as more ABC domains arrive.
2. **Compat:** clean break — old `foundationTypes.mathTypes.<abc module>` paths are
   deleted, no re-export shims. Pre-release library; zero in-repo consumers of the
   old paths survive the move.

## Proposed Approach

Target state:

```
src/foundation_abc/
├── __init__.py                    (unchanged, empty — direct submodule imports)
├── py.typed
├── peripheralByteTransport.py
└── math/
    ├── __init__.py                (empty, matching package convention)
    ├── py.typed
    ├── mathEnums.py               (moved verbatim; stdlib-only)
    ├── precisionTimeABC.py        (DataModelHelper base dropped; mathEnums import → sibling)
    ├── spatialABCs.py             (DataModelHelper base dropped)
    ├── sphericalABCs.py           (DataModelHelper base dropped)
    └── waveformABCs.py            (DataModelHelper base dropped; sibling imports → foundation_abc.math)
```

Inheritance chain changes from
`XxxxType → XxxxABC → (ABC, DataModelHelper)` to
`XxxxType → (XxxxABC → ABC, DataModelHelper)` — the generated class carries the
serialization base directly. **MRO rule: the ABC must stay first** in the generated
base list (`class PositionType(PositionABC, DataModelHelper):`) so the abstract
`@property` accessors and the injected literal field defaults keep interacting
per Invariant 2 of `mathTypeTiers.md` (L97-105), and so the ABCs' concrete
`to_dict` wins over `DataModelHelper`'s.

`foundation_abc` remains importable with zero non-stdlib, non-self imports — that
property is the point of the plan and gets a dedicated test.

## Alternatives Considered

Evaluated in conversation before this plan; recorded for reviewers:

1. **Do nothing** — placement itch, not a coupling problem; rejected in favor of
   formalizing the contracts in the ABC package.
2. **New tier-0 package (`foundation_core`) for `DataModelHelper`** — cleanest
   layering but adds a fifth top-level package; rejected as heavier than needed.
3. **Move `DataModelHelper` into `foundation_abc`** — no cycle (it is stdlib-only)
   but dilutes `foundation_abc` with a large concrete implementation.
4. **(Chosen)** break inheritance; ABCs stdlib-only in `foundation_abc`; generated
   types inherit both. Investigation removed its main cost (no Protocol needed).

## Risks

- **MRO / dataclass interaction.** `DataModelHelper` was already in every generated
  type's MRO (via the ABC), so runtime behavior should be identical — but the base
  order in the substitution string is load-bearing (ABC first). Mitigation: the
  existing type tests (`tests/typeTests/`) exercise `to_dict`/`from_dict` round
  trips; `make uv-typecheck` is strict.
- **Downstream consumers** importing `foundationTypes.mathTypes.spatialABCs` (etc.)
  or `foundationTypes.mathTypes.mathEnums` break — accepted (clean-break decision,
  pre-release). Call it out in HISTORY/changelog when released.
- **Hand-edit drift:** `MathTypes.py` must not be hand-edited to the new shape —
  the change must land in `postprocess_mathtypes.py` and be realized by
  `make codegen-all`, or the next regeneration silently reverts it.
- **Docstring/spec truth:** the ABC docstrings and `mathTypeTiers.md` name old
  paths and the old inheritance; if not updated in the same change, the spec lies
  about the tier contract.

## Out of Scope (surfaced, not folded in)

- `schemaCodegen.md:29` still names `generateUnitSphericalSmallCircle.sh` as the
  golden template — that script no longer exists (superseded by
  `generateMathTypes.sh`). Pre-existing staleness, independent of this change.
- `README.md:93-95` references nonexistent `foundationTypes.mathTypes.<PerClass>`
  modules — pre-existing staleness.
- The not-yet-written `*MathLike` math-contract modules referenced by docstrings —
  future work; their eventual home (likely `foundation_math`) is unaffected here.

## Implementation Steps

- [x] **1. Create the subpackage.** `src/foundation_abc/math/` with empty
  `__init__.py` and a `py.typed` marker (mirrors `mathTypes/`).
- [x] **2. Move `mathEnums.py`** verbatim to `foundation_abc/math/mathEnums.py`;
  update its docstring's location references if any.
- [x] **3. Move the four ABC modules** to `foundation_abc/math/`, and in each:
  - Remove `from foundationTypes.data_model_helper import DataModelHelper` and the
    `DataModelHelper` base: `class XxxxABC(ABC, DataModelHelper):` →
    `class XxxxABC(ABC):` (12 classes across the 4 files).
  - `precisionTimeABC.py`: `mathEnums` import → `foundation_abc.math.mathEnums`.
  - `waveformABCs.py`: sibling ABC imports → `foundation_abc.math.<module>`.
  - Update module docstrings that cite `foundationTypes.mathTypes.*` paths.
- [x] **4. Delete the old modules** from `src/foundationTypes/mathTypes/`
  (`spatialABCs.py`, `sphericalABCs.py`, `waveformABCs.py`, `precisionTimeABC.py`,
  `mathEnums.py`) — clean break, no shims.
- [x] **5. Update `schema/scripts/reuse/postprocess_mathtypes.py`:**
  - Reparent substitution (L139): emit two bases, ABC first —
    `f"class {type_name}({like}, DataModelHelper):"`.
  - ABC import injection (L142): prefix `foundationTypes.mathTypes.` →
    `foundation_abc.math.`.
  - Injected import block (L147-153): add
    `from foundationTypes.data_model_helper import DataModelHelper`; change the
    `mathEnums` import to `foundation_abc.math.mathEnums`.
  - Update the module docstring/comments (L51-54) describing the reparenting.
- [x] **6. Regenerate:** `make codegen-all`. Verify the `MathTypes.py` diff shows
  exactly: dual-base class declarations (ABC first), the `DataModelHelper` class
  import, and the new `foundation_abc.math.*` import paths — no other drift.
- [x] **7. Add a dependency-direction test** (e.g. `tests/test_package_layering.py`):
  assert no module under `foundation_abc/` imports `foundationTypes`,
  `foundation_math`, or `foundation_tools` (AST or import-source scan). This is the
  invariant the whole plan exists to establish; make it executable.
- [x] **8. Update `.claude/specs/mathTypeTiers.md`:** frontmatter `applies_to`
  (add `foundation_abc/math/`), tier diagram (L53-62), tier table "Lives in" /
  "Inherits" rows (L66-71 — `XxxxLike`: `ABC` only, lives in `foundation_abc/math/`;
  `XxxxType`: inherits `XxxxLike, DataModelHelper`), codegen description
  (L113-122), compliance checklist. Bump `last_updated`/`semver`.
- [x] **9. Touch `.claude/specs/schemaCodegen.md`** only where this change makes it
  false: note the math post-processor now injects `DataModelHelper` directly on
  generated classes. Bump tracking fields.
- [x] **10. Update `.claude/CLAUDE.md`** package descriptions: `foundation_abc` now
  holds the math ABC contracts + enums subpackage; `foundationTypes/mathTypes`
  description drops the ABC modules.
- [x] **11. Gate:** `make uv-fullCheck` (lint + strict mypy + tests) and
  `make testInEnv` (packaging path — new subpackage must ship).

## Resolution Notes (2026-07-08)

Executed as written — option 4 (clean break, ABC-first dual inheritance), no
redesign. No blockers encountered.

- **quicktype was available on PATH** (`quicktype version 23.2.6`), so step 6
  (`make codegen-all`) ran without the fallback-to-STOP path. `git mv` was used
  for the five moved files so file history follows them.
- **`MathTypes.py` diff after `make codegen-all`** matched the plan's prediction
  exactly: 6 new `foundation_abc.math.*` import lines (replacing the 5 old
  `foundationTypes.mathTypes.*` ones), one added `DataModelHelper` import, and 13
  `class XxxxType(...)` lines gaining `, DataModelHelper` with the ABC staying
  first — no other lines changed. No MRO or dataclass-field-default issues
  surfaced; invariant 2 (literal defaults clearing the inherited abstract
  `@property`) and invariant 4 (new — ABC-first base order) held on first
  regeneration.
- **`postprocess_mathtypes.py` import injection:** rather than folding
  `DataModelHelper` into the existing conditional `from foundationTypes.data_model_helper
  import (from_float, ..., DataModelHelper)` block (which only fires when
  `present_helpers` is non-empty), the script now emits a second, unconditional
  `from foundationTypes.data_model_helper import DataModelHelper` line. This is a
  minor deviation from the plan's literal "add the DataModelHelper import
  injection" phrasing but keeps the injection correct even in a hypothetical
  future schema that uses none of the `from_*`/`to_*` helpers.
- **Docstring path updates were scoped narrowly.** Per the plan's Out-of-Scope
  section, the `*MathLike` forward-references in `spatialABCs.py`,
  `sphericalABCs.py`, and `precisionTimeABC.py` docstrings (e.g.
  `foundationTypes.mathTypes.positionVectorMathLike`) were left untouched — those
  modules don't exist yet and their eventual home is explicitly undecided. Only
  `waveformABCs.py`'s docstring reference to the (real, moved) `spatialABCs`
  module was updated, to `foundation_abc.math.spatialABCs`.
- **`mathTypeTiers.md` gained a new Invariant 4** (ABC-must-be-first in the
  generated base list) that wasn't explicitly enumerated in the plan's checklist
  item 8 but follows directly from the plan's own "Proposed Approach" MRO rule —
  added so the spec states the constraint as a numbered invariant rather than
  only in prose. Compliance checklist also gained a 5th item pointing at the new
  `tests/test_package_layering.py`.
- **`schemaCodegen.md` edit** was a single explanatory addition to the
  `add_datamodelhelper.sh` bullet noting the Math family's post-processor is a
  separate, math-specific mechanism that now also injects `DataModelHelper`
  directly — nothing else in that file was factually contradicted by this change.
- **Side effects caught and reverted before finishing:** `make uv-fullCheck` /
  `make testInEnv` runs incidentally deleted the tracked `uv.lock` (restored via
  `git checkout -- uv.lock`) and an errant `cp` left a stray `MathTypes.py` copy
  at the repo root (removed); the `.cleanroom-venv` directory from `testInEnv`
  was also cleaned up. None of these are part of the plan's intended diff.
- **Gate results:** `make uv-fullCheck` — ruff clean, `mypy -p foundationTypes -p
  foundation_abc -p foundation_math -p foundation_tools` and `mypy tests` both
  "Success: no issues found", 312/312 tests passed. `make testInEnv` — clean-room
  venv install + 312/312 tests passed; confirmed via wheel inspection that
  `foundation_abc/math/{__init__.py,py.typed,mathEnums.py,precisionTimeABC.py,
  spatialABCs.py,sphericalABCs.py,waveformABCs.py}` all ship in the built wheel.
