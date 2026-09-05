---
plan: Fix16DataModelHelperResponsibilities
scope: project
status: needs-approval
last_updated: 2026-09-04
semver: 1.0.0
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
