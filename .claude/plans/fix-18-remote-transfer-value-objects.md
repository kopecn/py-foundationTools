---
plan: Fix18RemoteTransferValueObjects
scope: project
status: needs-approval
last_updated: 2026-09-04
semver: 1.0.0
author: Nicholas Bergantz
---

# Fix candidate 18 — valid SSH/rsync transfer configuration

Evidence: rsync construction accepts ten contextual parameters and repeats most of them
across four transaction methods. Combinations such as `ssh_user` without a host are silently
ignored, `remote_side` is meaningful only in remote mode, and SSH transport formatting is
duplicated "by hand." The exported `WINDOWS_SAFE_RSYNC_OPTIONS` constant is a mutable list.

Minimum fix: model local and remote endpoints plus transfer direction/options as immutable
value objects whose constructors reject invalid combinations. Share SSH transport formatting,
reduce forwarding duplication, quote/encode identity paths correctly for rsync `-e`, and
publish immutable option presets.

Do not change rsync defaults, invent remote hosts from ambient configuration, or retain every
invalid keyword combination through compatibility branches unless separately approved.
