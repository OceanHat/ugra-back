"""Category repository for database operations."""

from typing import Optional, List, Protocol
from sqlalchemy.orm import Session
from .models import Category
from .schemas import CategoryCreate, CategoryUpdate
from ..core.slug import generate_slug


class ICategoryRepository(Protocol):
    """Interface for category repository."""

    def create(self, db: Session, data: CategoryCreate, user_id: int) -> Category: ...
    def get_by_id(self, db: Session, category_id: int) -> Optional[Category]: ...
    def get_by_slug(self, db: Session, slug: str) -> Optional[Category]: ...
    def get_all(self, db: Session, include_hidden: bool = False) -> List[Category]: ...
    def update(self, db: Session, category_id: int, data: CategoryUpdate) -> Optional[Category]: ...
    def delete(self, db: Session, category_id: int) -> bool: ...
    def count(self, db: Session) -> int: ...


class CategoryRepository:
    """Concrete implementation of category repository."""

    def create(self, db: Session, data: CategoryCreate, user_id: int) -> Category:
        slug = data.slug if data.slug else generate_slug(data.name)

        db_category = Category(
            name=data.name,
            slug=slug,
            description=data.description,
            is_hidden=data.is_hidden,
            created_by_id=user_id,
        )
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category

    def get_by_id(self, db: Session, category_id: int) -> Optional[Category]:
        return db.query(Category).filter(Category.id == category_id).first()

    def get_by_slug(self, db: Session, slug: str) -> Optional[Category]:
        return db.query(Category).filter(Category.slug == slug).first()

    def get_all(self, db: Session, include_hidden: bool = False) -> List[Category]:
        query = db.query(Category)
        if not include_hidden:
            query = query.filter(Category.is_hidden == False)
        return query.order_by(Category.name).all()

    def update(self, db: Session, category_id: int, data: CategoryUpdate) -> Optional[Category]:
        db_category = self.get_by_id(db, category_id)
        if not db_category:
            return None

        update_data = data.model_dump(exclude_unset=True)

        if "name" in update_data and "slug" not in update_data:
            update_data["slug"] = generate_slug(update_data["name"])

        for field, value in update_data.items():
            setattr(db_category, field, value)

        db.commit()
        db.refresh(db_category)
        return db_category

    def delete(self, db: Session, category_id: int) -> bool:
        db_category = self.get_by_id(db, category_id)
        if not db_category:
            return False
        db.delete(db_category)
        db.commit()
        return True

    def count(self, db: Session) -> int:
        return db.query(Category).count()
