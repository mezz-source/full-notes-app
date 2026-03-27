from typing import Dict, Any, List, Union, Literal
from datetime import datetime
import msgspec

MUTABLE_NOTE_KEYS = {"title", "content"}
VALID_NOTE_FLAGS = {"private", "admin_only", "archived"}
Flag = Union[Literal["private"], Literal["admin_only"], Literal["archived"]]
class Note(msgspec.Struct):
    author_id: int
    title: str
    content: str
    posted_at: datetime
    flags: List[Flag]

class NoteResponse(msgspec.Struct):
    note_id: int
    author_id: int
    title: str
    content: str
    posted_at: datetime
    flags: List[Flag]
class GetNote(msgspec.Struct):
    note_id: int
    current_user: Dict[str, Any] | None = None
class CreateNote(msgspec.Struct):
    author_id: int
    title: str
    content: str
    flags: List[Flag | str]
    current_user: Dict[str, Any] | None = None
class DeleteNote(msgspec.Struct):
    note_id: int
    current_user: Dict[str, Any] | None = None
class ModifyNote(msgspec.Struct):
    note_id: int
    modifications: Dict[str, Any]
    current_user: Dict[str, Any] | None = None
class UpdateNoteFlags(msgspec.Struct):
    note_id: int
    new_flags: List[Flag]
    current_user: Dict[str, Any] | None = None
class RemoveNoteFlag(msgspec.Struct):
    note_id: int
    flags: List[Flag | str]
    current_user: Dict[str, Any] | None = None
class AddNoteFlag(msgspec.Struct):
    note_id: int
    flags: List[Flag | str]
    current_user: Dict[str, Any] | None = None

class NoteQuery(msgspec.Struct):
    note_id: int | None = None
    author_id: int | None = None
    title: str | None = None
    title_contains: str | None = None
    content_contains: str | None = None
    flags: str | None = None
    current_user: Dict[str, Any] | None = None
    offset: int = 0
    limit: int = 100