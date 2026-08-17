from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from models.category_model import Categories
from schemas.product_schema import CategoryCreate, CategoryResponse
from utils.dependencies import check_admin_role
from models.user_model import Users

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("/", response_model=list[CategoryResponse])
def get_all_categories(db: Session = Depends(get_db)):
    """Public route: Har visitor categories dekh sakta hai."""
    return db.query(Categories).all()

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate, 
    db: Session = Depends(get_db),
    current_admin: Users = Depends(check_admin_role)  # Requires admin token
):
    """Admin route: Sirf admin hi naye category generate kar sakta hai."""
    existing = db.query(Categories).filter(Categories.name == category_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Yeh category pehle se exist karti hai!")
        
    new_cat = Categories(name=category_data.name)
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat

@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
def delete_category(
    category_id: int, 
    db: Session = Depends(get_db),
    current_admin: Users = Depends(check_admin_role)
):
    """Admin route: Category delete karein aur cascade ki wajah se saare products drop ho jayein ge."""
    category = db.query(Categories).filter(Categories.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category nahi mili!")
        
    db.delete(category)
    db.commit()
    return {"message": f"Category '{category.name}' aur iski saari products drop kar di gayi hain."}