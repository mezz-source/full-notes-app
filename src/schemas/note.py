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

class ModifyNote(BaseModel):
    note_id: int
    modifications: Dict[str, Any]

class AddNoteFlag(BaseModel):
    note_id: int
    flag: str

class RemoveNoteFlag(BaseModel):
    note_id: int
    flag: str

class UpdateNoteFlags(BaseModel):
    note_id: int
    new_flags: str

class SearchNote(BaseModel):
    note_id: int | None = None
    author_id: int | None = None
    title: str | None = None
    title_contains: str | None = None
    content_contains: str | None = None
    tag: str | None = None