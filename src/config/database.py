from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os
Base=declarative_base()

load_dotenv()
db_url=os.getenv("DATABASE_URL")
base=declarative_base()

session=create_engine(db_url)
session_local=sessionmaker(autocommit=False,autoflush=False,bind=session)

def get_db():
    db=session_local()
    try:
        yield db
    finally:
        db.close()