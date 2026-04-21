"""Listing service: query helpers for paginated resource lists."""

from sample_project.models.user import User
from sample_project.models.project import Project


def list_users(users: list[User], active_only: bool = False) -> list[str]:
    """Return user IDs, optionally filtered to active users only."""
    if active_only:
        return [u.user_id for u in users if u.active]
    return [u.user_id for u in users]


def list_projects(projects: list[Project], include_archived: bool = False) -> list[str]:
    """Return project IDs, optionally including archived entries."""
    if include_archived:
        return [p.project_id for p in projects]
    return [p.project_id for p in projects if not p.archived]


def paginate(items: list[object], page: int, page_size: int) -> list[object]:
    """Slice a list into a single page of results. Page index is 1-based."""
    if page < 1 or page_size < 1:
        return []
    start = (page - 1) * page_size
    return items[start : start + page_size]
