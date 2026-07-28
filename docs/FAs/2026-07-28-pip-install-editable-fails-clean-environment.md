---
title: pip editable install fails in clean Python.org macOS environment
date: 2026-07-28
status: open
severity: high
component: packaging / toolchain / python installation
commit: 519a363
tags: [failure, toolchain, python-packaging, editable-install]
---

# pip `-e install` fails in clean Python.org macOS environment — no fallback path

## Summary

Running `pip install -e .` in a locally-developed Python installation (Python.org macOS build) that was explicitly cleaned via the project's `make nuke` target produces irrecoverable failures: `setuptools.build_meta` is not importable, and pip has no mechanism to proceed without an external build backend. This revealed that the CPython packaging ecosystem provides **zero** self-contained build/install semantics — every tool in the chain (pip, setuptools, build) is a third-party program with no fallback to stdlib.

## Failure

Two failure modes confirmed:

### Mode 1 — Build isolation + network needed
```
python3 -m pip install .
# → Connecting to pypi.org/simple/setuptools/ ... nodename nor servname provided
# → "Could not find a version that satisfies the requirement setuptools>=61.0.0"
```
Build isolation (PEP 517) spins up a fresh environment and fetches setuptools from PyPI. Requires network access.

### Mode 2 — No build isolation + setuptools not installed
```
python3 -m pip install -v -e . --no-build-isolation
# → ERROR: Exception: ... BackendUnavailable: Cannot import 'setuptools.build_meta'
```
Without a virtualenv's bundled wheels, the Python.org macOS framework does not ship setuptools as an importable module. The `site-packages/` directory contains only metadata-only stubs (`.dist-info/METADATA` pointing at pip but nothing on disk).

## Environment

| Field | Value |
|---|---|
| OS | macOS 24.6.0 (Darwin) |
| Python | 3.13.5 from Python.org, `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3` |
| pip | 25.1.1 (from same framework) |
| Branch | `feat/switch-to-new-template` at `519a363` (.env dirty) |
| setuptools | **Not importable** — `ModuleNotFoundError: No module named 'setuptools'` |
| Network access | Offline (DNS resolution unavailable) |

## Root Cause

The Python.org macOS installer ships pip as a **metadata-only entry** without the actual distribution files on disk. There is no bundled wheel for setuptools, and the site-packages directory is effectively empty of importable packages. When pip encounters a local source tree that requires `[build-system]` support:

1. `pip install .` (no `-e`) → attempts build isolation → fetches setuptools from PyPI → fails without network
2. `pip install -e . --no-build-isolation` → checks if `setuptools.build_meta` is importable → import error → crash

There is **no third option pip offers** for this scenario. The tool requires setuptools as an explicit import-time dependency before it can look at the project's own metadata or parse `pyproject.toml`.

## Contributing Factors

- Python.org macOS installers deliberately do not ship bundled wheels with the framework distribution (Python 3.11+ changed away from including setuptools in ensurepip bootstrap)
- The `nuke` target removes all locally-installed packages, leaving behind only the bare Python binary and the empty stdlib — no bootstrapping tools remain
- The project's zero-dependency pyproject.toml is correct; the gap is at the **toolchain layer**, not the project config
- Offline/off-DNS mode eliminates pip's one escape hatch (network fetch during build isolation)

## Impact

- Cannot perform editable development installs (`pip install -e .`) on this Python installation without either network access or pre-planted wheels
- `nuke` was intended to reveal isolation gaps; it confirmed that the ambient Python environment has no internal recovery path for any kind of code installation (not just editable)
- All project tooling (ruff, mypy, pytest) becomes unavailable until the bootstrapping gap is closed

## Architecture Gap Identified

The packaging chain is a three-link dependency where **none** link is part of the CPython distribution:

| Step | Who provides it | Part of stdlib? |
|---|---|---|
| Parse `pyproject.toml` and resolve build spec | pip + setuptools / build / uv | No |
| Download/install dependencies | pip (requires network) / uv (caches differently) | No |
| Build the package from source | `setuptools.build_meta` (must be `import`able) | No |
| Install .whl into site-packages | pip (unzip + egg-link manipulation) | stdlib-adjacent — `venv + installer` |

Python's stdlib provides, for project-level code installation:

- A zip-import engine (`zipimport`)
- Import search path manipulation (`site.py` / `sys.path` at startup)

That is it. Everything else the packaging ecosystem claims to be "Python's packaging interface" was implemented by separate software projects over decades and never converged into a single standardized tool in the distribution itself.

## Remediation (Proposed)

- [ ] **Immediate** — for offline dev on this Python: point `python3` at homebrew's Python (`brew install python@3.13`) which ships with setuptools installed
- [ ] **Near-term** — add a `bootstrap-setuptools` documentation artifact or script that handles the "first install" case without network (download wheels manually, store in a known location)
- [ ] **Long-term** — document this as an explicit constraint: the project's dev requirement list includes a *bootable* Python installation with pip + setuptools at minimum; `nuke` does not account for re-bootstrapping

## Open Questions

- Does any PEP/spec cover "stdlib guarantees for bootstrapping pip" when ensurepip is used? (Likely none — ensurebootstrap only provides pip itself which then fetches pip's own deps from PyPI.)
- Is there a stdlib-only `python -m build` equivalent that could exist in principle?
