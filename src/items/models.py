"""Item database models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class Item(Base):
    """Item model representing items table."""
    
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    picture_url = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    is_hidden = Column(Boolean, default=False, index=True)
    
    # Flexible additional data as JSON string
    additional_data = Column(Text, nullable=True)
    
    # Relationships
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    category = relationship("Category", back_populates="items")
    
    # Audit fields
    created_by_id = Column(Integer, ForeignKey("users.id"))
    updated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<Item(id={self.id}, name={self.name}, slug={self.slug}, category_id={self.category_id})>"

    @property
    def link(self) -> str:
        """Generating link"""
        if self.category and self.slug:
            return f"/{self.category.slug}/{self.slug}"
        return f"/{self.slug}"
