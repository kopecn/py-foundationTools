"""Introspective discovery of the constants declared in this package.

The registry is *derived*, never hand-maintained: a table of constants written out
by hand would be a second source of truth that drifts the moment someone adds a
value. Walking the modules instead means the index cannot disagree with the code.

It backs the CI audit that every constant declares its uncertainty state
deliberately, and is the natural input to a future uncertainty-budget report.
"""

import importlib
import pkgutil
from collections.abc import Iterator
from types import ModuleType

from foundation_science.constants.constant import Constant

_PACKAGE = "foundation_science.constants"


def iter_module_constants(module: ModuleType) -> Iterator[tuple[str, Constant]]:
    """Yield ``(qualified_name, constant)`` for every ``Constant`` in ``module``.

    Covers both module-level constants and those held as attributes of a namespace
    class, since the package uses both forms. Names are qualified with the module
    path so a caller can tell ``DryAir.R`` from ``ISA.T_SL``.

    - module: An already-imported module to scan
    """
    for attr_name, attr in vars(module).items():
        if attr_name.startswith("_"):
            continue

        if isinstance(attr, Constant):
            yield f"{module.__name__}.{attr_name}", attr
            continue

        # A namespace class (DryAir, ISA, JetA1) holding constants as attributes.
        # Guard on __module__ so an imported class is not scanned twice.
        if isinstance(attr, type) and getattr(attr, "__module__", None) == module.__name__:
            for member_name, member in vars(attr).items():
                if isinstance(member, Constant):
                    yield f"{module.__name__}.{attr_name}.{member_name}", member


def iter_constants() -> Iterator[tuple[str, Constant]]:
    """Yield ``(qualified_name, constant)`` for every constant in the package.

    Imports every submodule under ``foundation_science.constants`` and scans each.
    """
    package = importlib.import_module(_PACKAGE)

    for module_info in pkgutil.walk_packages(package.__path__, prefix=f"{_PACKAGE}."):
        module = importlib.import_module(module_info.name)
        yield from iter_module_constants(module)
