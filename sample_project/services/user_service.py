"""User service: business logic layer for User operations."""

from sample_project.models.user import User


def build_user(user_id: str, name: str, email: str = "") -> User:
    """Create and return a new active User instance."""
    if not user_id.strip():
        raise ValueError("user_id must not be blank")
    return User(user_id=user_id.strip(), name=name.strip(), email=email.strip())


def find_active_users(users: list[User]) -> list[User]:
    """Filter and return only active users from the provided list."""
    return [u for u in users if u.active]


def deactivate_user(users: list[User], user_id: str) -> bool:
    """Deactivate a user by ID. Returns True if found and deactivated."""
    for user in users:
        if user.user_id == user_id:
            user.deactivate()
            return True
    return False


def tag_user(users: list[User], user_id: str, tag: str) -> bool:
    """Add a tag to a user identified by user_id. Returns True if found."""
    for user in users:
        if user.user_id == user_id:
            user.add_tag(tag)
            return True
    return False
