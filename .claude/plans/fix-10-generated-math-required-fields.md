---
plan: Fix10GeneratedMathRequiredFields
scope: project
status: complete
last_updated: 2026-09-07
semver: 2.0.0
author: Nicholas Bergantz
---

# Fix candidate 10 — restore schema-faithful Math carriers

## Corrected diagnosis

The generated `None` annotations were a symptom, not the root defect. Raw quicktype
output already represented every schema-required Math field as a non-optional,
default-free dataclass field.

The defect was introduced by postprocessing: generated storage classes were made
nominal subclasses of interfaces whose fields were abstract read-only properties.
Python property descriptors conflict with dataclass field assignment, so a later
workaround added class-level defaults merely to make the generated subclasses
instantiable. Nested objects had no plausible literal default, producing the
schema-invalid `XxxxType | None = None` annotations and type suppressions. Required
scalars and collections were also incorrectly made optional at construction, even
though the original finding called out only nested objects.

The prior conclusion that literal defaults were a foundational invariant was
therefore backwards: it documented the workaround as architecture.

## Resolution

- Generated `XxxxType` carriers inherit `DataModelHelper` directly and retain all
  common IO extensions.
- Math shape interfaces use `typing.Protocol`; carriers satisfy them structurally
  without inheriting their property descriptors.
- Protocols declare serialization signatures but no longer duplicate schema-owned
  wire mappings.
- The Math postprocessor no longer injects interface parents, `Sequence` field
  rewrites, fabricated defaults, or assignment suppressions.
- Regeneration restores quicktype's required constructor fields unchanged.
- Contract tests cover direct construction, missing `from_dict` fields, legitimate
  schema optionals, structural protocol compatibility, and generated source shape.

This supersedes the blocked 2026-09-05 analysis. Obsolete archived plans 21–23,
which preserved the nominal-inheritance/MRO workaround and its tests, were removed.

## Verification

- Focused Black and Flake8 checks pass for the Math implementation and tests.
- Strict mypy passes for all 62 source files and all 36 test files; the test
  module includes a compile-time proof for all 13 carrier/protocol pairs.
- The full suite passes: 589 tests and 75 subtests.
- Two consecutive Math generations produced the same SHA-256 for `MathTypes.py`.
- The repository-wide `make uv-fullCheck` currently stops in Flake8 on unrelated
  formatter-migration findings outside this change; Math-scoped Flake8 is clean.
