---
plan: ActionPlan11MermaidNucleation
scope: project
status: outline
last_updated: 2026-08-23
semver: 0.0.1
author: Nicholas Bergantz
---

# 11 — Mermaid Nucleation (tier 3)

> **Outline.** Expand at gate 2. **This chunk is deliberately fenced and must not grow.**

## Goal

Establish where a mermaid diagram would attach, and nothing more. Explicitly a nucleation point, not a feature.

## Sketch

- A `mermaid` arm on `contentBlock.type` with payload `{source: string, renderer: "image"}`.
- Nothing else. No parser, no layout engine, no renderer, no CLI, no dependency.

## Fence

This chunk ships a schema arm and a documented seam. It does not ship a working mermaid diagram. If implementing it starts to look like it belongs here, that is the signal to scope it as its own plan set instead.

Note the tension with R7 ("block types must be renderable"): this arm is knowingly unrenderable at tier 3 and is the single sanctioned exception, because its purpose is to reserve the shape. It must be marked as such in the schema description so no author mistakes it for working.

## Out of scope

Everything beyond the schema arm.
