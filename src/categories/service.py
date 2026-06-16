"""Category service for business logic."""

import logging
from typing import List
from sqlalchemy.orm import Session
from .repository import ICategoryRepository, CategoryRepository
from .schemas import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse
from ..users.models import User
from ..users.enums import UserRole
from ..exceptions import NotFoundException, ConflictException, ForbiddenException

logger = logging.getLogger(__name__)


class CategoryService:
    """Category service implementing business logic."""
    
    def __init__(self, repository: ICategoryRepository = None):
        """Initialize service with repository.
        
        Args:
            repository: Category repository instance
        """
        self.repository = repository or CategoryRepository()
    
    def create_category(self, db: Session, data: CategoryCreate, current_user: User) -> CategoryResponse:
        """Create a new category.
        
        Args:
            db: Database session
            data: Category creation data
            current_user: User making the request
            
        Returns:
            Created category
            
        Raises:
            ForbiddenException: If user doesn't have permission
            ConflictException: If slug already exists
        """
        # Only admins and editors can create categories
        if current_user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
            logger.warning(f"User {current_user.id} attempted to create category without permission")
            raise ForbiddenException("Only administrators and editors can create categories")
        
        # Check if slug already exists
        slug = data.slug if data.slug else data.name.lower().replace(' ', '-')
        existing = self.repository.get_by_slug(db, slug)
        if existing:
            logger.warning(f"Attempted to create category with existing slug: {slug}")
            raise ConflictException(f"Category with slug '{slug}' already exists")
        
        category = self.repository.create(db, data, current_user.id)
        logger.info(f"Category created: {category.id} by user {current_user.id}")
        
        return CategoryResponse.model_validate(category)
    
    def get_category(self, db: Session, category_id: int) -> CategoryResponse:
        """Get category by ID.
        
        Args:
            db: Database session
            category_id: Category ID
            
        Returns:
            Category data
            
        Raises:
            NotFoundException: If category not found
        """
        category = self.repository.get_by_id(db, category_id)
        
        if not category:
            logger.warning(f"Category not found: {category_id}")
            raise NotFoundException(f"Category with ID {category_id} not found")
        
        return CategoryResponse.model_validate(category)
    
    def get_category_by_slug(self, db: Session, slug: str) -> CategoryResponse:
        """Get category by slug.
        
        Args:
            db: Database session
            slug: Category slug
            
        Returns:
            Category data
            
        Raises:
            NotFoundException: If category not found
        """
        category = self.repository.get_by_slug(db, slug)
        
        if not category:
            logger.warning(f"Category not found: {slug}")
            raise NotFoundException(f"Category with slug '{slug}' not found")
        
        return CategoryResponse.model_validate(category)
    
    def get_categories(self, db: Session, current_user: User = None) -> CategoryListResponse:
        """Get all categories.
        
        Args:
            db: Database session
            current_user: User making the request (optional)
            
        Returns:
            List of categories
        """
        # Admins and editors can see hidden categories
        include_hidden = current_user and current_user.role in [UserRole.ADMIN, UserRole.EDITOR]
        
        categories = self.repository.get_all(db, include_hidden=include_hidden)
        
        return CategoryListResponse(
            categories=[CategoryResponse.model_validate(cat) for cat in categories],
            total=len(categories)
        )
    
    def update_category(self, db: Session, category_id: int, data: CategoryUpdate, current_user: User) -> CategoryResponse:
        """Update a category.
        
        Args:
            db: Database session
            category_id: Category ID
            data: Category update data
            current_user: User making the request
            
        Returns:
            Updated category
            
        Raises:
            ForbiddenException: If user doesn't have permission
            NotFoundException: If category not found
            ConflictException: If slug already exists
        """
        # Only admins and editors can update categories
        if current_user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
            logger.warning(f"User {current_user.id} attempted to update category without permission")
            raise ForbiddenException("Only administrators and editors can update categories")
        
        # Check if slug is being changed and already exists
        if data.slug:
            existing = self.repository.get_by_slug(db, data.slug)
            if existing and existing.id != category_id:
                logger.warning(f"Attempted to update category with existing slug: {data.slug}")
                raise ConflictException(f"Category with slug '{data.slug}' already exists")
        
        category = self.repository.update(db, category_id, data)
        
        if not category:
            logger.warning(f"Category not found for update: {category_id}")
            raise NotFoundException(f"Category with ID {category_id} not found")
        
        logger.info(f"Category updated: {category_id} by user {current_user.id}")
        
        return CategoryResponse.model_validate(category)
    
    def delete_category(self, db: Session, category_id: int, current_user: User) -> None:
        """Delete a category.
        
        Args:
            db: Database session
            category_id: Category ID
            current_user: User making the request
            
        Raises:
            ForbiddenException: If user doesn't have permission
            NotFoundException: If category not found
        """
        # Only admins can delete categories
        if current_user.role != UserRole.ADMIN:
            logger.warning(f"User {current_user.id} attempted to delete category without permission")
            raise ForbiddenException("Only administrators can delete categories")
        
        deleted = self.repository.delete(db, category_id)
        
        if not deleted:
            logger.warning(f"Category not found for deletion: {category_id}")
            raise NotFoundException(f"Category with ID {category_id} not found")
        
        logger.info(f"Category deleted: {category_id} by admin {current_user.id}")
