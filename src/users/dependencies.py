"""User dependencies."""

from fastapi import Depends
from .repository import UserRepository, IUserRepository
from .service import UserService


def get_user_repository() -> IUserRepository:
    """Get user repository instance.
    
    Returns:
        User repository
    """
    return UserRepository()


def get_user_service(
    repository: IUserRepository = Depends(get_user_repository)
) -> UserService:
    """Get user service instance.
    
    Args:
        repository: User repository
        
    Returns:
        User service
    """
    return UserService(repository=repository)
