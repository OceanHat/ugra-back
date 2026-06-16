"""Category dependencies."""

from fastapi import Depends
from .repository import CategoryRepository, ICategoryRepository
from .service import CategoryService


def get_category_repository() -> ICategoryRepository:
    """Get category repository instance.
    
    Returns:
        Category repository
    """
    return CategoryRepository()


def get_category_service(
    repository: ICategoryRepository = Depends(get_category_repository)
) -> CategoryService:
    """Get category service instance.
    
    Args:
        repository: Category repository
        
    Returns:
        Category service
    """
    return CategoryService(repository=repository)
