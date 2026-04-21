"""Extended mathematical helpers not covered by the standard library."""


def clamp(value: int, low: int, high: int) -> int:
    """Constrain an integer to the inclusive range [low, high]."""
    return max(low, min(value, high))


def safe_divide(numerator: float, denominator: float) -> float:
    """Divide two numbers, returning 0.0 when denominator is zero."""
    if denominator == 0:
        return 0.0
    return numerator / denominator


def median(values: list[float]) -> float:
    """Compute the median of a non-empty list of floats."""
    if not values:
        raise ValueError("Cannot compute median of an empty list")
    sorted_vals = sorted(values)
    mid = len(sorted_vals) // 2
    if len(sorted_vals) % 2 == 0:
        return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2.0
    return sorted_vals[mid]
