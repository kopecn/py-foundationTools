---
plan: RepositoryHardeningOverview
scope: project
status: needs-approval
last_updated: 2026-08-28
semver: 1.0.0
author: Nicholas Bergantz
---

# Repository review findings

Plans `fix-01`–`fix-07` are concrete findings from a repository review, but they were
bundled into the presentation commit without being requested as presentation work.
They are independent candidates, not a stack, and none blocks another.

Each candidate may be approved separately:

- `fix-01`: invalid JSON in one schema;
- `fix-02`: framing-codec constructor permits non-progressing configuration;
- `fix-03`: router can orphan requests after frame-processing failure;
- `fix-04`: log rotation compares an open descriptor with itself;
- `fix-05`: glob patterns can lexically escape their root;
- `fix-06`: bounded uncertainty accepts non-finite values;
- `fix-07`: public documentation contains stale commands/imports.

`fix-08` is already complete. Do not infer approval for the other findings from its
completion or from their presence here.
