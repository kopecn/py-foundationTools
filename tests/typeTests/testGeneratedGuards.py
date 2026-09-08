"""Contract test for fix-08: generated `from_dict` dict-guards raise `TypeError`.

quicktype emits every generated `from_dict` with a bare `assert isinstance(obj, dict)`
guard, which raises `AssertionError` on non-dict input and vanishes entirely under
`python -O`. `normalize_generated.sh` rewrites that guard into an explicit
`if not isinstance(obj, dict): raise TypeError(...)` statement matching
`data_model_helper.py`'s own `from_dict` converter. This test asserts the rewrite
landed everywhere and behaves correctly on a representative model from each
generated module.
"""

import re
import unittest
from pathlib import Path
from typing import Any

from foundationTypes.commonTypes.disk_usage.DiskUsage import DiskUsage
from foundationTypes.commonTypes.GeoCoordinate import GeoCoordinate
from foundationTypes.commonTypes.ModelContextProtocol import Basemetadata
from foundationTypes.cvTypes.ChArUcoConfig import ChArUcoBoard
from foundationTypes.mathTypes.MathTypes import QuaternionType
from foundationTypes.presentationTypes.Presentations import PresentationColor
from foundationTypes.standardizedLoggerConfig.StandardizedLoggerConfig import (
    StandardizedLoggerConfig,
)

SRC_ROOT = Path(__file__).resolve().parents[2] / "src" / "foundationTypes"

BARE_ASSERT_PATTERN = re.compile(r"assert isinstance\(obj, dict\)")

REPRESENTATIVE_MODELS: tuple[type[Any], ...] = (
    GeoCoordinate,
    DiskUsage,
    ChArUcoBoard,
    QuaternionType,
    PresentationColor,
    StandardizedLoggerConfig,
    Basemetadata,
)


class TestGeneratedGuardsUseTypeError(unittest.TestCase):
    """No generated `from_dict` guard should still be a bare `assert`."""

    def test_no_bare_assert_isinstance_dict_guard_remains(self) -> None:
        offenders = []
        for path in SRC_ROOT.rglob("*.py"):
            content = path.read_text(encoding="utf-8")
            if BARE_ASSERT_PATTERN.search(content):
                offenders.append(str(path))
        self.assertEqual(
            offenders,
            [],
            f"bare 'assert isinstance(obj, dict)' guard still present in: {offenders}",
        )

    def test_non_dict_input_raises_type_error_on_every_module(self) -> None:
        bad_inputs: tuple[Any, ...] = (None, [], "x")
        for model in REPRESENTATIVE_MODELS:
            for bad_input in bad_inputs:
                with self.subTest(model=model.__name__, bad_input=bad_input):
                    with self.assertRaises(TypeError):
                        model.from_dict(bad_input)


if __name__ == "__main__":
    unittest.main()
