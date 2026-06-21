"""Category service for business logic."""

import logging
from typing import List, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from .repository import ICategoryRepository, CategoryRepository
from .schemas import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse
from ..users.models import User
from ..users.enums import UserRole
from ..exceptions import NotFoundException, ConflictException, ForbiddenException
from ..core.images.storage import ImageStorageManager

logger = logging.getLogger(__name__)


class CategoryService:
    """Category service implementing business logic."""

    def __init__(self, repository: ICategoryRepository = None):
        self.repository = repository or CategoryRepository()
        self.storage = ImageStorageManager()

    def create_category(self, db: Session, data: CategoryCreate, current_user: User) -> CategoryResponse:
        if current_user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
            raise ForbiddenException("Only administrators and editors can create categories")

        slug = data.slug if data.slug else data.name.lower().replace(' ', '-')
        existing = self.repository.get_by_slug(db, slug)
        if existing:
            raise ConflictException(f"Category with slug '{slug}' already exists")

        category = self.repository.create(db, data, current_user.id)
        logger.info(f"Category created: {category.id} by user {current_user.id}")
        return CategoryResponse.model_validate(category)

    def get_category(self, db: Session, category_id: int) -> CategoryResponse:
        category = self.repository.get_by_id(db, category_id)
        if not category:
            raise NotFoundException(f"Category with ID {category_id} not found")
        return CategoryResponse.model_validate(category)

    def get_category_by_slug(self, db: Session, slug: str) -> CategoryResponse:
        category = self.repository.get_by_slug(db, slug)
        if not category:
            raise NotFoundException(f"Category with slug '{slug}' not found")
        return CategoryResponse.model_validate(category)

    def get_categories(self, db: Session, current_user: User = None) -> CategoryListResponse:
        include_hidden = current_user and current_user.role in [UserRole.ADMIN, UserRole.EDITOR]
        categories = self.repository.get_all(db, include_hidden=include_hidden)
        return CategoryListResponse(
            categories=[CategoryResponse.model_validate(cat) for cat in categories],
            total=len(categories)
        )

    def update_category(self, db: Session, category_id: int, data: CategoryUpdate, current_user: User) -> CategoryResponse:
        if current_user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
            raise ForbiddenException("Only administrators and editors can update categories")

        if data.slug:
            existing = self.repository.get_by_slug(db, data.slug)
            if existing and existing.id != category_id:
                raise ConflictException(f"Category with slug '{data.slug}' already exists")

        category = self.repository.update(db, category_id, data)
        if not category:
            raise NotFoundException(f"Category with ID {category_id} not found")

        logger.info(f"Category updated: {category_id} by user {current_user.id}")
        return CategoryResponse.model_validate(category)

    def delete_category(self, db: Session, category_id: int, current_user: User) -> None:
        if current_user.role != UserRole.ADMIN:
            raise ForbiddenException("Only administrators can delete categories")

        deleted = self.repository.delete(db, category_id)
        if not deleted:
            raise NotFoundException(f"Category with ID {category_id} not found")

        logger.info(f"Category deleted: {category_id} by admin {current_user.id}")

    # ------------------------------------------------------------------ images

    def update_category_image(
        self,
        db: Session,
        category_id: int,
        file_bytes: bytes,
        original_filename: str,
        current_user: User,
    ) -> str:
        """Upload / replace the category image.

        Returns the new storage key (image_url).
        """
        if current_user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
            raise ForbiddenException("Только администраторы могут загружать изображения")

        category = self.repository.get_by_id(db, category_id)
        if not category:
            raise NotFoundException(f"Category with ID {category_id} not found")

        new_image_url = self.storage.replace_item_image(
            old_picture_url=category.image_url,
            new_file_bytes=file_bytes,
            original_filename=original_filename,
        )

        self.repository.update(db, category_id, CategoryUpdate(image_url=new_image_url))
        logger.info(f"Image updated for category {category_id} by user {current_user.id}")
        return new_image_url

    def get_category_image(
        self,
        db: Session,
        category_id: int,
        size: str = "full",
    ) -> Optional[Path]:
        """Return the filesystem path for the category image."""
        category = self.repository.get_by_id(db, category_id)
        if not category or not category.image_url:
            return None
        return self.storage.get_image_path(category.image_url, size=size)
