"""Authentication configuration."""

from ..config import settings


class AuthConfig:
    """Authentication configuration class."""
    
    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = settings.ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    # JWT token types
    TOKEN_TYPE_ACCESS = "access"
    TOKEN_TYPE_REFRESH = "refresh"
    
    # Password hashing
    PWD_CONTEXT_SCHEMES = ["bcrypt"]
    PWD_CONTEXT_DEPRECATED = "auto"


auth_config = AuthConfig()
