"""A Python file with a class and multiple typed methods — fixture for tests."""


class Calculator:
    """A simple four-operation calculator."""

    def add(self, x: int, y: int) -> int:
        """Return the sum of x and y."""
        return x + y

    def subtract(self, x: int, y: int) -> int:
        """Return x minus y."""
        return x - y

    def multiply(self, x: int, y: int) -> int:
        """Return the product of x and y."""
        return x * y

    def divide(self, x: float, y: float) -> float:
        """Return x divided by y."""
        return x / y
