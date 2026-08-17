
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from src.config.database import Base
class OrderItems(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Integer, nullable=False) 
    
    order = relationship("Orders", back_populates="items")
    product = relationship("Products", back_populates="order_items")