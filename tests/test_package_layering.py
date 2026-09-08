"""Dependency-direction tests for the leaf packages.

Plan 21 broke the ``XxxxABC(ABC, DataModelHelper)`` inheritance so the math ABCs
(now under ``foundation_abc/math/``) could move out of ``foundationTypes`` without
creating a ``foundationTypes -> foundation_abc -> foundationTypes`` cycle. The
invariant that makes that safe — ``foundation_abc`` stays a zero-dependency leaf,
importing nothing from the other top-level packages — is exactly the thing this
test enforces, via a static AST scan (no imports executed) of every module under
``src/foundation_abc/``.

``foundation_science`` is held to the same rule. Constants have no business
importing anything, and keeping the scan in place now is what will stop the
deferred ``foundation_science.metrology`` layer from inverting into them later.
"""

import ast
from pathlib import Path

ALL_TOP_LEVEL_PACKAGES = {
    "foundationTypes",
    "foundation_math",
    "foundation_tools",
    "foundation_abc",
    "foundation_science",
}

SRC_ROOT = Path(__file__).resolve().parent.parent / "src"
FOUNDATION_ABC_ROOT = SRC_ROOT / "foundation_abc"
FOUNDATION_SCIENCE_ROOT = SRC_ROOT / "foundation_science"


def _imported_top_level_names(module_path: Path) -> set[str]:
    """Return the top-level package name of every module imported by ``module_path``."""
    tree = ast.parse(module_path.read_text(encoding="utf-8"), filename=str(module_path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            # node.level > 0 is a relative import (`from . import x`); it can only
            # resolve within foundation_abc itself, so it is never forbidden.
            if node.level == 0 and node.module:
                names.add(node.module.split(".")[0])
    return names


def _sibling_import_violations(root: Path) -> dict[str, set[str]]:
    """Map each module under ``root`` to the sibling top-level packages it imports."""
    forbidden = ALL_TOP_LEVEL_PACKAGES - {root.name}
    violations: dict[str, set[str]] = {}
    for module_path in root.rglob("*.py"):
        imported = _imported_top_level_names(module_path) & forbidden
        if imported:
            violations[str(module_path.relative_to(SRC_ROOT))] = imported
    return violations


def test_foundation_abc_does_not_import_sibling_packages() -> None:
    violations = _sibling_import_violations(FOUNDATION_ABC_ROOT)

    assert not violations, (
        "foundation_abc must stay a zero-dependency leaf (no imports from the other "
        f"top-level packages), but found: {violations}"
    )


def test_foundation_science_does_not_import_sibling_packages() -> None:
    """``foundation_science`` is a leaf for the same reason ``foundation_abc`` is.

    It also pre-enforces the one-way dependency for the deferred
    ``foundation_science.metrology`` layer: uncertainty propagation may consume
    constants, but constants must never grow a dependency on a math engine.
    """
    violations = _sibling_import_violations(FOUNDATION_SCIENCE_ROOT)

    assert not violations, (
        "foundation_science must stay a zero-dependency leaf (no imports from the "
        f"other top-level packages), but found: {violations}"
    )


def test_foundation_science_is_scanned() -> None:
    """Guard against the scan silently finding zero files."""
    scanned = list(FOUNDATION_SCIENCE_ROOT.rglob("*.py"))
    assert (
        len(scanned) >= 6
    ), f"expected at least 6 modules under foundation_science/, found {scanned}"


def test_foundation_abc_math_subpackage_is_scanned() -> None:
    """Guard against the scan silently finding zero files (e.g. a bad glob root)."""
    scanned = list(FOUNDATION_ABC_ROOT.rglob("*.py"))
    assert len(scanned) >= 6, f"expected at least 6 modules under foundation_abc/, found {scanned}"
