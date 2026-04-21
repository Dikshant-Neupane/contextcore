"""Label rendering and normalization utilities for display."""

from sample_project.utils.strings import normalize_name


def render_label(name: str) -> str:
    """Render a normalized display label prefixed with 'Label:'."""
    return f"Label:{normalize_name(name)}"


def truncate_label(label: str, max_length: int = 32) -> str:
    """Truncate a label to max_length characters with an ellipsis suffix."""
    if len(label) <= max_length:
        return label
    return label[: max_length - 1] + "…"


def build_badge(key: str, value: str) -> str:
    """Format a key-value pair as a compact badge string."""
    safe_key = normalize_name(key).replace(" ", "_").lower()
    safe_val = normalize_name(value)
    return f"[{safe_key}:{safe_val}]"
