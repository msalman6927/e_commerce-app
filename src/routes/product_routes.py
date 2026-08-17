from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from models.product_model import Products
from models.category_model import Categories
from schemas.product_schema import ProductCreate, ProductResponse, CategoryCreate, CategoryResponse
from utils.dependencies import check_admin_role
router = APIRouter(
    prefix="/store",
    tags=["Store Management (Products & Categories)"]
)

# ================= CATEGORY ENDPOINTS =================

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category_data: CategoryCreate, db: Session = Depends(get_db), current_user = Depends(check_admin_role)):
    """
    [SECURE: Admin Only] Nayi product category banane ke liye.
    Humne check_admin_role lagaya hai jo user ke token se 'role' check karega.
    """
    existing = db.query(Categories).filter(Categories.name == category_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Yeh category pehle se maujood hai!")
    
    new_category = Categories(name=category_data.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.get("/categories", response_model=List[CategoryResponse])
def get_all_categories(db: Session = Depends(get_db)):
    """
    [PUBLIC Route] Isay koi bhi browse kar sakta hai bina login kiye.
    """
    return db.query(Categories).all()


# ================= PRODUCT ENDPOINTS =================

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductCreate, db: Session = Depends(get_db), current_user = Depends(check_admin_role)):
    """
    [SECURE: Admin Only] Store par naya product list karne ke liye.
    """
    # Check karein ke jo category_id di gayi hai, kya woh exist karti hai
    if product_data.category_id:
        category = db.query(Categories).filter(Categories.id == product_data.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Di gayi Category ID exist nahi karti!")
    
    new_product = Products(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock_quantity=product_data.stock_quantity,
        category_id=product_data.category_id
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/products", response_model=List[ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    """
    [PUBLIC Route] Customer ko saare products dikhane ke liye.
    """
    return db.query(Products).all()

@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    """
    [PUBLIC Route] Kisi specific product ki depth details dekhne ke liye.
    """
    product = db.query(Products).filter(Products.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product nahi mila!")
    return product