"""A Python file with multiple import styles and top-level functions — fixture for tests."""

import os
from pathlib import Path
from typing import Optional


def read_file(path: str) -> Optional[str]:
    """Read a file and return its text contents, or None if it does not exist."""
    p = Path(path)
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8")


def file_exists(path: str) -> bool:
    """Return True if the path exists on disk."""
    return os.path.exists(path)
