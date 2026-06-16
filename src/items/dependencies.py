"""Item dependencies."""

from fastapi import Depends
from .repository import ItemRepository, IItemRepository
from .service import ItemService


def get_item_repository() -> IItemRepository:
    """Get item repository instance.
    
    Returns:
        Item repository
    """
    return ItemRepository()


def get_item_service(
    repository: IItemRepository = Depends(get_item_repository)
) -> ItemService:
    """Get item service instance.
    
    Args:
        repository: Item repository
        
    Returns:
        Item service
    """
    return ItemService(repository=repository)
