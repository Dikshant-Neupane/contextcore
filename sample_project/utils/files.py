"""File system utility helpers."""

from pathlib import Path


def read_text(path: Path) -> str:
    """Read and return the full UTF-8 text content of a file."""
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    """Write a UTF-8 string to a file, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def list_python_files(root: Path) -> list[Path]:
    """Recursively collect all .py files under a root directory."""
    return sorted(p for p in root.rglob("*.py") if p.is_file())


def file_size_kb(path: Path) -> float:
    """Return file size in kilobytes rounded to two decimal places."""
    return round(path.stat().st_size / 1024, 2)
