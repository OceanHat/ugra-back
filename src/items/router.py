"""Item router."""

import logging
from fastapi import APIRouter, Depends, status, Query, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from ..dependencies import get_db
from ..users.models import User
from ..auth.dependencies import get_current_active_user, get_optional_current_user
from ..exceptions import NotFoundException, ConflictException, ForbiddenException, BadRequestException
from .schemas import ItemCreate, ItemUpdate, ItemResponse, ItemListResponse
from .service import ItemService
from .dependencies import get_item_service
from .constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/items", tags=["items"])


@router.get(
    "/",
    response_model=ItemListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Items",
    description="Get list of items with pagination and filtering"
)
def list_items(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Maximum number of records to return"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user),
    service: ItemService = Depends(get_item_service)
) -> ItemListResponse:
    """List all items with pagination and filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        category_id: Filter by category ID
        db: Database session
        current_user: Current authenticated user
        service: Item service
        
    Returns:
        List of items with pagination info
    """
    return service.get_items(db, skip=skip, limit=limit, category_id=category_id, current_user=current_user)


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Item",
    description="Get item by ID"
)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user),
    service: ItemService = Depends(get_item_service)
) -> ItemResponse:
    """Get item by ID.
    
    Args:
        item_id: Item ID
        db: Database session
        current_user: Current authenticated user
        service: Item service
        
    Returns:
        Item data
    """
    return service.get_item(db, item_id)


@router.get(
    "/slug/{slug}",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Item by Slug",
    description="Get item by slug"
)
def get_item_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user),
    service: ItemService = Depends(get_item_service)
) -> ItemResponse:
    """Get item by slug.
    
    Args:
        slug: Item slug
        db: Database session
        current_user: Current authenticated user
        service: Item service
        
    Returns:
        Item data
    """
    return service.get_item_by_slug(db, slug)


@router.post(
    "/",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Item",
    description="Create a new item (admin/editor only)"
)
def create_item(
    data: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    service: ItemService = Depends(get_item_service)
) -> ItemResponse:
    """Create a new item.
    
    Args:
        data: Item creation data
        db: Database session
        current_user: Current authenticated user
        service: Item service
        
    Returns:
        Created item
    """
    return service.create_item(db, data, current_user)


@router.put(
    "/{item_id}",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Item",
    description="Update an item (admin/editor only)"
)
def update_item(
    item_id: int,
    data: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    service: ItemService = Depends(get_item_service)
) -> ItemResponse:
    """Update an item.
    
    Args:
        item_id: Item ID
        data: Item update data
        db: Database session
        current_user: Current authenticated user
        service: Item service
        
    Returns:
        Updated item
    """
    return service.update_item(db, item_id, data, current_user)


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Item",
    description="Delete an item (admin only)"
)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    service: ItemService = Depends(get_item_service)
) -> None:
    """Delete an item.
    
    Args:
        item_id: Item ID
        db: Database session
        current_user: Current authenticated user
        service: Item service
    """
    service.delete_item(db, item_id, current_user)


@router.post("/{item_id}/image")
async def upload_item_image(
    item_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """Загрузить изображение товара"""
    try:
        service = ItemService()
        file_bytes = await file.read()
        
        result = service.update_item_image(
            db=db,
            item_id=item_id,
            file_bytes=file_bytes,
            original_filename=file.filename,
            current_user=current_user
        )
        
        return {
            "success": True,
            "picture_url": result,
            "message": "Изображение загружено"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Товар не найден")
    except ForbiddenException:
        raise HTTPException(status_code=403, detail="Нет прав на редактирование")


@router.get("/{item_id}/image")
async def get_item_image(
    item_id: int,
    size: str = Query("full", regex="^(thumbnail|full)$"),
    db: Session = Depends(get_db)
) -> FileResponse:
    """Получить изображение товара (thumbnail или full)"""
    service = ItemService()
    
    file_path = service.get_item_image(
        db=db,
        item_id=item_id,
        size=size
    )
    
    if not file_path:
        raise HTTPException(status_code=404, detail="Изображение не найдено")
    
    return FileResponse(
        path=file_path,
        media_type="image/webp",
        filename=f"item-{item_id}-{size}.webp"
    )


@router.delete("/{item_id}/image")
async def delete_item_image(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """Удалить изображение товара"""
    try:
        service = ItemService()
        service.delete_item_image(
            db=db,
            item_id=item_id,
            current_user=current_user
        )
        
        return {
            "success": True,
            "message": "Изображение удалено"
        }
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Товар не найден")
    except ForbiddenException:
        raise HTTPException(status_code=403, detail="Нет прав на редактирование")