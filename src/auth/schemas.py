"""Authentication schemas for request/response validation."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from ..users.enums import UserRole


class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }
    }


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    }


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str = Field(..., description="JWT refresh token")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    }


class CurrentUserResponse(BaseModel):
    """Schema for current user information."""
    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    full_name: str = Field(..., description="User full name")
    role: UserRole = Field(..., description="User role")
    is_active: bool = Field(..., description="Whether user is active")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "full_name": "John Doe",
                "role": "viewer",
                "is_active": True
            }
        }
    }
