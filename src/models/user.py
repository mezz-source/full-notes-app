from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from src.db.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    password_hash = Column(String, default="", nullable=False)
    roles = Column(String, default="user", nullable=False) # Seperated by commas
