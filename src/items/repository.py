"""Item repository for database operations."""

import json
import re
from typing import Optional, List, Protocol
from sqlalchemy.orm import Session
from sqlalchemy import or_
from .models import Item
from .schemas import ItemCreate, ItemUpdate
from ..core.slug import generate_slug


class IItemRepository(Protocol):
    """Interface for item repository."""

    def create(self, db: Session, data: ItemCreate, user_id: int) -> Item: ...
    def get_by_id(self, db: Session, item_id: int) -> Optional[Item]: ...
    def get_by_slug(self, db: Session, slug: str) -> Optional[Item]: ...
    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        include_hidden: bool = False,
    ) -> List[Item]: ...
    def update(self, db: Session, item_id: int, data: ItemUpdate, user_id: int) -> Optional[Item]: ...
    def delete(self, db: Session, item_id: int) -> bool: ...
    def count(self, db: Session, category_id: Optional[int] = None, include_hidden: bool = False) -> int: ...


class ItemRepository:
    """Concrete implementation of item repository."""

    def create(self, db: Session, data: ItemCreate, user_id: int) -> Item:
        slug = data.slug if data.slug else generate_slug(data.name)

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
            created_by_id=user_id,
        )

        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    def get_by_id(self, db: Session, item_id: int) -> Optional[Item]:
        return db.query(Item).filter(Item.id == item_id).first()

    def get_by_slug(self, db: Session, slug: str) -> Optional[Item]:
        return db.query(Item).filter(Item.slug == slug).first()

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        include_hidden: bool = False,
    ) -> List[Item]:
        query = db.query(Item)
        if category_id is not None:
            query = query.filter(Item.category_id == category_id)
        if not include_hidden:
            query = query.filter(Item.is_hidden == False)
        return query.order_by(Item.created_at.desc()).offset(skip).limit(limit).all()

    def update(self, db: Session, item_id: int, data: ItemUpdate, user_id: int) -> Optional[Item]:
        db_item = self.get_by_id(db, item_id)
        if not db_item:
            return None

        update_data = data.model_dump(exclude_unset=True)

        if "name" in update_data and "slug" not in update_data:
            update_data["slug"] = generate_slug(update_data["name"])

        if "additional_data" in update_data:
            update_data["additional_data"] = (
                json.dumps(update_data["additional_data"])
                if update_data["additional_data"] is not None
                else None
            )

        update_data["updated_by_id"] = user_id

        for field, value in update_data.items():
            setattr(db_item, field, value)

        db.commit()
        db.refresh(db_item)
        return db_item

    def delete(self, db: Session, item_id: int) -> bool:
        db_item = self.get_by_id(db, item_id)
        if not db_item:
            return False
        db.delete(db_item)
        db.commit()
        return True

    def count(self, db: Session, category_id: Optional[int] = None, include_hidden: bool = False) -> int:
        query = db.query(Item)
        if category_id is not None:
            query = query.filter(Item.category_id == category_id)
        if not include_hidden:
            query = query.filter(Item.is_hidden == False)
        return query.count()
