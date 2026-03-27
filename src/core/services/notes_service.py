import msgspec
from typing import Sequence
from src.schemas.core.note import MUTABLE_NOTE_KEYS, \
    Note, GetNote, CreateNote, DeleteNote, ModifyNote, \
        UpdateNoteFlags, AddNoteFlag, RemoveNoteFlag, NoteResponse, VALID_NOTE_FLAGS, NoteQuery
from src.policy.policy import can_create_note, can_edit_note, can_read_note, Permission, has_permission

from src.util.key import validate as validate_keys
from src.schemas.core.request import Error, Result
from sqlalchemy.orm import Session
from datetime import datetime
from src.util.responses import model_to_dict
from src.util.string_list import add_item, remove_item, add_many_items, remove_many_items, parse_string_list, filter_valid_items, remove_items_force
class NoteService():
    def __init__(self, note_repo, user_repo):
        self.note_repo = note_repo
        self.user_repo = user_repo

    async def _normalize_flags(self, flags: Sequence[object]) -> list[str]:
        return [flag.strip() for flag in flags if isinstance(flag, str) and flag.strip()]

    async def _is_note_owner(self, acting_user: dict, note: dict) -> bool:
        return int(acting_user.get("id")) == int(note.get("author_id")) # type: ignore

    async def _validate_owner_flag_scope(self, acting_user: dict, note: dict, flags: Sequence[str]) -> Error | None:
        if await self._is_note_owner(acting_user, note):
            illegal_flags = [flag for flag in flags if flag != "private"]
            if illegal_flags:
                return Error("FORBIDDEN", "Authors can only add or remove the 'private' flag on their own notes", 403)
        return None

    async def query_notes(self, data: NoteQuery, acting_user: dict | None = None) -> Result | Error:
        if not acting_user:
            return Error("UNAUTHORIZED", "Authentication required to query notes", 401)

        results = await self.note_repo.query(
            offset=data.offset,
            limit=data.limit,
            note_id=data.note_id or None,
            author_id=data.author_id or None,
            title=data.title or None,
            title_contains=data.title_contains or None,
            content_contains=data.content_contains or None,
            flags=data.flags or None,
        )

        is_admin_view = await has_permission(acting_user, Permission.EDIT_ANY_NOTE)

        response = []

        # Response head contains pagination info and total count of results for client convenience, but is not required for clients to function properly. Clients should be able to handle the absence of this head gracefully.
        response.append({
            "pagination": True,
            "count": len(results),
            "offset": data.offset,
            "limit": data.limit,
            "view_type": "admin" if is_admin_view else "standard",
            "query": {
                "note_id": data.note_id,
                "author_id": data.author_id,
                "title": data.title,
                "title_contains": data.title_contains,
                "content_contains": data.content_contains,
                "flags": data.flags
            }
        })

        for result in results:
            note_dict = await model_to_dict(result)
            if await can_read_note(acting_user, note_dict):
                response.append(note_dict)

        return Result("SUCCESS", "Notes retrieved successfully", response, 200)

    async def get_note(self, data: GetNote, acting_user: dict | None = None) -> Result | Error:
        if not acting_user:
            return Error("UNAUTHORIZED", "Authentication required to get note", 401)

        result = await self.note_repo.get(data.note_id)
        if not result:
            return Error("NOT_FOUND", f"Note with ID {data.note_id} was not found", 404)

        response = await model_to_dict(result)
        if not await can_read_note(acting_user, response):
            return Error("FORBIDDEN", "You do not have permission to read this note", 403)

        return Result("SUCCESS", f"Note found with ID {data.note_id}", response, 200)
    
    async def create_note(self, data: CreateNote, acting_user: dict | None = None) -> Result | Error:
        if not acting_user:
            return Error("UNAUTHORIZED", "Authentication required to create note", 401)

        if not await can_create_note(acting_user):
            return Error("FORBIDDEN", "You do not have permission to create notes", 403)

        if data.author_id != int(acting_user.get("id")): # type: ignore
            return Error("FORBIDDEN", "Author ID must match the authenticated user's ID", 403)

        cleaned_flags = await self._normalize_flags(data.flags) # type: ignore

        result = await validate_keys(VALID_NOTE_FLAGS, cleaned_flags) # type: ignore
        valid, illegal_keys = result.get("valid"), result.get("illegal_keys")

        if not valid:
            return Error("BAD_REQUEST", f"Failed to create note due to one or more invalid flags: {illegal_keys}", 422)

        # Convert list into xyz,xyz
        flags_str = ",".join(cleaned_flags)

        note_result = await self.note_repo.create(
            author_id=int(acting_user.get("id")), # type: ignore
            title=data.title,
            content=data.content,
            flags=flags_str
        )

        note_data = await model_to_dict(note_result)
        return Result("SUCCESS", f"New note created by author_id {acting_user.get('id')}", note_data, 201)

    async def delete_note(self, data: DeleteNote, acting_user: dict | None = None) -> Result | Error:
        if not acting_user:
            return Error("UNAUTHORIZED", "Authentication required to delete note", 401)

        note = await self.note_repo.get(data.note_id)
        if not note:
            return Error("NOT_FOUND", f"Note with ID {data.note_id} was not found", 404)

        note_data = await model_to_dict(note)
        if not await can_edit_note(acting_user, note_data):
            return Error("FORBIDDEN", "You do not have permission to delete this note", 403)

        success = await self.note_repo.delete(data.note_id)
        if not success:
            return Error("INTERNAL_ERROR", f"Failed to delete note with ID {data.note_id}", 500)

        return Result("SUCCESS", f"Note with ID {data.note_id} deleted", None, 200)
    
    async def modify_note(self, data: ModifyNote, acting_user: dict | None = None) -> Result | Error:
        if not acting_user:
            return Error("UNAUTHORIZED", "Authentication required to modify note", 401)

        note = await self.note_repo.get(data.note_id)
        if not note:
            return Error("NOT_FOUND", f"Note with ID {data.note_id} was not found", 404)

        existing_note = await model_to_dict(note)
        if not await can_edit_note(acting_user, existing_note):
            return Error("FORBIDDEN", "You do not have permission to modify this note", 403)

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
    
    async def add_flag(self, data: AddNoteFlag, acting_user: dict | None = None) -> Result | Error:
        if not acting_user:
            return Error("UNAUTHORIZED", "Authentication required to add flags", 401)

        flags_to_add = await self._normalize_flags(data.flags)
        note_id = data.note_id

        note = await self.note_repo.get(note_id)
        if not note:
            return Error("NOT_FOUND", f"Note with ID {note_id} was not found", 404)

        existing_note = await model_to_dict(note)
        if not await can_edit_note(acting_user, existing_note):
            return Error("FORBIDDEN", "You do not have permission to modify note flags", 403)

        owner_scope_error = await self._validate_owner_flag_scope(acting_user, existing_note, flags_to_add)
        if owner_scope_error:
            return owner_scope_error

        # Validate all flags
        result = await validate_keys(VALID_NOTE_FLAGS, flags_to_add)
        valid, illegal_keys = result.get("valid"), result.get("illegal_keys")

        if not valid:
            return Error("BAD_MODIFY", f"Failed to add flags as one or more are not valid: {illegal_keys}", 422)    

        # Parse existing flags and add new ones
        existing_flags = await parse_string_list(note.flags)
        for flag in flags_to_add:
            if flag not in existing_flags:
                existing_flags.append(flag)
        
        flags_str = ",".join(existing_flags)
        result = await self.note_repo.modify(note_id, {"flags": flags_str})
        note_data = await model_to_dict(result)
        return Result("SUCCESS", f"Flags added to note with ID {note_id}", note_data, 200)

    async def remove_flag(self, data: RemoveNoteFlag, acting_user: dict | None = None) -> Result | Error:
        if not acting_user:
            return Error("UNAUTHORIZED", "Authentication required to remove flags", 401)

        flags_to_remove = await self._normalize_flags(data.flags)
        note_id = data.note_id

        note = await self.note_repo.get(note_id)
        if not note:
            return Error("NOT_FOUND", f"Note with ID {note_id} was not found", 404)

        existing_note = await model_to_dict(note)
        if not await can_edit_note(acting_user, existing_note):
            return Error("FORBIDDEN", "You do not have permission to modify note flags", 403)

        owner_scope_error = await self._validate_owner_flag_scope(acting_user, existing_note, flags_to_remove)
        if owner_scope_error:
            return owner_scope_error

        # Allow removal of any flags (even invalid/stale ones) to enable cleanup
        flags_str = await remove_items_force(note.flags, flags_to_remove)
        result = await self.note_repo.modify(note_id, {"flags": flags_str})
        note_data = await model_to_dict(result)
        return Result("SUCCESS", f"Flags removed from note with ID {note_id}", note_data, 200)

    async def update_flags(self, data: UpdateNoteFlags, acting_user: dict | None = None) -> Result | Error:
        if not acting_user:
            return Error("UNAUTHORIZED", "Authentication required to update flags", 401)

        new_flags = await self._normalize_flags(data.new_flags)

        result = await validate_keys(VALID_NOTE_FLAGS, new_flags)
        valid, illegal_keys = result.get("valid"), result.get("illegal_keys")

        if not valid:
            return Error("BAD_MODIFY", f"Failed to alter flags as one or more are not valid: {illegal_keys}", 422)    

        note = await self.note_repo.get(data.note_id)
        if not note:
            return Error("NOT_FOUND", f"Note with ID {data.note_id} was not found", 404)

        existing_note = await model_to_dict(note)
        if not await can_edit_note(acting_user, existing_note):
            return Error("FORBIDDEN", "You do not have permission to modify note flags", 403)

        owner_scope_error = await self._validate_owner_flag_scope(acting_user, existing_note, new_flags)
        if owner_scope_error:
            return owner_scope_error

        result = await self.note_repo.modify(data.note_id, {"flags": ",".join(new_flags)})
        note_data = await model_to_dict(result)
        return Result("SUCCESS", f"Flags for note with ID {data.note_id} updated", note_data, 200)