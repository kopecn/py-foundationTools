---
title: pip editable install fails in clean Python.org macOS environment
date: 2026-07-28
last_updated: 2026-08-10
status: closed
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

Two compounding findings from plan 24's investigation (`.claude/action-plan/24-pip-half-bootstrap-recoverability.md`, E1–E2):

**E1 — `ensurepip` seeds pip only.** `ensurepip`'s bundled-wheel directory
(`.../ensurepip/_bundled/`) contains exactly one wheel: pip itself. Every
`python3 -m venv` — and, by extension, a bare Python.org macOS framework
interpreter — therefore starts with **no build backend**. Any PEP-517 build in
that environment must reach PyPI for `setuptools`, which is what makes a clean
install network-bound.

**E2 — `make nuke` became self-destructive at Python >= 3.12.** In
`pip/_internal/commands/freeze.py:12-20`:

```python
def _should_suppress_build_backends() -> bool:
    return sys.version_info < (3, 12)          # freeze.py:12-13

def _dev_pkgs() -> AbstractSet[str]:
    pkgs = {"pip"}
    if _should_suppress_build_backends():
        pkgs |= {"setuptools", "distribute", "wheel"}   # freeze.py:19-20

    return pkgs
```

Below Python 3.12, `pip freeze` hid `setuptools`/`wheel` from its output. At
>= 3.12 it lists them. The (former) `nuke` target piped `pip freeze
--exclude-editable` straight into `pip uninstall`, so on 3.12+ `nuke` now
uninstalled the build backend it used to implicitly preserve — turning a
"clean" reset into an unrecoverable one. `pip` itself was never at risk (always
in `_dev_pkgs()`); `setuptools`/`wheel` were the casualty. This — not the
Python.org installer's packaging choices — is the mechanism that produced the
`BackendUnavailable` crash: E1 explains why a bare interpreter starts with no
build backend, and E2 explains why `nuke` actively stripped it rather than
leaving it alone.

## Contributing Factors

- Python.org macOS installers deliberately do not ship bundled wheels with the framework distribution (Python 3.11+ changed away from including setuptools in ensurepip bootstrap)
- The `nuke` target removes all locally-installed packages, leaving behind only the bare Python binary and the empty stdlib — no bootstrapping tools remain
- The project's zero-dependency pyproject.toml is correct; the gap is at the **toolchain layer**, not the project config
- Offline/off-DNS mode eliminates pip's one escape hatch (network fetch during build isolation)

## Impact

- Cannot perform editable development installs (`pip install -e .`) on this Python installation without either network access or pre-planted wheels
- `nuke` was intended to reveal isolation gaps; it confirmed that the ambient Python environment has no internal recovery path for any kind of code installation (not just editable)
- All project tooling **on the pip/ambient-interpreter path** becomes unavailable until the bootstrapping gap is closed — see blast radius below for the corrected scope

### Blast radius (E3)

The original "all project tooling becomes unavailable" claim above is
**overstated**. Verified offline against a scratch venv, the uv half is
unaffected by this failure:

```
$ VIRTUAL_ENV=<scratch> uv pip install --offline -e .
Resolved 1 package in 9ms
   Building pyfoundationtools @ file:///…/py-foundationTools
      Built pyfoundationtools @ file:///…/py-foundationTools
Installed 1 package in 1ms
```

`uv cache dir` carries its own `setuptools` wheel independent of the ambient
interpreter, and this repo's CI (`.github/workflows/ci.yml`, formerly
`ci-cd.yml`) invokes only `uv-bootstrap-pythons` / `uv-bootstrap` /
`uv-fullCheck` / `uv-test-all`. **CI was never at risk.** The blast radius of
this failure is scoped to the pip/ambient-interpreter fallback path
(`installDev`, `e`, `refresh`, `testInEnv`) — `make uv-fullCheck` kept working
throughout.

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

## Remediation

- [x] **Immediate** — run `make pip-bootstrap`: it runs `python3 -m ensurepip
      --upgrade` then `pip install --upgrade setuptools wheel` against the
      ambient interpreter, restoring the build backend `nuke` (pre-fix) or a
      bare Python.org install never had. Requires network (build isolation must
      reach PyPI per E1); if the interpreter is externally-managed
      (Homebrew/Debian) and refuses ambient installs, `pip-bootstrap` names
      `make uv-bootstrap` as the offline-capable alternative instead of routing
      around the interpreter via a Homebrew reinstall.
- [x] **Near-term** — `nuke` itself now excludes `setuptools`/`wheel` from the
      `pip freeze | pip uninstall` pipeline (see `Makefile`, `nuke` target), so
      the failure mode E2 describes can no longer be triggered by `nuke` going
      forward; `pip-bootstrap` remains the documented inverse for interpreters
      that arrive pre-stripped (bare Python.org installs, or pre-fix history).
- [x] **Long-term** — documented as an explicit constraint via `check-pip`
      (wired only into the `testInEnv` clean-room target, per plan 24's D1/D2):
      it asserts `pip --version` succeeds and `setuptools.build_meta` imports
      before the clean-room proceeds, failing fast with a pointer to
      `make pip-bootstrap` / `make uv-sync` instead of a raw
      `BackendUnavailable` traceback. `installDev`/`e`/`refresh`/`build` remain
      intentionally unguarded (D1) — see `.claude/action-plan/24-pip-half-bootstrap-recoverability.md`.

## Open Questions

- Does any PEP/spec cover "stdlib guarantees for bootstrapping pip" when ensurepip is used? (Likely none — ensurebootstrap only provides pip itself which then fetches pip's own deps from PyPI.)
- Is there a stdlib-only `python -m build` equivalent that could exist in principle?
