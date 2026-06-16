"""Authentication router."""

import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..users.models import User
from ..users.repository import UserRepository
from ..exceptions import UnauthorizedException, BadRequestException
from .schemas import LoginRequest, TokenResponse, RefreshTokenRequest, CurrentUserResponse
from .utils import verify_password, create_access_token, create_refresh_token, decode_token
from .dependencies import get_current_active_user
from .config import auth_config

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login",
    description="Authenticate user and return access and refresh tokens"
)
def login(login_data: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Login endpoint.
    
    Args:
        login_data: Login credentials
        db: Database session
        
    Returns:
        Access and refresh tokens
        
    Raises:
        UnauthorizedException: If credentials are invalid
    """
    user_repo = UserRepository()
    
    # Get user by email
    user = user_repo.get_by_email(db, login_data.email)
    
    if not user:
        logger.warning(f"Login attempt with non-existent email: {login_data.email}")
        raise UnauthorizedException("Invalid email or password")
    
    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        logger.warning(f"Failed login attempt for user: {user.email}")
        raise UnauthorizedException("Invalid email or password")
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"Inactive user login attempt: {user.email}")
        raise UnauthorizedException("User account is inactive")
    
    # Create tokens
    token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    logger.info(f"User logged in: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh Token",
    description="Refresh access token using refresh token"
)
def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Refresh token endpoint.
    
    Args:
        refresh_data: Refresh token
        db: Database session
        
    Returns:
        New access and refresh tokens
        
    Raises:
        UnauthorizedException: If refresh token is invalid
    """
    # Decode refresh token
    payload = decode_token(refresh_data.refresh_token)
    
    if not payload:
        logger.warning("Invalid refresh token")
        raise UnauthorizedException("Invalid refresh token")
    
    # Check token type
    if payload.get("type") != auth_config.TOKEN_TYPE_REFRESH:
        logger.warning("Invalid token type for refresh")
        raise UnauthorizedException("Invalid token type")
    
    # Get user ID
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload")
    
    # Verify user exists and is active
    user_repo = UserRepository()
    user = user_repo.get_by_id(db, int(user_id))
    
    if not user or not user.is_active:
        logger.warning(f"Refresh token for invalid/inactive user: {user_id}")
        raise UnauthorizedException("User not found or inactive")
    
    # Create new tokens
    token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    logger.info(f"Token refreshed for user: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User",
    description="Get current authenticated user information"
)
def get_me(current_user: User = Depends(get_current_active_user)) -> CurrentUserResponse:
    """Get current user endpoint.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user information
    """
    return CurrentUserResponse.model_validate(current_user)
