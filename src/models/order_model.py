from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship,declarative_base
from src.config.database import Base


import datetime

class Orders(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    total_price = Column(Integer, nullable=False)
    status = Column(String, default="pending", nullable=False)  # pending, completed, cancelled
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    customer = relationship("Users", back_populates="orders")
    items = relationship("OrderItems", back_populates="order", cascade="all, delete-orphan")
    
