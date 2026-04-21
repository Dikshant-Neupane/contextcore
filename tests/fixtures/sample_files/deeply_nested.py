"""A Python file with nested class and function definitions — fixture for tests."""


class Outer:
    """Outer class with an inner class and its own method."""

    class Inner:
        """Inner class that should NOT appear as a top-level structure."""

        def inner_method(self) -> str:
            """Return a string from the inner method."""
            return "inner"

    def outer_method(self) -> int:
        """Return an integer from the outer method."""
        return 42


def top_level(x: int) -> bool:
    """A top-level function alongside the nested class."""
    return x > 0
