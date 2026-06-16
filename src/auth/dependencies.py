"""Authentication dependencies."""

from typing import Optional
from fastapi import Depends, Header
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..users.models import User
from ..exceptions import UnauthorizedException
from .utils import decode_token
from .config import auth_config


def get_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    """Extract JWT token from Authorization header.
    
    Args:
        authorization: Authorization header value
        
    Returns:
        JWT token
        
    Raises:
        UnauthorizedException: If token is missing or invalid format
    """
    if not authorization:
        raise UnauthorizedException("Authorization header missing")
    
    parts = authorization.split()
    
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedException("Invalid authorization header format")
    
    return parts[1]

def get_optional_token_from_header(
    authorization: Optional[str] = Header(None)
) -> Optional[str]:
    """Extract JWT token from Authorization header (optional).
    
    Returns None if no token provided, raises exception if token format is invalid.
    """
    if not authorization:
        return None
    
    parts = authorization.split()
    
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedException("Invalid authorization header format")
    
    return parts[1]


def get_current_user(
    token: str = Depends(get_token_from_header),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token.
    
    Args:
        token: JWT access token
        db: Database session
        
    Returns:
        Current user
        
    Raises:
        UnauthorizedException: If token is invalid or user not found
    """
    payload = decode_token(token)
    
    if not payload:
        raise UnauthorizedException("Invalid token")
    
    # Check token type
    if payload.get("type") != auth_config.TOKEN_TYPE_ACCESS:
        raise UnauthorizedException("Invalid token type")
    
    # Get user ID from token
    user_id: Optional[int] = payload.get("sub")
    
    if user_id is None:
        raise UnauthorizedException("Invalid token payload")
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise UnauthorizedException("User not found")
    
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user.
    
    Args:
        current_user: Current user from token
        
    Returns:
        Current active user
        
    Raises:
        UnauthorizedException: If user is inactive
    """
    if not current_user.is_active:
        raise UnauthorizedException("Inactive user")
    
    return current_user


def get_optional_current_user(
    token: Optional[str] = Depends(get_optional_token_from_header),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Optional authentication.
    
    Returns the user if they are authorized and active, otherwise None.
    If token format is invalid, raises UnauthorizedException.
    """
    if not token:
        return None
    
    try:
        payload = decode_token(token)
        
        if not payload:
            return None
        
        # Check token type
        if payload.get("type") != auth_config.TOKEN_TYPE_ACCESS:
            return None
        
        # Get user ID from token
        user_id: Optional[int] = payload.get("sub")
        
        if user_id is None:
            return None
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return None
        
        # Check if user is active
        if not user.is_active:
            return None
        
        return user
    
    except Exception:
        # If anything goes wrong with token decoding, just return None
        return None