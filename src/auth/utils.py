"""Authentication utilities for password hashing and JWT tokens."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import auth_config

# Password hashing context
pwd_context = CryptContext(
    schemes=auth_config.PWD_CONTEXT_SCHEMES,
    deprecated=auth_config.PWD_CONTEXT_DEPRECATED
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    # Encode to bytes and truncate to 72 bytes if needed
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        # Decode back to string after truncating
        plain_password = password_bytes[:72].decode('utf-8', errors='ignore')

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    # Encode to bytes and truncate to 72 bytes if needed
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # Decode back to string after truncating
        password = password_bytes[:72].decode('utf-8', errors='ignore')

    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=auth_config.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": auth_config.TOKEN_TYPE_ACCESS
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        auth_config.SECRET_KEY,
        algorithm=auth_config.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token.
    
    Args:
        data: Data to encode in the token
        
    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=auth_config.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "type": auth_config.TOKEN_TYPE_REFRESH
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        auth_config.SECRET_KEY,
        algorithm=auth_config.ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify a JWT token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            auth_config.SECRET_KEY,
            algorithms=[auth_config.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
