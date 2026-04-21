"""String normalization and transformation utilities."""


def normalize_name(value: str) -> str:
    """Collapse internal whitespace and strip leading/trailing spaces."""
    return " ".join(value.strip().split())


def to_slug(value: str) -> str:
    """Convert a display string to a lowercase hyphenated slug."""
    return normalize_name(value).lower().replace(" ", "-")


def truncate(value: str, length: int, suffix: str = "...") -> str:
    """Truncate a string to length characters, appending suffix if cut."""
    if len(value) <= length:
        return value
    return value[: length - len(suffix)] + suffix


def is_blank(value: str) -> bool:
    """Return True when the string is empty or contains only whitespace."""
    return not value or not value.strip()
