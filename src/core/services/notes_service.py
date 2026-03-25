import msgspec
from src.schemas.core.note import MUTABLE_NOTE_KEYS, \
    Note, GetNote, CreateNote, DeleteNote, ModifyNote, \
        UpdateNoteFlags, AddNoteFlag, RemoveNoteFlag, NoteResponse, VALID_NOTE_FLAGS, NoteQuery

from src.util.key import validate as validate_keys
from src.schemas.core.request import Error, Result
from sqlalchemy.orm import Session
from datetime import datetime
from src.util.responses import model_to_dict
from src.util.string_list import add_item, remove_item
class NoteService():
    def __init__(self, note_repo, user_repo):
        self.note_repo = note_repo
        self.user_repo = user_repo

    async def query_notes(self, data: NoteQuery) -> Result | Error:
        results = await self.note_repo.query(
            offset=data.offset,
            limit=data.limit,
            note_id=data.note_id or None,
            author_id=data.author_id or None,
            title=data.title or None,
            title_contains=data.title_contains or None,
            content_contains=data.content_contains or None,
            tag=data.tag or None,
        )

        response = []

        # Response head contains pagination info and total count of results for client convenience, but is not required for clients to function properly. Clients should be able to handle the absence of this head gracefully.
        response.append({
            "pagination": True,
            "count": len(results),
            "offset": data.offset,
            "limit": data.limit,
            "query": {
                "note_id": data.note_id,
                "author_id": data.author_id,
                "title": data.title,
                "title_contains": data.title_contains,
                "content_contains": data.content_contains,
                "tag": data.tag
            }
        })

        for result in results:
            note_dict = await model_to_dict(result)
            response.append(note_dict)

        return Result("SUCCESS", "Notes retrieved successfully", response, 200)

    async def get_note(self, data: GetNote) -> Result | Error:
        result = await self.note_repo.get(data.note_id)
        if not result:
            return Error("NOT_FOUND", f"Note with ID {data.note_id} was not found", 404)

        response = await model_to_dict(result)
        return Result("SUCCESS", f"Note found with ID {data.note_id}", response, 200)
    
    async def create_note(self, data: CreateNote) -> Result | Error:
        note_result = await self.note_repo.create(
            author_id=data.author_id,
            title=data.title,
            content=data.content,
            flags=data.flags
        )
        note_data = await model_to_dict(note_result)
        return Result("SUCCESS", f"New note created by author_id {data.author_id}", note_data, 201)

    async def delete_note(self, data: DeleteNote) -> Result | Error:
        success = await self.note_repo.delete(data.note_id)
        if not success:
            return Error("NOT_FOUND", f"Note with ID {data.note_id} was not found", 404)

        return Result("SUCCESS", f"Note with ID {data.note_id} deleted", None, 200)
    
    async def modify_note(self, data: ModifyNote) -> Result | Error:
        modify_dict = msgspec.structs.asdict(data)
        modifications = modify_dict.get("modifications")

        result = await validate_keys(MUTABLE_NOTE_KEYS, modifications.keys()) # type: ignore
        valid, illegal_keys = result.get("valid"), result.get("illegal_keys")

        if not valid:
            return Error("BAD_MODIFY", f"Failed to alter note due to illegal key changes: {illegal_keys}", 422) 
        
        result = await self.note_repo.modify(data.note_id, modifications)
        if not result:
            return Error("NOT_FOUND", f"Note with ID {data.note_id} was not found", 404)

        note_data = await model_to_dict(result)
        return Result("SUCCESS", f"Note with ID {data.note_id} modified", note_data, 200)
    
    async def add_flag(self, data: AddNoteFlag) -> Result | Error:
        flag = data.flag

        result = await validate_keys(VALID_NOTE_FLAGS, [flag])
        valid, illegal_keys = result.get("valid"), result.get("illegal_keys")

        if not valid:
            return Error("BAD_MODIFY", f"Failed to alter flags as one or more are not valid: {illegal_keys}", 422)    

        note = await self.note_repo.get(data.note_id)
        if not note:
            return Error("NOT_FOUND", f"Note with ID {data.note_id} was not found", 404)

        if data.flag in note.flags.split(","):
            return Error("FLAG_EXISTS", f"Note with ID {data.note_id} already has flag {data.flag}", 409)
        flags = add_item(note.flags, data.flag)
        result = await self.note_repo.modify(data.note_id, {"flags": flags})
        
        return Result("SUCCESS", f"Flag added to note with ID {data.note_id}", result, 200)

    async def remove_flag(self, data: RemoveNoteFlag) -> Result | Error:
        flag = data.flag

        result = await validate_keys(VALID_NOTE_FLAGS, [flag])
        valid, illegal_keys = result.get("valid"), result.get("illegal_keys")

        if not valid:
            return Error("BAD_MODIFY", f"Failed to alter flags as one or more are not valid: {illegal_keys}", 422)    

        note = await self.note_repo.get(data.note_id)
        if not note:
            return Error("NOT_FOUND", f"Note with ID {data.note_id} was not found", 404)

        if data.flag not in note.flags.split(","):
            return Error("FLAG_NOT_FOUND", f"Note with ID {data.note_id} does not have flag {data.flag}", 404)
        
        flags = remove_item(note.flags, data.flag)
        result = await self.note_repo.modify(data.note_id, {"flags": flags})
        
        return Result("SUCCESS", f"Flag removed from note with ID {data.note_id}", result, 200)

    async def update_flags(self, data: UpdateNoteFlags) -> Result | Error:
        new_flags = data.new_flags

        result = await validate_keys(VALID_NOTE_FLAGS, new_flags)
        valid, illegal_keys = result.get("valid"), result.get("illegal_keys")

        if not valid:
            return Error("BAD_MODIFY", f"Failed to alter flags as one or more are not valid: {illegal_keys}", 422)    

        note = await self.note_repo.get(data.note_id)
        if not note:
            return Error("NOT_FOUND", f"Note with ID {data.note_id} was not found", 404)

        result = await self.note_repo.modify(data.note_id, {"flags": ",".join(new_flags)})
        
        return Result("SUCCESS", f"Flags for note with ID {data.note_id} updated", result, 200)