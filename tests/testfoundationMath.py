"""
Unit tests for foundationMath module.
"""
import pytest
from src.foundationMath.math import clamp


class TestClamp:
    """Test cases for the clamp function."""

    def test_clamp_within_bounds(self):
        """Test that values within bounds are unchanged."""
        assert clamp(5, 0, 10) == 5
        assert clamp(0, 0, 10) == 0
        assert clamp(10, 0, 10) == 10

    def test_clamp_below_lower_bound(self):
        """Test that values below lower bound are clamped to lower bound."""
        assert clamp(-5, 0, 10) == 0
        assert clamp(-1, 0, 10) == 0

    def test_clamp_above_upper_bound(self):
        """Test that values above upper bound are clamped to upper bound."""
        assert clamp(15, 0, 10) == 10
        assert clamp(11, 0, 10) == 10

    def test_clamp_with_floats(self):
        """Test clamp function with floating point numbers."""
        assert clamp(5.5, 0.0, 10.0) == 5.5
        assert clamp(-1.5, 0.0, 10.0) == 0.0
        assert clamp(10.5, 0.0, 10.0) == 10.0

    def test_clamp_invalid_bounds(self):
        """Test that invalid bounds (lo > hi) raise ValueError."""
        with pytest.raises(ValueError, match="Lower bound \\(10\\).*upper bound \\(0\\)"):
            clamp(5, 10, 0)

    def test_clamp_equal_bounds(self):
        """Test clamp function when lower and upper bounds are equal."""
        assert clamp(5, 7, 7) == 7
        assert clamp(7, 7, 7) == 7
        assert clamp(9, 7, 7) == 7