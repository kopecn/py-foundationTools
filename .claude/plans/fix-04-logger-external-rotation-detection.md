---
plan: Fix04LoggerExternalRotationDetection
scope: project
status: pending
last_updated: 2026-08-23
semver: 0.0.1
author: Nicholas Bergantz
---

# Fix 04 — Logger External-Rotation Detection

## Goal

Make `_DateRollingFileHandler` reopen its configured path when external tooling
renames, replaces, or removes the active log file.

## Depends on

Fix 03 only in preferred landing order. There is no code dependency.

## Defect

`_needs_inode_rollover()` compares `os.fstat(self._stream.fileno()).st_ino` with the
inode recorded from that same open descriptor. Renaming or unlinking the path does not
change the open descriptor's inode, so the comparison remains equal and the handler
continues writing to the old or unlinked file.

## Files

Edit:

- `src/foundation_tools/standardized_logger.py`
- `HISTORY.md`

Create:

- `tests/test_standardized_logger.py`

## Design constraints

**Compare descriptor to path.** Determine the expected current path with
`_path_for_date(self._current_date)` and compare `os.stat(path).st_ino` to the open
stream's `os.fstat(...).st_ino`. A missing path means rollover is needed.

**Keep emit self-healing.** The next `emit()` after replacement/removal closes the old
descriptor, opens the canonical path, and writes the new record there.

**Portable tests.** Use `tmp_path`. If a platform forbids renaming an open file, isolate
only that OS-specific operation while still testing the path-stat decision through a
monkeypatch. Do not weaken production behavior to accommodate a test platform.

**No watcher dependency.** Detection remains emit-time and stdlib-only; do not add a
filesystem watcher or background thread.

## Steps (TDD)

1. Add a test that opens a handler, renames the active file, creates a replacement at
   the canonical path, and proves `_needs_inode_rollover()` returns true.
2. Emit a record and assert it lands in the replacement, not the rotated file.
3. Add the removal-without-replacement case and assert the next emit recreates the
   canonical path.
4. Preserve same-path/no-change and date-rollover tests.
5. Implement path-versus-descriptor comparison with missing-file handling.
6. Add an `[Unreleased]` `Fixed` bullet.
7. Run the focused logger tests, then `make uv-fullCheck`.

## Acceptance criteria

- [ ] Renaming and replacing the current log path is detected on the next emit.
- [ ] Removing the path is detected and the file is recreated.
- [ ] An unchanged active file does not reopen on every record.
- [ ] Existing UTC date and `rotation_days` behavior remains unchanged.
- [ ] Streams are closed during rollover and handler close.
- [ ] No runtime dependency or background watcher is introduced.
- [ ] `make uv-fullCheck` passes.

## Out of scope

- Size-based rotation, compression, or retention policies.
- Cross-process write locking.
- Renaming historical date files.
- Redesigning the structured log schema.

