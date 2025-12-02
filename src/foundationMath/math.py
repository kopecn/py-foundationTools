"""
Mathematical utility functions.

This module provides common mathematical operations and utilities
for numerical computations and value manipulation.
"""

from math import pi


def clamp(x: float, lo: float, hi: float) -> float:
    """
    Clamp a value between a minimum and maximum bound.
    - x: The value to clamp
    - lo: The minimum bound (inclusive)
    - hi: The maximum bound (inclusive)

    Returns: The clamped value, constrained to [lo, hi]

    Raises: ValueError: If lo > hi
    """
    if lo > hi:
        raise ValueError(
            f"Lower bound ({lo}) cannot be greater than upper bound ({hi})"
        )

    return max(lo, min(x, hi))


def wrap(a: float, lo: float = -pi, hi: float = pi) -> float:
    """
    Normalize a value to the range [lo, hi].

    Args:
        a: Value to normalize (e.g., angle in radians).
        lo: Lower bound of the range (inclusive, default: -pi).
        hi: Upper bound of the range (exclusive, default: pi).

    Returns:
        Value normalized to [lo, hi).
    """
    span = hi - lo
    return ((a - lo) % span) + lo
