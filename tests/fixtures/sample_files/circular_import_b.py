"""Circular import B — used to test graceful handling of circular dependencies."""

MODULE_NAME = "circular_b"


def get_name() -> str:
    """Return this module's name."""
    return MODULE_NAME
