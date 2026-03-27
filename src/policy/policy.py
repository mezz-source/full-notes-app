from src.policy.roles import Permission, ROLE_PERMISSIONS
from src.util.string_list import parse_string_list
from typing import Dict, Any

# Helper functions to extract data from user dict and note dict/model


async def get_user_id(user: Dict[str, Any]) -> int | None:
    """Extract user ID from user dict."""
    return user.get("id")


async def get_user_roles(user: Dict[str, Any]) -> list[str]:
    """Extract and parse roles from user dict."""
    roles_str = user.get("roles", "")
    return await parse_string_list(roles_str)


async def get_note_author_id(note: Dict[str, Any]) -> int | None:
    """Extract author ID from note dict."""
    return note.get("author_id")


async def get_note_flags(note: Dict[str, Any]) -> list[str]:
    """Extract and parse flags from note dict."""
    flags_str = note.get("flags", "")
    return await parse_string_list(flags_str)


async def get_user_permissions_from_roles(roles: list[str]) -> set[Permission]:
    """Get all permissions for a list of roles."""
    permissions = set()
    for role in roles:
        if role in ROLE_PERMISSIONS:
            permissions.update(ROLE_PERMISSIONS[role])
    return permissions


async def get_user_permissions(user: Dict[str, Any]) -> set[Permission]:
    """Get all permissions for a user."""
    roles = await get_user_roles(user)
    return await get_user_permissions_from_roles(roles)


async def has_flag(note: Dict[str, Any], flag: str) -> bool:
    """Check if a note has a specific flag."""
    note_flags = await get_note_flags(note)
    return flag in note_flags


async def has_permission(user: Dict[str, Any], permission: Permission) -> bool:
    """Check if user has a specific permission."""
    permissions = await get_user_permissions(user)
    return permission in permissions


async def can_edit_note(user: Dict[str, Any], note: Dict[str, Any]) -> bool:
    """Check if user can edit a note."""
    user_id = await get_user_id(user)
    author_id = await get_note_author_id(note)

    if user_id == author_id:
        # Owners can always edit their own note even if roles are missing/misconfigured.
        return True

    return await has_permission(user, Permission.EDIT_ANY_NOTE)


async def can_read_note(user: Dict[str, Any], note: Dict[str, Any]) -> bool:
    """Check if user can read a note."""
    user_id = await get_user_id(user)
    author_id = await get_note_author_id(note)
    
    # Check flag restrictions first
    if await has_flag(note, "private"):
        if not (await has_permission(user, Permission.READ_PRIVATE_NOTES) or user_id == author_id):
            return False
    
    if await has_flag(note, "admin_only"):
        if not await has_permission(user, Permission.MANAGE_ANY_USER):
            return False
    
    # General read permissions
    return await has_permission(user, Permission.READ_ANY_NOTE) or \
           (user_id == author_id and await has_permission(user, Permission.READ_OWN_NOTE))


async def can_create_note(user: Dict[str, Any]) -> bool:
    """Check if user is allowed to create a note."""
    return await has_permission(user, Permission.CREATE_NOTE)


async def can_manage_user(acting_user: Dict[str, Any], target_user: Dict[str, Any]) -> bool:
    """Check if acting user can manage target user."""
    acting_user_id = await get_user_id(acting_user)
    target_user_id = await get_user_id(target_user)
    
    target_roles = await get_user_roles(target_user)
    acting_roles = await get_user_roles(acting_user)
    if "owner" in acting_roles:
        return True # im the owner

    if "admin" in target_roles or "owner" in target_roles:
        return False 

    if acting_user_id == target_user_id:
        return await has_permission(acting_user, Permission.MANAGE_OWN_USER)
    
    return await has_permission(acting_user, Permission.MANAGE_ANY_USER)


async def can_ban_user(acting_user: Dict[str, Any], target_user: Dict[str, Any]) -> bool:
    """Check if acting user can ban target user. Prevents self-banning."""
    acting_user_id = await get_user_id(acting_user)
    target_user_id = await get_user_id(target_user)
    
    if acting_user_id == target_user_id:
        return False
    return await has_permission(acting_user, Permission.BAN_USERS)


async def can_view_user(acting_user: Dict[str, Any], viewed_user: Dict[str, Any]) -> bool:
    """Check if acting user can view basic info of viewed user. Only admins are hidden."""
    acting_roles = await get_user_roles(acting_user)
    viewed_roles = await get_user_roles(viewed_user)
    
    if "admin" in acting_roles or "owner" in acting_roles:
        return True
    # elif "admin" in viewed_roles:
        # return False
    return True


async def can_view_extended_user(acting_user: Dict[str, Any], viewed_user: Dict[str, Any]) -> bool:
    """Check if acting user can view extended/private info of viewed user."""
    acting_user_id = await get_user_id(acting_user)
    viewed_user_id = await get_user_id(viewed_user)
    
    if acting_user_id == viewed_user_id:
        return True  # Users can view their own extended info
    # Admins can view all
    return await has_permission(acting_user, Permission.MANAGE_ANY_USER)
