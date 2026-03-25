from typing import Dict, Any, List
from datetime import datetime
import msgspec

MUTABLE_USER_KEYS = {"username", "email", "birthday"}
VALID_ROLES = {"admin", "user", "moderator"}
class User(msgspec.Struct):
    user_id: int
    username: str
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
    role: str
class AddRole(msgspec.Struct):
    user_id: int
    role: str

class ModifyUser(msgspec.Struct):
    user_id: int
    modifications: Dict[str, Any]

class UserResponse(msgspec.Struct):
    user_id: int
    username: str
    token: str
    
class UserQuery(msgspec.Struct):
    username_contains: str | None = None
    username: str | None = None
    email: str | None = None
    offset: int = 0
    limit: int = 100