from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Dict, Any

class CreateUser(BaseModel):
    username: str
    password: str
    email: EmailStr
    # birthday: datetime

class ModifyUser(BaseModel):
    user_id: int
    modifications: Dict[str, Any]

class DeleteUser(BaseModel):
    user_id: int

class SearchUser(BaseModel):
    user_id: int | None
    username: str | None
