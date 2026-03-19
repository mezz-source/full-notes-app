from typing import Dict, Any
from datetime import datetime
import msgspec

MUTABLE_USER_KEYS = {"username", "email", "birthday"}

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

class ModifyUser(msgspec.Struct):
    user_id: int
    modifications: Dict[str, Any]

class UserResponse(msgspec.Struct):
    user_id: int
    username: str
    token: str