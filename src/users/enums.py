"""User-related enumerations."""

from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
    
    def __str__(self) -> str:
        return self.value
