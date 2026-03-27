from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from src.db.base import Base

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, default="", nullable=False)
    content = Column(String, default="", nullable=False)
    posted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    flags = Column(String, default="", nullable=False) # Seperated by commas
