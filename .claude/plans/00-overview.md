---
plan: PresentationsOverview
scope: project
status: active
last_updated: 2026-08-28
semver: 1.1.0
author: Nicholas Bergantz
---

# Presentation infrastructure roadmap

## Source request

Recovered from Claude session `d87190ca-1689-4218-a704-7d14d61de926` and reconfirmed
2026-08-28.

The goal is schema-driven corporate presentations: centralize theme/layout decisions,
nucleate an approximately 80%-complete deck so an agent focuses on narrative and
content, and allow old presentations to adopt later corporate standards—“CSS for
pptx.”

This repository owns schemas, strict generated types, ABCs, and dependency-free common
functions. PowerPoint rendering belongs in `py-clerical-tools`; plans here never assign
work to that repository.

## Three levels and gates

| level | local plans | functional gate |
|---|---|---|
| 1 — MVP | 01–05 | Current schemas generate strict types and support the basic renderer contract. Revalidate after the active schema cleanup before opening level 2. |
| 2 — narrative deck | 06–08 | Typed narrative content and charts round-trip through generated models without adding runtime dependencies. |
| 3 — standards evolution | 09–11 | Versions and pure migration support theme/layout updating; Mermaid has a bounded schema attachment point. |

## Planning rules

- Keep each plan short and repository-local.
- Expand only the next plan after the preceding level's revision gate.
- Deliver the smallest usable form of each feature and grow from actual usage.
- Do not add runtime dependencies or PowerPoint rendering here.
- Do not restore files removed by `c78008a` merely because the old plan mentioned them.
- Specs record agreed contracts; they do not override this source request.
