"""Item repository for database operations."""

import json
import re
from typing import Optional, List, Protocol
from sqlalchemy.orm import Session
from sqlalchemy import or_
from .models import Item
from .schemas import ItemCreate, ItemUpdate


def generate_slug(name: str) -> str:
    """Generate URL-friendly slug from name.
    
    Args:
        name: Item name
        
    Returns:
        URL-friendly slug
    """
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = slug.strip('-')
    return slug


class IItemRepository(Protocol):
    """Interface for item repository."""
    
    def create(self, db: Session, data: ItemCreate, user_id: int) -> Item:
        """Create a new item."""
        ...
    
    def get_by_id(self, db: Session, item_id: int) -> Optional[Item]:
        """Get item by ID."""
        ...
    
    def get_by_slug(self, db: Session, slug: str) -> Optional[Item]:
        """Get item by slug."""
        ...
    
    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        include_hidden: bool = False
    ) -> List[Item]:
        """Get all items with filtering."""
        ...
    
    def update(self, db: Session, item_id: int, data: ItemUpdate, user_id: int) -> Optional[Item]:
        """Update an item."""
        ...
    
    def delete(self, db: Session, item_id: int) -> bool:
        """Delete an item."""
        ...
    
    def count(self, db: Session, category_id: Optional[int] = None, include_hidden: bool = False) -> int:
        """Count total items."""
        ...


class ItemRepository:
    """Concrete implementation of item repository."""
    
    def create(self, db: Session, data: ItemCreate, user_id: int) -> Item:
        """Create a new item.
        
        Args:
            db: Database session
            data: Item creation data
            user_id: ID of user creating the item
            
        Returns:
            Created item
        """
        slug = data.slug if data.slug else generate_slug(data.name)
        
        # Serialize additional_data to JSON string
        additional_data_str = None
        if data.additional_data:
            additional_data_str = json.dumps(data.additional_data)
        
        db_item = Item(
            name=data.name,
            slug=slug,
            picture_url=data.picture_url,
            description=data.description,
            category_id=data.category_id,
            is_hidden=data.is_hidden,
            additional_data=additional_data_str,
            created_by_id=user_id
        )
        
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        return db_item
    
    def get_by_id(self, db: Session, item_id: int) -> Optional[Item]:
        """Get item by ID.
        
        Args:
            db: Database session
            item_id: Item ID
            
        Returns:
            Item or None if not found
        """
        return db.query(Item).filter(Item.id == item_id).first()
    
    def get_by_slug(self, db: Session, slug: str) -> Optional[Item]:
        """Get item by slug.
        
        Args:
            db: Database session
            slug: Item slug
            
        Returns:
            Item or None if not found
        """
        return db.query(Item).filter(Item.slug == slug).first()
    
    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        include_hidden: bool = False
    ) -> List[Item]:
        """Get all items with filtering and pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            category_id: Filter by category ID
            include_hidden: Whether to include hidden items
            
        Returns:
            List of items
        """
        query = db.query(Item)
        
        if category_id is not None:
            query = query.filter(Item.category_id == category_id)
        
        if not include_hidden:
            query = query.filter(Item.is_hidden == False)
        
        return query.order_by(Item.created_at.desc()).offset(skip).limit(limit).all()
    
    def update(self, db: Session, item_id: int, data: ItemUpdate, user_id: int) -> Optional[Item]:
        """Update an item.
        
        Args:
            db: Database session
            item_id: Item ID
            data: Item update data
            user_id: ID of user updating the item
            
        Returns:
            Updated item or None if not found
        """
        db_item = self.get_by_id(db, item_id)
        
        if not db_item:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Generate slug if name is being updated but slug is not provided
        if "name" in update_data and "slug" not in update_data:
            update_data["slug"] = generate_slug(update_data["name"])
        
        # Serialize additional_data to JSON string
        if "additional_data" in update_data:
            if update_data["additional_data"] is not None:
                update_data["additional_data"] = json.dumps(update_data["additional_data"])
            else:
                update_data["additional_data"] = None
        
        # Set updated_by_id
        update_data["updated_by_id"] = user_id
        
        for field, value in update_data.items():
            setattr(db_item, field, value)
        
        db.commit()
        db.refresh(db_item)
        
        return db_item
    
    def delete(self, db: Session, item_id: int) -> bool:
        """Delete an item.
        
        Args:
            db: Database session
            item_id: Item ID
            
        Returns:
            True if deleted, False if not found
        """
        db_item = self.get_by_id(db, item_id)
        
        if not db_item:
            return False
        
        db.delete(db_item)
        db.commit()
        
        return True
    
    def count(self, db: Session, category_id: Optional[int] = None, include_hidden: bool = False) -> int:
        """Count total items.
        
        Args:
            db: Database session
            category_id: Filter by category ID
            include_hidden: Whether to include hidden items
            
        Returns:
            Total number of items
        """
        query = db.query(Item)
        
        if category_id is not None:
            query = query.filter(Item.category_id == category_id)
        
        if not include_hidden:
            query = query.filter(Item.is_hidden == False)
        
        return query.count()
