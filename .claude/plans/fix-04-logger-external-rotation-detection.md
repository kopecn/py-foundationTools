---
plan: Fix04LoggerExternalRotationDetection
scope: project
status: needs-approval
last_updated: 2026-08-28
semver: 1.0.0
author: Nicholas Bergantz
---

# Fix candidate 04 — external log rotation

Evidence: `_needs_inode_rollover()` compares the current open descriptor with the inode
originally recorded from that same descriptor, so a renamed or replaced path is not
detected.

Minimum fix: compare `fstat(open_stream)` with `stat(configured_path)` and treat a
missing path as rollover. Test replacement, removal, and no-change using `tmp_path`.

Do not add watchers, threads, retention, compression, or cross-process locking.
