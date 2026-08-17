from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserSignUp(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="User ka poora naam")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=6, max_length=100, description="Secure password")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True  # SQLAlchemy models se direct data parse karne ke liye

class TokenData(BaseModel):
    user_id: int
    role: str
