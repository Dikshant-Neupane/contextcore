"""User domain model."""

from dataclasses import dataclass, field


@dataclass
class User:
    """Represents a registered system user."""

    user_id: str
    name: str
    email: str = ""
    active: bool = True
    tags: list[str] = field(default_factory=list)

    def display_name(self) -> str:
        """Return a human-readable display name for UI rendering."""
        clean = self.name.strip()
        return clean if clean else self.user_id

    def deactivate(self) -> None:
        """Mark this user as inactive so they cannot log in."""
        self.active = False

    def add_tag(self, tag: str) -> None:
        """Attach a classification tag if it is not already present."""
        if tag and tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove a classification tag if it exists."""
        if tag in self.tags:
            self.tags.remove(tag)

    def to_dict(self) -> dict[str, object]:
        """Serialize the user to a plain dictionary for storage."""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "active": self.active,
            "tags": list(self.tags),
        }
