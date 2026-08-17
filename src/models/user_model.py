from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.orm import relationship
from src.config.database import Base

class Users(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String(50),nullable=False)
    email=Column(String(50),nullable=False,unique=True)
    password=Column(String(100),nullable=False) 
    orders=relationship("Orders",back_populates="customer")
    role = Column(String(20), nullable=False, server_default="customer")  # ← yeh add karo

    
    