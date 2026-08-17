from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_at_purchase: int  # <-- Matches your model's Integer field

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_price: int  # <-- Matches your model's Integer field
    status: str
    created_at: datetime
    items: List[OrderItemResponse]  # <-- Detailed items returns automatically

    class Config:
        from_attributes = True