"""Category router."""

import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..users.models import User
from ..auth.dependencies import get_current_active_user, get_optional_current_user
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
    """List all categories.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        service: Category service
        
    Returns:
        List of categories
    """
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
    """Get category by ID.
    
    Args:
        category_id: Category ID
        db: Database session
        current_user: Current authenticated user
        service: Category service
        
    Returns:
        Category data
    """
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
    """Get category by slug.
    
    Args:
        slug: Category slug
        db: Database session
        current_user: Current authenticated user
        service: Category service
        
    Returns:
        Category data
    """
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
    """Create a new category.
    
    Args:
        data: Category creation data
        db: Database session
        current_user: Current authenticated user
        service: Category service
        
    Returns:
        Created category
    """
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
    """Update a category.
    
    Args:
        category_id: Category ID
        data: Category update data
        db: Database session
        current_user: Current authenticated user
        service: Category service
        
    Returns:
        Updated category
    """
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
    """Delete a category.
    
    Args:
        category_id: Category ID
        db: Database session
        current_user: Current authenticated user
        service: Category service
    """
    service.delete_category(db, category_id, current_user)
