---
plan: RepositoryHardeningOverview
scope: project
status: needs-approval
last_updated: 2026-09-04
semver: 1.0.0
author: Nicholas Bergantz
---

# Repository review findings

Plans `fix-01`–`fix-04` and `fix-06`–`fix-08` are completed records. The obsolete
`fix-05` record was removed after its path-root work was superseded and completed.

The 2026-09-04 trace-path review added these independent candidates:

- `fix-09`: make transaction-ID registration and frame preparation atomic;
- `fix-10`: stop generated math types from weakening required ABC fields to `None`;
- `fix-11`: prevent incomplete presentation migrations from claiming target versions;
- `fix-12`: define and enforce socket client/router/server lifecycle ownership;
- `fix-13`: terminate and reap asynchronous CLI children when callers cancel;
- `fix-14`: replace the sync/async string-command shell mismatch with an explicit contract;
- `fix-15`: make typed transaction results report decode failure truthfully;
- `fix-16`: separate model serialization from files, environment, wire codecs, and invocation;
- `fix-17`: align presentation schema defaults/constraints with Python construction;
- `fix-18`: replace SSH/rsync parameter combinations with valid endpoint/transfer values;
- `fix-19`: restore `logging.Logger` compatibility and make structured output safe.

These candidates are not an implementation stack, although `fix-15` and `fix-16` need
a coordinated API decision. Their presence records findings only; it does not authorize
implementation, compatibility shims, adjacent cleanup, or preservation of accidental
behavior as legacy support. Approve and scope each candidate explicitly before execution.
