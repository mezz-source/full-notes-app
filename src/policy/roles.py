from enum import Enum

class Permission(str, Enum):
    EDIT_OWN_NOTE = "edit_own"
    EDIT_ANY_NOTE = "edit_any"

    CREATE_NOTE = "create"

    READ_ANY_NOTE = "read_any"
    READ_OWN_NOTE = "read_own"
    READ_PRIVATE_NOTES = "read_private"

    BAN_USERS = "ban_users"

    MANAGE_OWN_USER = "manage_own_user"
    MANAGE_ANY_USER = "manage_all_users"


ROLE_PERMISSIONS = {
    "banned": {},
    "user": {
        Permission.EDIT_OWN_NOTE,
        Permission.READ_ANY_NOTE,
        Permission.READ_OWN_NOTE,
        Permission.MANAGE_OWN_USER,
        Permission.CREATE_NOTE
    },

    "moderator": {
        Permission.EDIT_ANY_NOTE,
        Permission.READ_PRIVATE_NOTES,
        Permission.BAN_USERS,
        Permission.CREATE_NOTE
    },

    "admin": {
        Permission.EDIT_ANY_NOTE,
        Permission.READ_ANY_NOTE,
        Permission.READ_PRIVATE_NOTES,
        Permission.MANAGE_ANY_USER,
        Permission.BAN_USERS,
        Permission.CREATE_NOTE
    },

    "owner": {
        Permission.EDIT_ANY_NOTE,
        Permission.READ_ANY_NOTE,
        Permission.READ_PRIVATE_NOTES,
        Permission.MANAGE_ANY_USER,
        Permission.BAN_USERS,
        Permission.CREATE_NOTE
    }
}