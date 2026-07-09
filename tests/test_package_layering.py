"""Dependency-direction test for ``foundation_abc``.

Plan 21 broke the ``XxxxABC(ABC, DataModelHelper)`` inheritance so the math ABCs
(now under ``foundation_abc/math/``) could move out of ``foundationTypes`` without
creating a ``foundationTypes -> foundation_abc -> foundationTypes`` cycle. The
invariant that makes that safe — ``foundation_abc`` stays a zero-dependency leaf,
importing nothing from the other three top-level packages — is exactly the thing
this test enforces, via a static AST scan (no imports executed) of every module
under ``src/foundation_abc/``.
"""

import ast
from pathlib import Path

FORBIDDEN_TOP_LEVEL_PACKAGES = {"foundationTypes", "foundation_math", "foundation_tools"}

SRC_ROOT = Path(__file__).resolve().parent.parent / "src"
FOUNDATION_ABC_ROOT = SRC_ROOT / "foundation_abc"


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


def test_foundation_abc_does_not_import_sibling_packages() -> None:
    violations: dict[str, set[str]] = {}
    for module_path in FOUNDATION_ABC_ROOT.rglob("*.py"):
        imported = _imported_top_level_names(module_path) & FORBIDDEN_TOP_LEVEL_PACKAGES
        if imported:
            violations[str(module_path.relative_to(SRC_ROOT))] = imported

    assert not violations, (
        "foundation_abc must stay a zero-dependency leaf (no imports from "
        f"foundationTypes, foundation_math, or foundation_tools), but found: {violations}"
    )


def test_foundation_abc_math_subpackage_is_scanned() -> None:
    """Guard against the scan silently finding zero files (e.g. a bad glob root)."""
    scanned = list(FOUNDATION_ABC_ROOT.rglob("*.py"))
    assert len(scanned) >= 6, f"expected at least 6 modules under foundation_abc/, found {scanned}"
