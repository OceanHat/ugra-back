"""Custom exception classes for the application."""

from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Base exception for all API exceptions."""
    
    def __init__(self, detail: str = None, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(status_code=status_code, detail=detail or self.default_detail)
    
    default_detail = "An error occurred"


class NotFoundException(BaseAPIException):
    """Exception raised when a resource is not found."""
    default_detail = "Resource not found"
    
    def __init__(self, detail: str = None):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class UnauthorizedException(BaseAPIException):
    """Exception raised when authentication fails."""
    default_detail = "Authentication failed"
    
    def __init__(self, detail: str = None):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(BaseAPIException):
    """Exception raised when user doesn't have permission."""
    default_detail = "You don't have permission to perform this action"
    
    def __init__(self, detail: str = None):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class BadRequestException(BaseAPIException):
    """Exception raised for invalid requests."""
    default_detail = "Invalid request"
    
    def __init__(self, detail: str = None):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class ConflictException(BaseAPIException):
    """Exception raised when there's a conflict (e.g., duplicate resource)."""
    default_detail = "Resource already exists"
    
    def __init__(self, detail: str = None):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class ValidationException(BaseAPIException):
    """Exception raised for validation errors."""
    default_detail = "Validation error"
    
    def __init__(self, detail: str = None):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
