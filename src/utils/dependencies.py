import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.models.user_model import Users
from src.utils.security import SECRET_KEY, ALGORITHM

# OAuth2 Scheme header se 'Authorization: Bearer <token>' fetch karegi [21]
security_scheme =  HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme), 
    db: Session = Depends(get_db)
) -> Users:
    """JWT Token ko decode kar ke current logged-in user database se return karega."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Aap logged in nahi hain ya token invalid/expired hai!",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 3. Credentials object se plain token nikalhein
    token = credentials.credentials
    
    try:
        # Token decode karna
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = db.query(Users).filter(Users.id == user_id).first()
    if user is None:
        raise credentials_exception
        
    return user

def check_admin_role(current_user: Users = Depends(get_current_user)) -> Users:
    """Verify karega ke logged-in user strictly ek 'admin' ho."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Sirf Admin hi is operation ko perform kar sakta hai!"
        )
    return current_user