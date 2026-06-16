"""Category database models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class Category(Base):
    """Category model representing categories table."""
    
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_hidden = Column(Boolean, default=False)
    
    # Relationships
    items = relationship("Item", back_populates="category", cascade="all, delete-orphan")
    
    # Audit fields
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name}, slug={self.slug})>"
