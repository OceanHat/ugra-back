"""Category schemas for request/response validation."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class CategoryBase(BaseModel):
    """Base category schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255, description="Category name")
    description: Optional[str] = Field(None, description="Category description")


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""
    slug: Optional[str] = Field(None, max_length=255, description="URL-friendly slug (auto-generated if not provided)")
    is_hidden: bool = Field(default=False, description="Whether category is hidden")
    
    @field_validator('slug')
    def validate_slug(cls, v):
        """Validate slug format."""
        if v is not None:
            if not re.match(r'^[a-z0-9-]+$', v):
                raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Mineral",
                "description": "Mineral related items",
                "slug": "mineral",
                "is_hidden": False
            }
        }
    }


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Category name")
    slug: Optional[str] = Field(None, max_length=255, description="URL-friendly slug")
    description: Optional[str] = Field(None, description="Category description")
    is_hidden: Optional[bool] = Field(None, description="Whether category is hidden")
    
    @field_validator('slug')
    def validate_slug(cls, v):
        """Validate slug format."""
        if v is not None:
            if not re.match(r'^[a-z0-9-]+$', v):
                raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Mineral & Rock",
                "description": "Updated description"
            }
        }
    }


class CategoryResponse(CategoryBase):
    """Schema for category response."""
    id: int = Field(..., description="Category ID")
    slug: str = Field(..., description="URL-friendly slug")
    is_hidden: bool = Field(..., description="Whether category is hidden")
    created_by_id: Optional[int] = Field(None, description="User ID who created the category")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Mineral",
                "slug": "mineral",
                "description": "Mineral related items",
                "is_hidden": False,
                "created_by_id": 1,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
    }


class CategoryListResponse(BaseModel):
    """Schema for category list response."""
    categories: list[CategoryResponse] = Field(..., description="List of categories")
    total: int = Field(..., description="Total number of categories")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "categories": [],
                "total": 0
            }
        }
    }
