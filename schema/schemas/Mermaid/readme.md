# Mermaid Schema — Root Elements

## Scope

This folder holds the JSON Schemas that model a Mermaid diagram document. A document is made of four root elements: a frontmatter, a directive, a diagram type declaration, and a diagram body. These four are the schema trunk; each diagram type adds its own body (a branch) on top of the trunk.

This file is the index for the trunk. It has one section per root element, in document order. Each section states what the element is, its source of truth, and whether a schema models it yet.

Source of truth:

- The document structure and the frontmatter rules come from the Mermaid syntax reference page (`intro/syntax-reference`).
- The frontmatter `config` block is defined by Mermaid's published config schema, which we vendor. We do not copy its keys into this file, because a copy drifts from the source. See section 1.3.

## Document structure

A Mermaid document has this order from top to bottom:

1. Frontmatter — optional YAML metadata block.
2. Directive — optional `%%{ }%%` reconfiguration block.
3. Diagram type declaration — the required first token of the definition.
4. Diagram body — the type-specific content.

Two parser rules from the source constrain this order:

- Every diagram definition starts with the diagram type declaration. The only element permitted before it is the frontmatter.
- A misspelled or unknown word breaks the diagram. A misspelled parameter fails without a message.

## Root element list

| # | Element | Required | Marker | Modeled by |
| --- | --- | --- | --- | --- |
| 1 | Frontmatter | No | `---` … `---` | not yet modeled (its `config` key is modeled by the parent `mermaid-schema.json`, which references the vendored config) |
| 2 | Directive | No | `%%{` … `}%%` | placeholder in `mermaidDirectives-schema.json` (referenced by the parent) |
| 3 | Diagram type declaration | Yes | first token (e.g. `erDiagram`, `flowchart LR`) | the type selector is the `diagramType` enum in `mermaid-schema.json`; the literal declaration token is not yet modeled |
| 4 | Diagram body | Yes | lines after the declaration | the `body` node in `mermaid-schema.json`; each type's body content is a separate file (one branch per diagram type) |

A comment (`%%`) is a lexical element, not a root. It lives inside the diagram body (section 4.1).

## 1. Frontmatter

The frontmatter is an optional YAML block at the start of the document. The source states these rules:

- A line with only `---` marks the start and the end of the block.
- The `---` characters must be the only characters on their line.
- The content is YAML. Indentation must be consistent. Keys are case-sensitive.
- A misspelled key is ignored without a message. A malformed value breaks the diagram.

The schema models only the YAML content between the fences. The `---` fences belong to the serializer, not to the data. The frontmatter has three keys: `title`, `displayMode`, and `config`. Every key is optional.

### 1.1 `title`

A string. The diagram title.

### 1.2 `displayMode`

A string. The source documents the value `compact` for the gantt diagram. The full value set is not fixed by the source page.

### 1.3 `config`

The `config` block is defined by the local schema `mermaidConfig-schema.json`, a copy of the official Mermaid config schema with one change: every `required` array is removed. The official schema describes the fully-resolved runtime config, where defaults fill every key, so its `required` lists the keys the runtime always has — not the keys an author writes. A partial frontmatter `config` would therefore fail against the unmodified schema. The local copy is the single source of truth; this file does not repeat its keys.

Official sources:

- Schema: https://mermaid.js.org/schemas/config.schema.json
- API docs: https://mermaid.js.org/config/schema-docs/config.html

#### Re-ingest procedure (run on each upstream bump)

1. Download the official schema verbatim to `vendor/mermaidConfig.upstream-schema.json`. Do not hand-edit the vendored copy; it is the provenance baseline for the diff on the next bump. Every `$ref` in it is internal, so this is one file, not a tree.
2. Produce the author-input copy `mermaidConfig-schema.json` by one deterministic transform of the vendored copy: remove the top-level `required` array and every `required` array inside `$defs`. Change nothing else — keep `properties`, `$defs`, enums, and defaults.
3. The upstream schema carries no version field, so pin by ingest date: record today's date as the pinned version in the table below.
4. `mermaid-schema.json` references the author-input copy for its `config` property.

#### Codegen caveats (do not resolve in Python)

A few nodes use the upstream `tsType` escape hatch and carry no JSON type. They degrade to `Any` or an open object under `quicktype`; this is expected, not an error to fix:

- `themeVariables` (`tsType: any`)
- `dompurifyConfig` (`tsType: import('dompurify').Config`)
- `FontCalculator` (a JS function type)
- `XYChartConfig.chartOrientation` (`tsType` string union)

#### Ingest record

The upstream schema carries no version field, so the pin is the ingest date.

| Pinned version (date) | Notes |
| --- | --- |
| 2026-10-11 | Pinned on first ingest. Upstream exposes no version string, so the date is the version. |

## 2. Directive

Status: placeholder modeled by `mermaidDirectives-schema.json` (a single generic `init` object), referenced by the parent `mermaid-schema.json`. To be refined later.

A directive is an optional `%%{ }%%` block that reconfigures the diagram just before the render. The source states two properties the schema must respect:

- Position is flexible. A directive can sit above or below the diagram definition, unlike the frontmatter, which must be first.
- The directive overlaps the frontmatter `config` in purpose, and Mermaid deprecates the directive in favor of the frontmatter. The source also warns that `{}` characters inside a `%%` comment confuse the renderer and break the diagram.

## 3. Diagram type declaration

Status: the type selector is modeled by the `diagramType` enum in `mermaid-schema.json` (populated with `flowchart`). The literal declaration token is not yet modeled.

The declaration is the required first token of the definition (for example `erDiagram`, `flowchart LR`, `gitGraph`). It tells the parser which diagram type to build, and it selects which body branch applies. The parent schema models this choice as the `diagramType` enum, which names the body that applies, not the literal token string.

Caveat for the declaration-keyword set: the declaration keywords are not the same strings as the config namespace names in section 1.3. The config uses camelCase names (`xyChart`, `c4`, `gitGraph`), while the declaration uses keywords such as `xychart-beta`, `C4Context`, and `stateDiagram-v2`. The declaration-keyword enum is its own authored source; it is informed by the config namespace list but not copied from it.

## 4. Diagram body

Status: modeled by the `body` node in `mermaid-schema.json`. One branch schema per diagram type, each generated in its own file.

The body is the type-specific content after the declaration — the nodes, edges, commits, and other structures that each diagram type defines. The parent schema holds a thin `body` object; each diagram type gets its own body schema, added one at a time and generated independently, so the parent does not grow with every type.

### 4.1 Comments

A comment starts with `%%` and the parser ignores the rest of that line. A comment is a lexical element inside the body, not a root element. The serializer emits comments; the body schema accounts for them.
