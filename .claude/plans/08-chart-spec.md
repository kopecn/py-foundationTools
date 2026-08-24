---
plan: ActionPlan08ChartSpec
scope: project
status: outline
last_updated: 2026-08-23
semver: 0.0.1
author: Nicholas Bergantz
---

# 08 — Chart Spec (tier 2)

> **Outline.** Expand at gate 1.

## Goal

A typed chart payload, replacing the untyped `data: {}` that chunk 01 deleted.

## Sketch

- `chartType`: enum, small — `bar`, `column`, `line`, `pie`, `scatter`. Grow on demand.
- `categories`: array of strings.
- `series`: array of `{name, values[]}`.
- `renderer`: enum `native | image`, default `native`. The adopted idea from the external review: native charts stay editable in PowerPoint but inflate the file; embedded images render identically everywhere but are static. It is a per-chart decision, so the schema should carry it per chart.
- Series colors come from `theme.chartColors[]` by index — never literal, so charts re-theme with everything else.

## Open at gate

Whether `image` renderers belong in this repository's schema at all, given it cannot render. The field is a hint to the downstream renderer, which is legitimate, but it is the first place the schema knows about rendering strategy.

## Out of scope

Axis configuration, legends, gridlines, dual axes, trendlines, data labels. Add on evidence.
