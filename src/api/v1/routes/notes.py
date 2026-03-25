from fastapi import APIRouter, Query, Depends
from src.repositories.note_repo import NoteRepository
from src.repositories.user_repo import UserRepository
from src.util.responses import handle_request
from fastapi.responses import PlainTextResponse

from src.db.session import get_db
from sqlalchemy.orm import Session

# Schema related
from src.schemas.note import CreateNote, ModifyNote, SearchNote, AddNoteFlag, RemoveNoteFlag, UpdateNoteFlags

# Service/Core related
import src.schemas.core.note as NoteCore
from src.core.services.notes_service import NoteService
from src.repositories.note_repo import NoteRepository

router = APIRouter(prefix="/notes")

DEFAULT_HEADER = "note"
DEFAULT_QUERY_HEADER = "note_query"

async def get_note_service(db: Session = Depends(get_db)) -> NoteService:
    """Dependency function to get a NoteService instance with the necessary repositories"""
    return NoteService(NoteRepository(db), UserRepository(db))
    
@router.get("/")
def root():
    return PlainTextResponse("this is the notes root!")
    # return await service.get_note(GetNote(note_id=note_id))

@router.get("/search")
async def query_notes(
    note_query: SearchNote, offset: int = 0, limit: int = Query(default=100, le=100), \
        service: NoteService = Depends(get_note_service)):
    return await handle_request(DEFAULT_QUERY_HEADER, NoteCore.NoteQuery, service.query_notes, \
                                **note_query.model_dump(), offset=offset, limit=limit)

@router.post("/flags")
async def add_note_flag(request: AddNoteFlag, service: NoteService = Depends(get_note_service)):
    return await handle_request(DEFAULT_HEADER, NoteCore.AddNoteFlag, service.add_flag, **request.model_dump())

@router.delete("/flags")
async def remove_note_flag(request: RemoveNoteFlag, service: NoteService = Depends(get_note_service)):
    return await handle_request(DEFAULT_HEADER, NoteCore.RemoveNoteFlag, service.remove_flag, **request.model_dump())

@router.patch("/flags")
async def update_note_flags(request: UpdateNoteFlags, service: NoteService = Depends(get_note_service)):
    return await handle_request(DEFAULT_HEADER, NoteCore.UpdateNoteFlags, service.update_flags, **request.model_dump())

@router.get("/{note_id}")
async def get_note(note_id: int, service: NoteService = Depends(get_note_service)):
    return await handle_request(DEFAULT_HEADER, NoteCore.GetNote, service.get_note, note_id=note_id)

@router.delete("/{note_id}")
async def delete_note(note_id: int, service: NoteService = Depends(get_note_service)):
    return await handle_request(DEFAULT_HEADER, NoteCore.DeleteNote, service.delete_note, note_id=note_id)

@router.patch("/")
async def modify_note(request: ModifyNote, service: NoteService = Depends(get_note_service)):
    return await handle_request(DEFAULT_HEADER, NoteCore.ModifyNote, service.modify_note, **request.model_dump())

@router.post("/")
async def create_note(request: CreateNote, service: NoteService = Depends(get_note_service)):
    return await handle_request(DEFAULT_HEADER, NoteCore.CreateNote, service.create_note, **request.model_dump())