from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Dict, Any, List

class CreateUser(BaseModel):
    username: str
    password: str
    email: EmailStr

    @field_validator("username")
    @classmethod
    def good_username(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if len(v) > 20:
            raise ValueError("Username must be at most 20 characters long")
        if not v.replace("_", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return v
    
    @field_validator("password")
    @classmethod
    def strong_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v


    # birthday: datetime

class ModifyUser(BaseModel):
    user_id: int
    modifications: Dict[str, Any]
class DeleteUser(BaseModel):
    user_id: int
class SearchUser(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    username_contains: str | None = None
class AddRole(BaseModel):
    user_id: int
    roles: List[str]

class UpdateRoles(BaseModel):
    user_id: int
    new_roles: List[str]
class RemoveRole(BaseModel):
    user_id: int
    roles: List[str]

class UserLogin(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str