"""
Tests for the shared socket-transaction lifecycle primitives (fix-12):
``LifecycleState`` and the construction-time numeric validators.
"""

import pytest

from foundation_tools.socket_transaction._lifecycle import (
    LifecycleState,
    require_min,
    require_positive,
)


class TestLifecycleState:
    def test_has_idle_and_active(self) -> None:
        assert {state.name for state in LifecycleState} == {"IDLE", "ACTIVE"}


class TestRequirePositive:
    @pytest.mark.parametrize("value", [0, 0.0, -1, -0.5])
    def test_rejects_non_positive(self, value: float) -> None:
        with pytest.raises(ValueError, match="read_size"):
            require_positive("read_size", value)

    @pytest.mark.parametrize("value", [1, 0.001, 4096])
    def test_accepts_positive(self, value: float) -> None:
        require_positive("read_size", value)  # no raise


class TestRequireMin:
    @pytest.mark.parametrize("value", [0, -1])
    def test_rejects_below_minimum(self, value: int) -> None:
        with pytest.raises(ValueError, match="max_concurrent"):
            require_min("max_concurrent", value, 1)

    @pytest.mark.parametrize("value", [1, 2, 100])
    def test_accepts_at_or_above_minimum(self, value: int) -> None:
        require_min("max_concurrent", value, 1)  # no raise
