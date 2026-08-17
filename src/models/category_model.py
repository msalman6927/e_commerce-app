from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from src.config.database import Base

class Categories(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relationship: category_id delete hone par saari linked products khud delete ho jayengi (CASCADE)
    products = relationship("Products", back_populates="category", cascade="all, delete-orphan")