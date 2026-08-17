from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from src.config.database import get_db
from src.models.product_model import Products
from src.models.category_model import Categories
from src.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from src.utils.dependencies import check_admin_role
from src.models.user_model import Users

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=list[ProductResponse])
def get_products(
    category_id: Optional[int] = Query(None, description="Category ke mutabiq filter karein"),
    search: Optional[str] = Query(None, description="Name ke mutabiq search karein"),
    db: Session = Depends(get_db)
):
    """Public route: Search or filter products in the store."""
    query = db.query(Products)
    if category_id:
        query = query.filter(Products.category_id == category_id)
    if search:
        query = query.filter(Products.name.ilike(f"%{search}%"))
    return query.all()

@router.get("/{product_id}", response_model=ProductResponse)
def get_single_product(product_id: int, db: Session = Depends(get_db)):
    """Public route: Single product view details."""
    product = db.query(Products).filter(Products.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product nahi mila!")
    return product

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate, 
    db: Session = Depends(get_db),
    current_admin: Users = Depends(check_admin_role)
):
    """Admin route: Securely upload new product."""
    # Check if category is valid
    category = db.query(Categories).filter(Categories.id == product_data.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category ID valid nahi hai!")
        
    new_product = Products(
        name=product_data.name,
        price=product_data.price,
        stock=product_data.stock,
        description=product_data.description,
        category_id=product_data.category_id
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_admin: Users = Depends(check_admin_role)
):
    """Admin route: Update pricing, description or stock values."""
    product = db.query(Products).filter(Products.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product nahi mila!")
        
    if product_data.category_id is not None:
        category = db.query(Categories).filter(Categories.id == product_data.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Invalid Category ID!")
            
    # Update only fields provided by client
    for key, value in product_data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
        
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: Users = Depends(check_admin_role)
):
    """Admin route: Delete product from database."""
    product = db.query(Products).filter(Products.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product nahi mila!")
        
    db.delete(product)
    db.commit()
    return {"message": f"Product '{product.name}' deleted successfully!"}