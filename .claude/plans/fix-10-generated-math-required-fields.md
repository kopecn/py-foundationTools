---
plan: Fix10GeneratedMathRequiredFields
scope: project
status: needs-approval
last_updated: 2026-09-05
semver: 1.1.0
author: Nicholas Bergantz
---

# Fix candidate 10 — generated math required-field contracts

Evidence: Math schemas require nested fields such as `position`, `orientation`, `t0`,
and `dt`, and their Tier-2 ABC accessors are non-optional. The generated dataclasses make
those fields optional with `None` defaults. `postprocess_mathtypes.py` acknowledges the
incompatible override and emits `# type: ignore[assignment]`, allowing direct constructors
to create schema-invalid objects that violate their base-class contract.

Minimum fix: change the schema/codegen/postprocessing strategy so required nested fields
remain required and non-optional in generated constructors. Remove the corresponding type
suppression and add contract tests for direct construction, `from_dict`, and regeneration.

Do not hand-edit `MathTypes.py`, weaken the ABC return types, make required schema fields
optional, or retain a `None` compatibility constructor unless separately approved.

## Session note — 2026-09-05 (BLOCKED; not executed)

An execution attempt this session (user approved fix-10 on 2026-09-05) stopped without
changing any code. The "Minimum fix" directly contradicts
[`mathTypeTiers.md`](../specs/mathTypeTiers.md) **Invariant 2**, which lives under a
heading explicitly marked *"Invariants (empirically forced — do not 'fix')"* and mandates
the opposite: nested single-object carrier fields **must** be `... | None = None` with
`# type: ignore[assignment]`, `field(default_factory=...)` is forbidden.

Verified empirically: a generated `@dataclass XxxxType(XxxxLike, DataModelHelper)` inherits
an abstract `@property` per field. To be instantiable each field needs a *literal,
hashable, class-level default* — to clear `__abstractmethods__` and to shadow the
setter-less property. Scalars (`0.0`/`0`/enum) and lists (`Sequence[...] = ()`) have such
literals; nested carriers have no literal except `None`. Options tried, all fail:
required-no-default → `TypeError: Can't instantiate abstract class`; `default_factory` →
same; real instance default → `ValueError: mutable default not allowed`.

Every route to the chunk's goal needs a separately-forbidden action (weaken the ABC
accessors, amend a do-not-fix invariant, or a `default_factory`/virtual-subclass strategy
that breaks other pinned invariants and tests). `quicktype` is installed — tooling is not
the blocker.

**Decision required from the human — pick one before re-scoping:**

1. Amend `mathTypeTiers.md` Invariant 2 to authorize a new Tier-2 strategy (e.g. concrete
   `@property` overrides on `XxxxType`, or a validating `__post_init__`), then re-scope
   fix-10 against the amended spec.
2. Narrow fix-10: keep the `| None` codegen tax but add a `from_dict` / `__post_init__`
   guard that rejects missing required nested fields at runtime — closes the
   schema-invalid-object hole without changing the constructor signature or removing the
   `# type: ignore`.
3. Close fix-10 as won't-fix: accept `# type: ignore[assignment]` + `| None` as
   load-bearing per Invariant 2.

Status stays `needs-approval` (blocked).
