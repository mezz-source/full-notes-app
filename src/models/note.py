from sqlalchemy import Column, Integer, String, ForeignKey
from src.db.base import Base

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    content = Column(String)
    flags = Column(String) # Seperated by commas