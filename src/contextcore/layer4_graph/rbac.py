"""Role-based path access helpers for v4 query filtering."""

from __future__ import annotations


def can_access_path(role: str, filepath: str) -> bool:
    """Return True when role is allowed to access the given file path."""
    normalized_role = role.strip().lower()
    normalized_path = filepath.replace("\\", "/").lower()

    if normalized_role == "maintainer":
        return True

    if normalized_role == "developer":
        return (
            normalized_path.startswith("src/")
            or normalized_path.startswith("sample_project/")
            or "/src/" in normalized_path
            or "/sample_project/" in normalized_path
        )

    if normalized_role == "auditor":
        return (
            normalized_path.startswith("tests/")
            or normalized_path.startswith("hooks/")
            or "/tests/" in normalized_path
            or "/hooks/" in normalized_path
            or normalized_path.endswith("/readme.md")
            or normalized_path.endswith("/project.md")
            or normalized_path.endswith("/context.md")
            or normalized_path.endswith("/decisions.md")
        )

    return False
