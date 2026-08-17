import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

# JWT Config (Envs se load hogi ya default values use karegi) [12]
SECRET_KEY = os.getenv("SECRET_KEY", "SUPER_SECRET_E_COMMERCE_KEY_2026_CHANGE_THIS")
ALGORITHM = os.getenv("ALGORITHM", "HS256") [12]
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # 24 Hours [13]

# Password Hashing Context [14]
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Plain password ko secure hash mein convert karega."""
    return pwd_context.hash(password) [15]

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Plain password ko database ke hashed password se verify karega."""
    return pwd_context.verify(plain_password, hashed_password) [16]

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """User ke liye ek secure JWT Token generate karega."""
    to_encode = data.copy() [17]
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire}) [17]
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) [17]
    return encoded_jwt