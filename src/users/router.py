"""User router."""

import logging
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..users.models import User
from ..auth.dependencies import get_current_active_user
from .schemas import UserCreate, UserUpdate, UserResponse, UserListResponse
from .service import UserService
from .dependencies import get_user_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Users",
    description="Get list of all users (admin only)"
)
def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service)
) -> UserListResponse:
    """List all users with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user
        service: User service
        
    Returns:
        List of users with pagination info
    """
    return service.get_users(db, skip=skip, limit=limit, current_user=current_user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get User",
    description="Get user by ID"
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Get user by ID.
    
    Args:
        user_id: User ID
        db: Database session
        current_user: Current authenticated user
        service: User service
        
    Returns:
        User data
    """
    return service.get_user(db, user_id, current_user)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create User",
    description="Create a new user (admin only)"
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Create a new user.
    
    Args:
        user_data: User creation data
        db: Database session
        current_user: Current authenticated user
        service: User service
        
    Returns:
        Created user
    """
    return service.create_user(db, user_data, current_user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update User",
    description="Update user information"
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Update a user.
    
    Args:
        user_id: User ID
        user_data: User update data
        db: Database session
        current_user: Current authenticated user
        service: User service
        
    Returns:
        Updated user
    """
    return service.update_user(db, user_id, user_data, current_user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete User",
    description="Delete a user (admin only)"
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service)
) -> None:
    """Delete a user.
    
    Args:
        user_id: User ID
        db: Database session
        current_user: Current authenticated user
        service: User service
    """
    service.delete_user(db, user_id, current_user)
