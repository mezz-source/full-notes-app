from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.models import *
from src.db.base import Base

DATABASE_URL = "sqlite:///./data/app.db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

# Import all models so they are registered with Base before creating tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()