"""User service for business logic."""

import logging
from typing import List
from sqlalchemy.orm import Session
from .repository import IUserRepository, UserRepository
from .schemas import UserCreate, UserUpdate, UserResponse, UserListResponse
from .models import User
from .enums import UserRole
from ..exceptions import NotFoundException, ConflictException, ForbiddenException

logger = logging.getLogger(__name__)


class UserService:
    """User service implementing business logic."""
    
    def __init__(self, repository: IUserRepository = None):
        """Initialize service with repository.
        
        Args:
            repository: User repository instance
        """
        self.repository = repository or UserRepository()
    
    def create_user(self, db: Session, user_data: UserCreate, current_user: User) -> UserResponse:
        """Create a new user.
        
        Args:
            db: Database session
            user_data: User creation data
            current_user: User making the request
            
        Returns:
            Created user
            
        Raises:
            ForbiddenException: If user doesn't have permission
            ConflictException: If email already exists
        """
        # Only admins can create users
        if current_user.role != UserRole.ADMIN:
            logger.warning(f"User {current_user.id} attempted to create user without permission")
            raise ForbiddenException("Only administrators can create users")
        
        # Check if email already exists
        existing_user = self.repository.get_by_email(db, user_data.email)
        if existing_user:
            logger.warning(f"Attempted to create user with existing email: {user_data.email}")
            raise ConflictException(f"User with email {user_data.email} already exists")
        
        user = self.repository.create(db, user_data)
        logger.info(f"User created: {user.id} by admin {current_user.id}")
        
        return UserResponse.model_validate(user)
    
    def get_user(self, db: Session, user_id: int, current_user: User = None) -> UserResponse:
        """Get user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User data
            
        Raises:
            NotFoundException: If user not found
        """
        if current_user.role != UserRole.ADMIN and current_user.id != user_id:
            logger.warning(f"User {current_user.id} attempted to get info about user {user_id} without permission")
            raise ForbiddenException("Only administrators can get info about other users")
        
        user = self.repository.get_by_id(db, user_id)
        
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise NotFoundException(f"User with ID {user_id} not found")
        
        return UserResponse.model_validate(user)
    
    def get_users(self, db: Session, skip: int = 0, limit: int = 100, current_user: User = None) -> UserListResponse:
        """Get all users with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            current_user: User making the request
            
        Returns:
            List of users with pagination info
            
        Raises:
            ForbiddenException: If user doesn't have permission
        """
        # Only admins can list all users
        if current_user and current_user.role != UserRole.ADMIN:
            logger.warning(f"User {current_user.id} attempted to list users without permission")
            raise ForbiddenException("Only administrators can list users")
        
        users = self.repository.get_all(db, skip=skip, limit=limit)
        total = self.repository.count(db)
        
        return UserListResponse(
            users=[UserResponse.model_validate(user) for user in users],
            total=total,
            skip=skip,
            limit=limit
        )
    
    def update_user(self, db: Session, user_id: int, user_data: UserUpdate, current_user: User) -> UserResponse:
        """Update a user.
        
        Args:
            db: Database session
            user_id: User ID
            user_data: User update data
            current_user: User making the request
            
        Returns:
            Updated user
            
        Raises:
            ForbiddenException: If user doesn't have permission
            NotFoundException: If user not found
            ConflictException: If email already exists
        """
        # Users can update themselves, admins can update anyone
        if current_user.role != UserRole.ADMIN and current_user.id != user_id:
            logger.warning(f"User {current_user.id} attempted to update user {user_id} without permission")
            raise ForbiddenException("You don't have permission to update this user")
        
        # Only admins can change roles
        if user_data.role is not None and current_user.role != UserRole.ADMIN:
            logger.warning(f"User {current_user.id} attempted to change role without permission")
            raise ForbiddenException("Only administrators can change user roles")
        
        # Check if email is being changed and already exists
        if user_data.email:
            existing_user = self.repository.get_by_email(db, user_data.email)
            if existing_user and existing_user.id != user_id:
                logger.warning(f"Attempted to update user with existing email: {user_data.email}")
                raise ConflictException(f"User with email {user_data.email} already exists")
        
        user = self.repository.update(db, user_id, user_data)
        
        if not user:
            logger.warning(f"User not found for update: {user_id}")
            raise NotFoundException(f"User with ID {user_id} not found")
        
        logger.info(f"User updated: {user_id} by user {current_user.id}")
        
        return UserResponse.model_validate(user)
    
    def delete_user(self, db: Session, user_id: int, current_user: User) -> None:
        """Delete a user.
        
        Args:
            db: Database session
            user_id: User ID
            current_user: User making the request
            
        Raises:
            ForbiddenException: If user doesn't have permission
            NotFoundException: If user not found
        """
        # Only admins can delete users
        if current_user.role != UserRole.ADMIN:
            logger.warning(f"User {current_user.id} attempted to delete user without permission")
            raise ForbiddenException("Only administrators can delete users")
        
        # Prevent self-deletion
        if current_user.id == user_id:
            logger.warning(f"User {current_user.id} attempted to delete themselves")
            raise ForbiddenException("You cannot delete your own account")
        
        deleted = self.repository.delete(db, user_id)
        
        if not deleted:
            logger.warning(f"User not found for deletion: {user_id}")
            raise NotFoundException(f"User with ID {user_id} not found")
        
        logger.info(f"User deleted: {user_id} by admin {current_user.id}")
