from pydantic import BaseModel, Field

class CartItemAdd(BaseModel):
    product_id: int = Field(..., description="Product ID jo cart mein add karni hai")
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    price_per_unit: float
    quantity: int
    total_price: float

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    items: list[CartItemResponse]
    grand_total: float