from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from models.user_model import Users
from schemas.auth_schema import UserResponse
from utils.dependencies import check_admin_role

router = APIRouter(prefix="/admin", tags=["Admin Operations"])

@router.put("/promote/{user_id}", response_model=UserResponse)
def promote_to_admin(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_admin: Users = Depends(check_admin_role)  # Requires strictly Admin Token [20]
):
    """Kisi bhi customer ko promote kar ke admin role assign karta hai."""
    user_to_promote = db.query(Users).filter(Users.id == user_id).first()
    if not user_to_promote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User nahi mila!")
        
    user_to_promote.role = "admin"
    db.commit()
    db.refresh(user_to_promote)
    return user_to_promote

@router.get("/users", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db), 
    current_admin: Users = Depends(check_admin_role)
):
    """Database mein registered saare users ki list return karta hai."""
    users = db.query(Users).all()
    return users

@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_or_ban_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_admin: Users = Depends(check_admin_role)
):
    """Kisi bhi malicious user ko database se delete/ban karta hai."""
    user_to_delete = db.query(Users).filter(Users.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User nahi mila!")
        
    if user_to_delete.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Aap khud apne admin account ko delete nahi kar sakte!"
        )
        
    db.delete(user_to_delete)
    db.commit()
    return {"message": f"User '{user_to_delete.name}' ko database se delete kar diya gaya hai."}