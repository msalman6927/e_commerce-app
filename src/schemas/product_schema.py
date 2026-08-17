from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ==================== CATEGORY SCHEMAS ====================
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Category ka naam (e.g., Electronics)")

class CategoryResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True

# ==================== PRODUCT SCHEMAS ====================
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    price: float = Field(..., gt=0, description="Product price must be greater than 0")
    stock: int = Field(..., ge=0, description="Available stock quantity")
    description: Optional[str] = Field(None, max_length=500)
    category_id: int = Field(..., description="Foreign Key linking to Category")

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    description: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int
    description: Optional[str]
    category_id: int
    created_at: datetime

    class Config:
        from_attributes = True