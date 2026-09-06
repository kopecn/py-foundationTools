---
plan: Fix16DataModelHelperResponsibilities
scope: project
status: needs-approval
last_updated: 2026-09-05
semver: 1.1.0
author: Nicholas Bergantz
---

# Fix candidate 16 — DataModelHelper responsibility separation

Evidence: `DataModelHelper` combines dict/JSON conversion, file and directory I/O,
environment-variable resolution, byte conversion, wire codecs, logging, and a transport-
specific `wire_invoke` union. DiskUsage activates wire behavior by import-time mutation of
generated class variables, making capability depend on import order and global state.

Minimum fix: design narrow contracts for model serialization, JSON persistence,
environment loading, `WireCodec[T]`, and transport invocation. Move transport commands and
codec registration out of model classes, eliminate import-side-effect mutation, and make
each consumer depend only on the protocol it uses.

Coordinate the typed-outcome boundary with `fix-15`, but do not turn approval of either
plan into approval of both. Preserve the zero-runtime-dependency rule and change generated
models only through the codegen pipeline.

## Session note — 2026-09-05 (not executed; own execution plan)

Status held at `needs-approval`. No implementation this session; this becomes its own
scoped execution plan.

Framing correction (user, 2026-09-05) — this is not a directive to dismantle the
abstraction:

- `DataModelHelper` is intentionally the **central model/representation boundary** — a
  hub, not a serialization chain. It gives a model a consistent, strongly typed path
  between its canonical representation and the representations its consumers need.
- A model may legitimately participate in multiple model-centered paths, all sharing the
  canonical `from_dict` / `to_dict`: dict/JSON ↔ model; bytes ↔ model; protocol wire
  representation ↔ model; model → structured persistence; model → communication.
- The responsibility boundary is crossed only when the model starts describing **how an
  external system acquires or invokes it** rather than how the model represents itself.
  `wire_invoke` is the clear example: `["df", "-h"]` is not a representation of
  `DiskUsage`; it is an external transaction used to obtain one. Move it out.
- Codec registration must not depend on **import-time mutation of generated model
  classes**. Available representation behavior is determined by the declared/generated
  contract, not by which configuration module executed first.
- Refactor so `DataModelHelper` stays the central boundary while transaction invocation,
  transport selection, and registration are owned by the layers that perform them.
- Introduce narrow protocols where they clarify what a consumer actually requires; the
  goal is **not** to replace the model-centered I/O abstraction with a chain of unrelated
  serializers.
- Preserve the zero-runtime-dependency rule; modify generated models only through the
  code-generation pipeline.

Coordinate the outcome boundary with `fix-15`; approval of one is not approval of both.
