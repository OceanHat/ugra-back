"""Item service for business logic."""

import logging
import json
from typing import Optional
from pathlib import Path
from sqlalchemy.orm import Session
from .repository import IItemRepository, ItemRepository
from .schemas import ItemCreate, ItemUpdate, ItemResponse, ItemListResponse
from ..users.models import User
from ..users.enums import UserRole
from ..categories.repository import CategoryRepository
from ..exceptions import NotFoundException, ConflictException, ForbiddenException, BadRequestException
from ..core.images.storage import ImageStorageManager

logger = logging.getLogger(__name__)


class ItemService:
    """Item service implementing business logic."""
    
    def __init__(self, repository: IItemRepository = None):
        """Initialize service with repository.
        
        Args:
            repository: Item repository instance
        """
        self.repository = repository or ItemRepository()
        self.category_repo = CategoryRepository()
        self.storage = ImageStorageManager()
    
    def _parse_additional_data(self, item: any) -> dict:
        """Parse additional_data JSON string to dict.
        
        Args:
            item: Item model instance
            
        Returns:
            Parsed additional_data as dict or None
        """
        if item.additional_data:
            try:
                return json.loads(item.additional_data)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse additional_data for item {item.id}")
                return None
        return None
    
    def create_item(self, db: Session, data: ItemCreate, current_user: User) -> ItemResponse:
        """Create a new item.
        
        Args:
            db: Database session
            data: Item creation data
            current_user: User making the request
            
        Returns:
            Created item
            
        Raises:
            ForbiddenException: If user doesn't have permission
            NotFoundException: If category not found
            ConflictException: If slug already exists
        """
        # Only admins and editors can create items
        if current_user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
            logger.warning(f"User {current_user.id} attempted to create item without permission")
            raise ForbiddenException("Only administrators and editors can create items")
        
        # Verify category exists
        category = self.category_repo.get_by_id(db, data.category_id)
        if not category:
            raise NotFoundException(f"Category with ID {data.category_id} not found")
        
        # Check if slug already exists
        slug = data.slug if data.slug else data.name.lower().replace(' ', '-')
        existing = self.repository.get_by_slug(db, slug)
        if existing:
            logger.warning(f"Attempted to create item with existing slug: {slug}")
            raise ConflictException(f"Item with slug '{slug}' already exists")
        
        item = self.repository.create(db, data, current_user.id)
        logger.info(f"Item created: {item.id} by user {current_user.id}")
        
        # Parse additional_data for response
        item_dict = ItemResponse.model_validate(item).model_dump()
        item_dict['additional_data'] = self._parse_additional_data(item)
        return ItemResponse(**item_dict)
    
    def get_item(self, db: Session, item_id: int) -> ItemResponse:
        """Get item by ID.
        
        Args:
            db: Database session
            item_id: Item ID
            
        Returns:
            Item data
            
        Raises:
            NotFoundException: If item not found
        """
        item = self.repository.get_by_id(db, item_id)
        
        if not item:
            logger.warning(f"Item not found: {item_id}")
            raise NotFoundException(f"Item with ID {item_id} not found")
        
        item_dict = ItemResponse.model_validate(item).model_dump()
        item_dict['additional_data'] = self._parse_additional_data(item)
        return ItemResponse(**item_dict)
    
    def get_item_by_slug(self, db: Session, slug: str) -> ItemResponse:
        """Get item by slug.
        
        Args:
            db: Database session
            slug: Item slug
            
        Returns:
            Item data
            
        Raises:
            NotFoundException: If item not found
        """
        item = self.repository.get_by_slug(db, slug)
        
        if not item:
            logger.warning(f"Item not found: {slug}")
            raise NotFoundException(f"Item with slug '{slug}' not found")
        
        item_dict = ItemResponse.model_validate(item).model_dump()
        item_dict['additional_data'] = self._parse_additional_data(item)
        return ItemResponse(**item_dict)
    
    def get_items(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
        category_id: Optional[int] = None,
        current_user: User = None
    ) -> ItemListResponse:
        """Get all items with pagination and filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            category_id: Filter by category ID
            current_user: User making the request (optional)
            
        Returns:
            List of items with pagination info
        """
        # Admins and editors can see hidden items
        include_hidden = current_user and current_user.role in [UserRole.ADMIN, UserRole.EDITOR]
        
        items = self.repository.get_all(db, skip=skip, limit=limit, category_id=category_id, include_hidden=include_hidden)
        total = self.repository.count(db, category_id=category_id, include_hidden=include_hidden)
        
        # Parse additional_data for each item
        item_responses = []
        for item in items:
            item_dict = ItemResponse.model_validate(item).model_dump()
            item_dict['additional_data'] = self._parse_additional_data(item)
            item_responses.append(ItemResponse(**item_dict))
        
        return ItemListResponse(
            items=item_responses,
            total=total,
            skip=skip,
            limit=limit
        )
    
    def update_item(self, db: Session, item_id: int, data: ItemUpdate, current_user: User) -> ItemResponse:
        """Update an item.
        
        Args:
            db: Database session
            item_id: Item ID
            data: Item update data
            current_user: User making the request
            
        Returns:
            Updated item
            
        Raises:
            ForbiddenException: If user doesn't have permission
            NotFoundException: If item or category not found
            ConflictException: If slug already exists
        """
        # Only admins and editors can update items
        if current_user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
            logger.warning(f"User {current_user.id} attempted to update item without permission")
            raise ForbiddenException("Only administrators and editors can update items")
        
        # Verify category exists if being changed
        if data.category_id is not None:
            category = self.category_repo.get_by_id(db, data.category_id)
            if not category:
                raise NotFoundException(f"Category with ID {data.category_id} not found")
        
        # Check if slug is being changed and already exists
        if data.slug:
            existing = self.repository.get_by_slug(db, data.slug)
            if existing and existing.id != item_id:
                logger.warning(f"Attempted to update item with existing slug: {data.slug}")
                raise ConflictException(f"Item with slug '{data.slug}' already exists")
        
        item = self.repository.update(db, item_id, data, current_user.id)
        
        if not item:
            logger.warning(f"Item not found for update: {item_id}")
            raise NotFoundException(f"Item with ID {item_id} not found")
        
        logger.info(f"Item updated: {item_id} by user {current_user.id}")
        
        item_dict = ItemResponse.model_validate(item).model_dump()
        item_dict['additional_data'] = self._parse_additional_data(item)
        return ItemResponse(**item_dict)
    
    def delete_item(self, db: Session, item_id: int, current_user: User) -> None:
        """Delete an item.
        
        Args:
            db: Database session
            item_id: Item ID
            current_user: User making the request
            
        Raises:
            ForbiddenException: If user doesn't have permission
            NotFoundException: If item not found
        """
        # Only admins can delete items
        if current_user.role != UserRole.ADMIN:
            logger.warning(f"User {current_user.id} attempted to delete item without permission")
            raise ForbiddenException("Only administrators can delete items")
        
        deleted = self.repository.delete(db, item_id)
        
        if not deleted:
            logger.warning(f"Item not found for deletion: {item_id}")
            raise NotFoundException(f"Item with ID {item_id} not found")
        
        logger.info(f"Item deleted: {item_id} by admin {current_user.id}")

    
    def update_item_image(
        self,
        db: Session,
        item_id: int,
        file_bytes: bytes,
        original_filename: str,
        current_user: User
    ) -> str:
        """Загрузить новое изображение для товара"""
        
        # Проверка прав
        if current_user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
            raise ForbiddenException("Только администраторы могут загружать изображения")
        
        # Получаем товар
        item = self.repository.get_by_id(db, item_id)
        if not item:
            raise NotFoundException(f"Item with ID {item_id} not found")
        
        # Сохраняем новое изображение (старое удалится автоматически)
        try:
            new_picture_url = self.storage.replace_item_image(
                old_picture_url=item.picture_url,
                new_file_bytes=file_bytes,
                original_filename=original_filename
            )
            
            data = ItemUpdate(
                picture_url=new_picture_url
            )
            # Обновляем в БД
            self.repository.update(db, item_id, data, current_user.id)
            
            logger.info(f"Image updated for item {item_id} by user {current_user.id}")
            
            return new_picture_url
            
        except ValueError as e:
            raise ValueError(str(e))
    
    def get_item_image(
        self,
        db: Session,
        item_id: int,
        size: str = "full"
    ) -> Optional[Path]:
        """Получить путь до изображения товара"""
        
        item = self.repository.get_by_id(db, item_id)
        if not item or not item.picture_url:
            return None
        
        return self.storage.get_image_path(item.picture_url, size=size)
    
    def delete_item_image(
        self,
        db: Session,
        item_id: int,
        current_user: User
    ) -> None:
        """Удалить изображение товара"""
        
        # Проверка прав
        if current_user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
            raise ForbiddenException("Только администраторы могут удалять изображения")
        
        item = self.repository.get_by_id(db, item_id)
        if not item:
            raise NotFoundException(f"Item with ID {item_id} not found")
        
        # Удаляем файлы
        if item.picture_url:
            self.storage.delete_item_image(item.picture_url)
            
            # Обновляем в БД
            self.repository.update(db, item_id, {"picture_url": None})
            
            logger.info(f"Image deleted for item {item_id} by user {current_user.id}")
    
    def delete_item(self, db: Session, item_id: int, current_user: User) -> None:
        """Удалить товар (включая изображение)"""
        
        item = self.repository.get_by_id(db, item_id)
        if not item:
            raise NotFoundException(f"Item with ID {item_id} not found")
        
        # Проверка прав
        if current_user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
            raise ForbiddenException("Only administrators can delete items")
        
        # Удаляем изображение
        if item.picture_url:
            self.storage.delete_item_image(item.picture_url)
        
        # Удаляем товар из БД
        self.repository.delete(db, item_id)
        
        logger.info(f"Item {item_id} deleted by user {current_user.id}")