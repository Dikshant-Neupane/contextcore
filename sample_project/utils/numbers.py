"""Numeric utility functions for common arithmetic checks."""


def is_even(value: int) -> bool:
    """Return True if the integer is evenly divisible by two."""
    return value % 2 == 0


def clamp(value: int, low: int, high: int) -> int:
    """Constrain value to the closed interval [low, high]."""
    return max(low, min(value, high))


def percentage(part: float, total: float) -> float:
    """Compute what percentage part is of total. Returns 0.0 for zero total."""
    if total == 0:
        return 0.0
    return (part / total) * 100.0


def round_to(value: float, decimals: int) -> float:
    """Round a float to the specified number of decimal places."""
    return round(value, decimals)
