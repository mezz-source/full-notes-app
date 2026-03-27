from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any

class Note(BaseModel):
    note_id: int
    author_id: int
    title: str
    content: str
    posted_at: datetime
    flags: str

class CreateNote(BaseModel):
    author_id: int
    title: str
    content: str
    flags: list[str] = [""]

class DeleteNote(BaseModel):
    note_id: int

class ModifyNote(BaseModel):
    note_id: int
    modifications: Dict[str, Any]

class AddNoteFlag(BaseModel):
    note_id: int
    flags: list[str]

class RemoveNoteFlag(BaseModel):
    note_id: int
    flags: list[str]

class UpdateNoteFlags(BaseModel):
    note_id: int
    new_flags: list[str]

class SearchNote(BaseModel):
    note_id: int | None = None
    author_id: int | None = None
    title: str | None = None
    title_contains: str | None = None
    content_contains: str | None = None
    flags: str | None = None