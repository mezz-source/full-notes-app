from typing import Dict, Any, List
from datetime import datetime
import msgspec

MUTABLE_USER_KEYS = {"username", "email", "birthday"}
VALID_ROLES = {"admin", "user", "moderator", "banned", "owner"}
class User(msgspec.Struct):
    user_id: int
    username: str
    created_at: datetime
    birthday: datetime

class GetUser(msgspec.Struct):
    user_id: int
class DeleteUser(msgspec.Struct):
    user_id: int
class CreateUser(msgspec.Struct):
    username: str
    password: str
    email: str

class UpdateRoles(msgspec.Struct):
    user_id: int
    new_roles: List[str]
class RemoveRole(msgspec.Struct):
    user_id: int
    roles: List[str]
class AddRole(msgspec.Struct):
    user_id: int
    roles: List[str]

class ModifyUser(msgspec.Struct):
    user_id: int
    modifications: Dict[str, Any]

class UserResponse(msgspec.Struct):
    user_id: int
    username: str
    token: str

class GetUserUsername(msgspec.Struct):
    user_id: int
class UserQuery(msgspec.Struct):
    username_contains: str | None = None
    username: str | None = None
    email: str | None = None
    offset: int = 0
    limit: int = 100
class Login(msgspec.Struct):
    password: str
    username: str | None = None
    email: str | None = None

class BanUser(msgspec.Struct):
    user_id: int
    reason: str
