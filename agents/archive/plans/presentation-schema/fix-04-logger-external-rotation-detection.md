---
plan: Fix04LoggerExternalRotationDetection
scope: project
status: complete
last_updated: 2026-09-04
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

## Ask ↔ result

- **Objective:** detect external log rotation (renamed/replaced/removed path) instead of comparing a descriptor with itself.
- **Authorized by:** `/execute-plan please proceed` (user approved all of fix-01–07).
- **Delivered:** `_needs_inode_rollover()` now compares `os.fstat(open_stream)` `(st_dev, st_ino)` against a fresh `os.stat(configured_path)`; a missing path (or fstat failure) counts as rollover. Removed the now-dead `_current_inode` field (only read by the rewritten method). New `tests/test_standardized_logger.py`: no-change, path-replaced, path-removed via `tmp_path` — confirmed failing pre-fix.
- **Gate:** `make uv-fullCheck` — ruff/mypy clean, 502 passed.
- **Gap:** dead-field removal beyond the plan's literal wording, but directly entailed by the fix (no watchers/threads/retention/compression/locking added).
