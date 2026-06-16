"""User schemas for request/response validation."""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from .enums import UserRole


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., min_length=1, max_length=255, description="User full name")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, description="User password")
    role: UserRole = Field(default=UserRole.VIEWER, description="User role")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "password": "securepass123",
                "role": "viewer"
            }
        }
    }


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = Field(None, description="User email address")
    full_name: Optional[str] = Field(None, min_length=1, max_length=255, description="User full name")
    password: Optional[str] = Field(None, min_length=8, description="New password")
    role: Optional[UserRole] = Field(None, description="User role")
    is_active: Optional[bool] = Field(None, description="Whether user is active")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength."""
        if v is not None:
            if len(v) < 8:
                raise ValueError('Password must be at least 8 characters long')
            if not any(char.isdigit() for char in v):
                raise ValueError('Password must contain at least one digit')
            if not any(char.isalpha() for char in v):
                raise ValueError('Password must contain at least one letter')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "newemail@example.com",
                "full_name": "John Smith",
                "role": "editor"
            }
        }
    }


class UserResponse(UserBase):
    """Schema for user response."""
    id: int = Field(..., description="User ID")
    role: UserRole = Field(..., description="User role")
    is_active: bool = Field(..., description="Whether user is active")
    created_at: datetime = Field(..., description="User creation timestamp")
    updated_at: datetime = Field(..., description="User last update timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "full_name": "John Doe",
                "role": "viewer",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
    }


class UserListResponse(BaseModel):
    """Schema for user list response with pagination."""
    users: list[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Number of items per page")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "users": [
                    {
                        "id": 1,
                        "email": "user@example.com",
                        "full_name": "John Doe",
                        "role": "viewer",
                        "is_active": True,
                        "created_at": "2024-01-01T00:00:00",
                        "updated_at": "2024-01-01T00:00:00"
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 10
            }
        }
    }
