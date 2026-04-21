"""Identifier construction and validation helpers."""

import re

_ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]{1,62}[a-z0-9]$")


def make_id(prefix: str, number: int) -> str:
    """Build a deterministic hyphen-delimited ID from a prefix and number."""
    if not prefix.isalpha():
        raise ValueError("prefix must be alphabetic")
    return f"{prefix.lower()}-{number}"


def is_valid_id(value: str) -> bool:
    """Return True if the value matches the canonical ID format."""
    return bool(_ID_PATTERN.match(value))


def parse_id(value: str) -> tuple[str, int]:
    """Split a formatted ID into its prefix and numeric parts."""
    parts = value.rsplit("-", 1)
    if len(parts) != 2 or not parts[1].isdigit():
        raise ValueError(f"Cannot parse ID: {value!r}")
    return parts[0], int(parts[1])
