from fastapi import APIRouter, Depends
from src.util.responses import handle_request
from fastapi.responses import PlainTextResponse, Response

# Schema related
from src.schemas.note import CreateNote, ModifyNote

# Service/Core related
import src.schemas.core.note as NoteCore
import src.core.services.notes_service as NoteService

router = APIRouter(prefix="/notes")

@router.get("/")
def root():
    return PlainTextResponse("this is the notes root!")

@router.get("/{note_id}")
def get_note(note_id: int):
    return Response()

@router.delete("/{note_id}")
def delete_note(note_id: int):
    return Response()

@router.patch("/")
def modify_note(request: ModifyNote):
    return Response()

@router.post("/")
def create_note(request: CreateNote):
    return Response()
