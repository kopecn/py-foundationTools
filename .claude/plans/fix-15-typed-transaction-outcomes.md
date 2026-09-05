---
plan: Fix15TypedTransactionOutcomes
scope: project
status: needs-approval
last_updated: 2026-09-04
semver: 1.0.0
author: Nicholas Bergantz
---

# Fix candidate 15 — truthful typed transaction outcomes

Evidence: CLI and socket typed transactions can return `success=True`, `model=None`, and
a parsing error. RetryPolicy consequently treats an unusable typed response as terminal
success. Mutable result dataclasses also permit contradictory states unrelated to any real
execution path.

Minimum fix: define separate execution and decoding outcomes, preferably with immutable,
discriminated result types that make invalid combinations unrepresentable. Align CLI,
socket, SSH/rsync forwarding, retry termination, documentation, and tests with that model.

This is an API-design task. Do not merely flip the existing `success` boolean, erase raw
transport output, retry permanent decode failures indiscriminately, or retain contradictory
states as legacy support without explicit approval.
