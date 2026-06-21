"""Category router."""

import logging
from fastapi import APIRouter, Depends, status, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..users.models import User
from ..auth.dependencies import get_current_active_user, get_optional_current_user
from ..exceptions import NotFoundException, ForbiddenException
from .schemas import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse
from .service import CategoryService
from .dependencies import get_category_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get(
    "/",
    response_model=CategoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Categories",
    description="Get list of all categories"
)
def list_categories(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
    service: CategoryService = Depends(get_category_service)
) -> CategoryListResponse:
    return service.get_categories(db, current_user)


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Category",
    description="Get category by ID"
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user),
    service: CategoryService = Depends(get_category_service)
) -> CategoryResponse:
    return service.get_category(db, category_id)


@router.get(
    "/slug/{slug}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Category by Slug",
    description="Get category by slug"
)
def get_category_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user),
    service: CategoryService = Depends(get_category_service)
) -> CategoryResponse:
    return service.get_category_by_slug(db, slug)


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Category",
    description="Create a new category (admin/editor only)"
)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    service: CategoryService = Depends(get_category_service)
) -> CategoryResponse:
    return service.create_category(db, data, current_user)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Category",
    description="Update a category (admin/editor only)"
)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    service: CategoryService = Depends(get_category_service)
) -> CategoryResponse:
    return service.update_category(db, category_id, data, current_user)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Category",
    description="Delete a category (admin only)"
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    service: CategoryService = Depends(get_category_service)
) -> None:
    service.delete_category(db, category_id, current_user)


@router.post(
    "/{category_id}/image",
    summary="Upload Category Image",
    description="Upload an image for a category (admin/editor only)"
)
async def upload_category_image(
    category_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    service: CategoryService = Depends(get_category_service)
) -> dict:
    """Upload category image."""
    try:
        file_bytes = await file.read()
        result = service.update_category_image(
            db=db,
            category_id=category_id,
            file_bytes=file_bytes,
            original_filename=file.filename,
            current_user=current_user
        )
        return {
            "success": True,
            "image_url": result,
            "message": "Изображение загружено"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    except ForbiddenException:
        raise HTTPException(status_code=403, detail="Нет прав на редактирование")


@router.get(
    "/{category_id}/image",
    summary="Get Category Image",
    description="Serve the category image file"
)
async def get_category_image(
    category_id: int,
    db: Session = Depends(get_db),
    service: CategoryService = Depends(get_category_service)
) -> FileResponse:
    """Return the category image file."""
    file_path = service.get_category_image(db, category_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="Изображение не найдено")
    return FileResponse(
        path=file_path,
        media_type="image/webp",
        filename=f"category-{category_id}.webp"
    )
