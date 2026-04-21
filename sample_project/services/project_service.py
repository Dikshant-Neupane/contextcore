"""Project service: business logic for Project lifecycle operations."""

from sample_project.models.project import Project


def build_project(project_id: str, title: str, owner_id: str = "") -> Project:
    """Create and return a new active Project instance."""
    if not project_id.strip():
        raise ValueError("project_id must not be blank")
    project = Project(project_id=project_id.strip(), title=title.strip())
    if owner_id:
        project.set_owner(owner_id)
    return project


def archive_project(projects: list[Project], project_id: str) -> bool:
    """Archive a project by ID. Returns True if the project was found."""
    for project in projects:
        if project.project_id == project_id:
            project.archive()
            return True
    return False


def find_by_owner(projects: list[Project], owner_id: str) -> list[Project]:
    """Return all non-archived projects belonging to the given owner."""
    return [p for p in projects if p.owner_id == owner_id and not p.archived]


def total_files(projects: list[Project]) -> int:
    """Return the aggregate file count across all tracked projects."""
    return sum(p.file_count for p in projects)
