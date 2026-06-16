"""Item schemas for request/response validation."""

from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import Optional, Dict, Any
from datetime import datetime
import json
import re


class AdditionalDataMixin:
    """Mixin for parsing additional_data"""
    
    @field_validator('additional_data', mode='before')
    @classmethod
    def parse_additional_data(cls, v):
        """Convert JSON-string to dict"""
        if v is None:
            return None
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return None

class ItemBase(BaseModel):
    """Base item schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255, description="Item name")
    picture_url: str = Field(..., max_length=500, description="Item picture URL")
    description: Optional[str] = Field(None, description="Item description")
    category_id: int = Field(..., gt=0, description="Category ID")


class ItemCreate(ItemBase, AdditionalDataMixin):
    """Schema for creating a new item."""
    slug: Optional[str] = Field(None, max_length=255, description="URL-friendly slug (auto-generated if not provided)")
    is_hidden: bool = Field(default=False, description="Whether item is hidden")
    additional_data: Optional[Dict[str, Any]] = Field(None, description="Additional flexible data as JSON")
    
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
                "name": "Example Item",
                "slug": "example-item",
                "picture_url": "https://example.com/image.jpg",
                "description": "An example item",
                "category_id": 1,
                "is_hidden": False,
                "additional_data": {"key": "value"}
            }
        }
    }


class ItemUpdate(BaseModel, AdditionalDataMixin):
    """Schema for updating an item."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Item name")
    slug: Optional[str] = Field(None, max_length=255, description="URL-friendly slug")
    picture_url: Optional[str] = Field(None, max_length=500, description="Item picture URL")
    description: Optional[str] = Field(None, description="Item description")
    category_id: Optional[int] = Field(None, gt=0, description="Category ID")
    is_hidden: Optional[bool] = Field(None, description="Whether item is hidden")
    additional_data: Optional[Dict[str, Any]] = Field(None, description="Additional flexible data as JSON")

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
                "name": "Updated Item Name",
                "description": "Updated description"
            }
        }
    }


class ItemResponse(ItemBase, AdditionalDataMixin):
    """Schema for item response."""
    id: int = Field(..., description="Item ID")
    slug: str = Field(..., description="URL-friendly slug")
    is_hidden: bool = Field(..., description="Whether item is hidden")
    additional_data: Optional[Dict[str, Any]] = Field(None, description="Additional flexible data")
    link: Optional[str] = Field(None, max_length=500, description="Item link URL")
    created_by_id: Optional[int] = Field(None, description="User ID who created the item")
    updated_by_id: Optional[int] = Field(None, description="User ID who last updated the item")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    @property
    def link(self) -> str:
        """Ссылка вычисляется из модели Item"""
        # Это поле будет автоматически браться из Item.link
        return self._link if hasattr(self, '_link') else ""

    @property
    def thumbnail_url(self) -> Optional[str]:
        if self.picture_url:
            return f"/api/items/{self.id}/image?size=thumbnail"
        return None
    
    @property
    def full_image_url(self) -> Optional[str]:
        if self.picture_url:
            return f"/api/items/{self.id}/image?size=full"
        return None
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Example Item",
                "slug": "example-item",
                "picture_url": "https://example.com/image.jpg",
                "link": "https://example.com/item",
                "description": "An example item",
                "category_id": 1,
                "is_hidden": False,
                "additional_data": {"key": "value"},
                "created_by_id": 1,
                "updated_by_id": 1,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
    }


class ItemListResponse(BaseModel):
    """Schema for item list response with pagination."""
    items: list[ItemResponse] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Number of items per page")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [],
                "total": 0,
                "skip": 0,
                "limit": 20
            }
        }
    }
