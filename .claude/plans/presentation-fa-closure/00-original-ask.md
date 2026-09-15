---
last_updated: 2026-09-14
semver: 0.0.1
author: Nicholas Bergantz
---

# Original ask

Preserved verbatim as the initiating human request. The request was made in the
downstream `py-clerical-tools` repo; this series is the upstream (schema) half.

> a series of FA's was generated from the first use of the build presentation tool.  please review: /Users/nbergantz/__Workspaces__/pythonWorkspaces/py-clerical-tools/.claude/fa_reports and create a series action plan on closing these gaps.

## Why this series exists (scope split, decided at scoping 2026-09-14)

The 2026-09-14 presentation visual-quality audit lives in
`py-clerical-tools/.claude/fa_reports/`. About half of each finding's corrective action
needs a schema/model change here, because this repo owns the Presentations schema, the
generated types, and stdlib resolution — the downstream renderer only consumes them.

The human directed a two-series split: gaps closed by rendering go to
`py-clerical-tools/.claude/plans/fa-closure/`; gaps needing schema/model changes are
written here. These chunks add the typed fields the renderer consumes, accepted at the
FA-closure gate as [presentationSchema.md](../../specs/presentationSchema.md) R15–R22.

This repository still renders nothing. Every chunk here is additive schema + codegen +
stdlib resolution, so existing decks keep validating and round-tripping. The FA reports
are the evidence, not the authorization.
