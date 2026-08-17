from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.models.user_model import Users
from src.models.order_model import Orders
from src.schemas.auth_schema import UserSignUp, UserLogin, UserResponse
from src.utils.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserSignUp, db: Session = Depends(get_db)):
    """Naya user register karega. Role hamesha default 'customer' hoga."""
    existing_user = db.query(Users).filter(Users.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Yeh email pehle se registered hai!"
        )
    
    hashed_pwd = hash_password(user_data.password) 
    new_user = Users(
        name=user_data.name,
        email=user_data.email,
        password=hashed_pwd,
        role="customer"  # Security Lock: Koi khud se admin role register nahi kar sakta!
    )
    db.add(new_user) 
    db.commit() 
    db.refresh(new_user) 
    return new_user

@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """User login kar ke access token return karega."""
    user = db.query(Users).filter(Users.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password): 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Ghalat email ya password!"
        )
    
    # Token payload mein user metadata save karna [25, 26]
    token_payload = {
        "user_id": user.id,
        "role": user.role
    }
    access_token = create_access_token(data=token_payload)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }