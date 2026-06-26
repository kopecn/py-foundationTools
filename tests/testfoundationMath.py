"""
Unit tests for foundationMath module.
"""

from math import pi

import pytest
from src.foundationMath.math import clamp, wrap


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


class TestWrap:
    """Test cases for the wrap function."""

    def test_wrap_within_bounds(self):
        """Test that values within bounds remain unchanged."""
        assert wrap(0, -pi, pi) == 0
        assert wrap(1.5, -pi, pi) == 1.5
        assert wrap(-1.5, -pi, pi) == -1.5

    def test_wrap_at_lower_boundary(self):
        """Test that lower boundary is inclusive."""
        assert wrap(-pi, -pi, pi) == -pi

    def test_wrap_at_upper_boundary(self):
        """Test that upper boundary wraps to lower boundary."""
        result = wrap(pi, -pi, pi)
        assert abs(result - (-pi)) < 1e-10

    def test_wrap_above_range(self):
        """Test wrapping values above the upper bound."""
        # pi + 1 should wrap to -pi + 1
        result = wrap(pi + 1, -pi, pi)
        expected = -pi + 1
        assert abs(result - expected) < 1e-10

    def test_wrap_below_range(self):
        """Test wrapping values below the lower bound."""
        # -pi - 1 should wrap to pi - 1
        result = wrap(-pi - 1, -pi, pi)
        expected = pi - 1
        assert abs(result - expected) < 1e-10

    def test_wrap_multiple_wraps_above(self):
        """Test wrapping values that exceed the range multiple times."""
        # 3*pi should wrap to -pi (after one full cycle)
        result = wrap(3 * pi, -pi, pi)
        expected = -pi
        assert abs(result - expected) < 1e-10

    def test_wrap_multiple_wraps_below(self):
        """Test wrapping values below the range multiple times."""
        # -3*pi should wrap to -pi
        result = wrap(-3 * pi, -pi, pi)
        expected = -pi
        assert abs(result - expected) < 1e-10

    def test_wrap_custom_range(self):
        """Test wrap with custom range [0, 360)."""
        assert wrap(0, 0, 360) == 0
        assert wrap(180, 0, 360) == 180
        assert wrap(360, 0, 360) == 0
        assert wrap(450, 0, 360) == 90
        assert wrap(-90, 0, 360) == 270

    def test_wrap_custom_negative_range(self):
        """Test wrap with custom negative range."""
        assert wrap(-5, -10, 0) == -5
        assert wrap(0, -10, 0) == -10
        assert wrap(5, -10, 0) == -5
        assert wrap(-15, -10, 0) == -5

    def test_wrap_small_range(self):
        """Test wrap with a small range."""
        assert wrap(0.5, 0, 1) == 0.5
        assert wrap(1.5, 0, 1) == 0.5
        assert wrap(2.7, 0, 1) == pytest.approx(0.7, abs=1e-10)
        assert wrap(-0.3, 0, 1) == pytest.approx(0.7, abs=1e-10)

    def test_wrap_default_parameters(self):
        """Test wrap with default parameters (angle normalization)."""
        assert wrap(0) == 0
        assert wrap(pi / 2) == pi / 2
        assert wrap(-pi / 2) == -pi / 2

    def test_wrap_with_floats(self):
        """Test wrap with floating point numbers."""
        result = wrap(7.5, 0.0, 5.0)
        assert abs(result - 2.5) < 1e-10
