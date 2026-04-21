"""Circular import A — used to test graceful handling of circular dependencies."""

# In a real project this would import from circular_import_b; here we simulate
# the structure without actually triggering a Python circular import error.
MODULE_NAME = "circular_a"


def get_name() -> str:
    """Return this module's name."""
    return MODULE_NAME
