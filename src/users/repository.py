"""User repository for database operations."""

from typing import Optional, List, Protocol
from sqlalchemy.orm import Session
from .models import User
from .schemas import UserCreate, UserUpdate
from ..auth.utils import get_password_hash


class IUserRepository(Protocol):
    """Interface for user repository."""
    
    def create(self, db: Session, user_data: UserCreate) -> User:
        """Create a new user."""
        ...
    
    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        ...
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        ...
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        ...
    
    def update(self, db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update a user."""
        ...
    
    def delete(self, db: Session, user_id: int) -> bool:
        """Delete a user."""
        ...
    
    def count(self, db: Session) -> int:
        """Count total users."""
        ...


class UserRepository:
    """Concrete implementation of user repository."""
    
    def create(self, db: Session, user_data: UserCreate) -> User:
        """Create a new user.
        
        Args:
            db: Database session
            user_data: User creation data
            
        Returns:
            Created user
        """
        hashed_password = get_password_hash(user_data.password)
        
        db_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=user_data.role,
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User or None if not found
        """
        return db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email.
        
        Args:
            db: Database session
            email: User email
            
        Returns:
            User or None if not found
        """
        return db.query(User).filter(User.email == email).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of users
        """
        return db.query(User).offset(skip).limit(limit).all()
    
    def update(self, db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update a user.
        
        Args:
            db: Database session
            user_id: User ID
            user_data: User update data
            
        Returns:
            Updated user or None if not found
        """
        db_user = self.get_by_id(db, user_id)
        
        if not db_user:
            return None
        
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Hash password if provided
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    def delete(self, db: Session, user_id: int) -> bool:
        """Delete a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            True if deleted, False if not found
        """
        db_user = self.get_by_id(db, user_id)
        
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        
        return True
    
    def count(self, db: Session) -> int:
        """Count total users.
        
        Args:
            db: Database session
            
        Returns:
            Total number of users
        """
        return db.query(User).count()
