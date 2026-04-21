"""Project domain model."""

from dataclasses import dataclass, field


@dataclass
class Project:
    """Represents a tracked software project."""

    project_id: str
    title: str
    description: str = ""
    owner_id: str = ""
    archived: bool = False
    file_count: int = 0
    labels: list[str] = field(default_factory=list)

    def archive(self) -> None:
        """Mark the project as archived and immutable."""
        self.archived = True

    def set_owner(self, owner_id: str) -> None:
        """Assign an owner. Raises ValueError for empty owner_id."""
        if not owner_id.strip():
            raise ValueError("owner_id must not be empty")
        self.owner_id = owner_id

    def increment_files(self, count: int = 1) -> None:
        """Increase the tracked file count by the given amount."""
        if count < 0:
            raise ValueError("count must be non-negative")
        self.file_count += count

    def summary(self) -> str:
        """Return a one-line human-readable project summary."""
        status = "archived" if self.archived else "active"
        return f"{self.title} [{status}] files={self.file_count}"

    def to_dict(self) -> dict[str, object]:
        """Serialize to a plain dictionary suitable for JSON output."""
        return {
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "owner_id": self.owner_id,
            "archived": self.archived,
            "file_count": self.file_count,
            "labels": list(self.labels),
        }
