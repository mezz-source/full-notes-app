from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any

class Note(BaseModel):
    note_id: int
    author_id: int
    title: str
    content: str
    time_written: datetime
    flags: str

class CreateNote(BaseModel):
    author_id: int
    title: str
    content: str
    flags: str

class DeleteNote(BaseModel):
    note_id: int
    reason: str | None = ""

class ModifyNote(BaseModel):
    note_id: int
    modifications: Dict[str, Any]