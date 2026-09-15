---
human_ask: >
  a series of FA's was generated from the first use of the build presentation tool.
  please review:
  /Users/nbergantz/__Workspaces__/pythonWorkspaces/py-clerical-tools/.claude/fa_reports
  and create a series action plan on closing these gaps.
goal: >
  Add altText, an ordered font fallback stack with a substitution flag, and document
  core-property metadata to the schema.
last_updated: 2026-09-15
semver: 0.1.0
author: Nicholas Bergantz
status: completed
---

# F7 — Accessibility + metadata

Serves [Summary goal](./00-overview.md#summary-goal) · [Original ask](./00-original-ask.md).
Implements [presentationSchema.md](../../specs/presentationSchema.md) **R21** and **R22**.
Evidence:
`py-clerical-tools/.claude/fa_reports/FA-07-portability-accessibility-and-document-fidelity.md`.
Unblocks clerical chunk 15.

## Deliverable

- `image` and `mermaid` blocks (Deck schema) gain optional `altText`.
- the typography contract gains an ordered font fallback stack + a substitution-allowed
  flag (Deck metadata / defaults).
- `PresentationMetadata` gains optional document core-property fields: `subject`/
  `description`, `author`, `keywords`, `revision`/`version` (title reuses the existing
  deck title; timestamps are set downstream at write time, not schema state).
- Regenerated types + round-trip tests.

## Files

- `schema/schemas/Presentations/PresentationDeck-schema.json` — `altText` on blocks;
  fallback stack + substitution flag on the typography/defaults; core-property fields on
  `PresentationMetadata`.
- `src/foundationTypes/presentationTypes/Presentations.py` — regenerated.
- `tests/test_presentation_accessibility_metadata.py` — new.

## Design constraints (decided here)

- All additive/optional; no defaults; no `required` change (R13's round-trip guarantee
  for older decks must hold).
- These carry no schema-level behavior beyond identity — the schema does not write a
  PPTX; downstream maps them (clerical chunk 15).
- Fallback stack is an ordered array of family names; substitution flag is boolean.

## TDD steps

1. Failing tests: `test_alttext_roundtrip`, `test_font_fallback_stack_roundtrip`,
   `test_core_property_metadata_roundtrip`,
   `test_pre_existing_metadata_still_roundtrips` (a deck predating these fields).
2. Edit schema; `make codegen-all`.
3. `make uv-fullCheck` green.

## Acceptance criteria

- [x] altText, fallback stack + substitution flag, and core-property metadata validate
      and round-trip.
- [x] A deck without any of the new fields still validates and round-trips (regression).
- [x] `make codegen-all` clean; `make uv-fullCheck` green.
- [x] Class-name-diff guard: no pre-existing generated class was removed or renamed; no
      `title` hint was needed.

## Out of scope

- Setting alt text / mapping core props / consuming the fallback stack (clerical 15).
- Reading order (clerical 14, via F6 roles).

## Ask ↔ result

R22's exact text lists four core-property items: `subject`/`description`, `author`,
`keywords`, and `revision`/`version`. Three of those four names are dual names (an OOXML
core-property name paired with a slash to an existing schema field) for fields that
already existed in `PresentationMetadata` before this chunk: `description` (required,
pre-existing), `author` (required, pre-existing), and `version` (optional, pre-existing).
This mirrors the parenthetical the chunk itself gives for `title` ("title reuses the
existing deck title") — extended by the same logic to the other three dual-named items,
since `author` in particular cannot be re-declared as a new optional field without
colliding with (and contradicting) its existing required declaration. `keywords` carries
no slash in R22's text and has no pre-existing equivalent (`tags` is a separate,
differently-scoped free-form array field), so it is the only field genuinely added by
this chunk: `PresentationMetadata.keywords` (optional string, no default).

The upstream FA-07 evidence phrases this item as "tags/keywords" (implying reuse of the
existing `tags` array), but R22 — the accepted, authoritative contract for this chunk —
diverges from that phrasing and lists `keywords` standalone. R22's text governs per this
plan's instructions; `tags` was left untouched.

Result matches this reading: `altText` added to the shared `contentBlock` definition
(covers both `image` and `mermaid` arms, consistent with how `fit`/`focalPoint` are
already shared rather than type-conditional); `fontFallbackStack` (array of strings) and
`substitutionAllowed` (boolean) added to `PresentationMetadata.defaults`; `keywords`
(string) added to `PresentationMetadata`. All three additions are optional, default-less,
and require no `required` change — R13's round-trip guarantee holds, verified by
`test_pre_existing_metadata_still_roundtrips`.
