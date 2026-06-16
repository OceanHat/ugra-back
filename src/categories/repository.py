"""Category repository for database operations."""

import re
from typing import Optional, List, Protocol
from sqlalchemy.orm import Session
from .models import Category
from .schemas import CategoryCreate, CategoryUpdate


def generate_slug(name: str) -> str:
    """Generate URL-friendly slug from name.
    
    Args:
        name: Category name
        
    Returns:
        URL-friendly slug
    """
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = slug.strip('-')
    return slug


class ICategoryRepository(Protocol):
    """Interface for category repository."""
    
    def create(self, db: Session, data: CategoryCreate, user_id: int) -> Category:
        """Create a new category."""
        ...
    
    def get_by_id(self, db: Session, category_id: int) -> Optional[Category]:
        """Get category by ID."""
        ...
    
    def get_by_slug(self, db: Session, slug: str) -> Optional[Category]:
        """Get category by slug."""
        ...
    
    def get_all(self, db: Session, include_hidden: bool = False) -> List[Category]:
        """Get all categories."""
        ...
    
    def update(self, db: Session, category_id: int, data: CategoryUpdate) -> Optional[Category]:
        """Update a category."""
        ...
    
    def delete(self, db: Session, category_id: int) -> bool:
        """Delete a category."""
        ...
    
    def count(self, db: Session) -> int:
        """Count total categories."""
        ...


class CategoryRepository:
    """Concrete implementation of category repository."""
    
    def create(self, db: Session, data: CategoryCreate, user_id: int) -> Category:
        """Create a new category.
        
        Args:
            db: Database session
            data: Category creation data
            user_id: ID of user creating the category
            
        Returns:
            Created category
        """
        slug = data.slug if data.slug else generate_slug(data.name)
        
        db_category = Category(
            name=data.name,
            slug=slug,
            description=data.description,
            is_hidden=data.is_hidden,
            created_by_id=user_id
        )
        
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        
        return db_category
    
    def get_by_id(self, db: Session, category_id: int) -> Optional[Category]:
        """Get category by ID.
        
        Args:
            db: Database session
            category_id: Category ID
            
        Returns:
            Category or None if not found
        """
        return db.query(Category).filter(Category.id == category_id).first()
    
    def get_by_slug(self, db: Session, slug: str) -> Optional[Category]:
        """Get category by slug.
        
        Args:
            db: Database session
            slug: Category slug
            
        Returns:
            Category or None if not found
        """
        return db.query(Category).filter(Category.slug == slug).first()
    
    def get_all(self, db: Session, include_hidden: bool = False) -> List[Category]:
        """Get all categories.
        
        Args:
            db: Database session
            include_hidden: Whether to include hidden categories
            
        Returns:
            List of categories
        """
        query = db.query(Category)
        
        if not include_hidden:
            query = query.filter(Category.is_hidden == False)
        
        return query.order_by(Category.name).all()
    
    def update(self, db: Session, category_id: int, data: CategoryUpdate) -> Optional[Category]:
        """Update a category.
        
        Args:
            db: Database session
            category_id: Category ID
            data: Category update data
            
        Returns:
            Updated category or None if not found
        """
        db_category = self.get_by_id(db, category_id)
        
        if not db_category:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Generate slug if name is being updated but slug is not provided
        if "name" in update_data and "slug" not in update_data:
            update_data["slug"] = generate_slug(update_data["name"])
        
        for field, value in update_data.items():
            setattr(db_category, field, value)
        
        db.commit()
        db.refresh(db_category)
        
        return db_category
    
    def delete(self, db: Session, category_id: int) -> bool:
        """Delete a category.
        
        Args:
            db: Database session
            category_id: Category ID
            
        Returns:
            True if deleted, False if not found
        """
        db_category = self.get_by_id(db, category_id)
        
        if not db_category:
            return False
        
        db.delete(db_category)
        db.commit()
        
        return True
    
    def count(self, db: Session) -> int:
        """Count total categories.
        
        Args:
            db: Database session
            
        Returns:
            Total number of categories
        """
        return db.query(Category).count()
