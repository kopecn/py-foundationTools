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
