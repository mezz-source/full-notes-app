import msgspec
from typing import List
from sqlalchemy.exc import IntegrityError
from src.util.key import validate as validate_keys
from src.security.hash import hash_password
from src.schemas.core.user import MUTABLE_USER_KEYS, VALID_ROLES, GetUser, CreateUser, \
    DeleteUser, ModifyUser, UserQuery
from src.schemas.core.request import Error, Result
from sqlalchemy.orm import Session

from src.util.string_list import add_item, remove_item, add_many_items, remove_many_items
from src.util.responses import model_to_dict
class UserService():
    def __init__(self, user_repo, note_repo):
        self.user_repo = user_repo
        self.note_repo = note_repo

    async def query_users(self, data: UserQuery) -> Result | Error:
        results = await self.user_repo.query(
            offset=data.offset,
            limit=data.limit,
            username=data.username  or None,
            username_contains = data.username_contains or None,
            email=data.email        or None,
        )

        print(results)

        response = []

        # Response head contains pagination info and total count of results for client convenience, but is not required for clients to function properly. Clients should be able to handle the absence of this head gracefully.
        response.append({
            "pagination": True,
            "count": len(results),
            "offset": data.offset,
            "limit": data.limit,
            "query": {"username": data.username, "email": data.email, "username_contains": data.username_contains}
        })

        for result in results:
            user_dict = await model_to_dict(result)
            response.append(user_dict)
        
        return Result("SUCCESS", "Users retrieved successfully", response, 200)
    
    async def get_user(self, data: GetUser) -> Result | Error:
        result = await self.user_repo.get(data.user_id)
        if not result:
            return Error("NOT_FOUND", f"User with ID {data.user_id} was not found", 404)
        
        response = await model_to_dict(result)
        return Result("SUCCESS", f"User with ID {data.user_id} was found", response, 200)

    async def create_user(self, data: CreateUser) -> Result | Error:
        # Use our current hasher to avoid getting John Doe's password leaked
        # I don't like him that much but I also don't want his password leaked
        password_hash = await hash_password(data.password)
        
        try:
            result = await self.user_repo.create(email=data.email, username=data.username, password_hash=password_hash)
        except IntegrityError as e:
            if "UNIQUE" in str(e):
                return Error("USER_EXISTS", "A user with the given email or username already exists", 409)
            return Error("INTERNAL_ERROR", f"Failed to create user: {str(e)}", 500)
        user_data = await model_to_dict(result)
    
        return Result("SUCCESS", f"User created with ID {1}", user_data, 201)
    
    async def delete_user(self, data: DeleteUser) -> Result | Error:
        success = await self.user_repo.delete(data.user_id)
        if not success:
            return Error("NOT_FOUND", f"User with ID {data.user_id} was not found", 404)
        return Result("SUCCESS", f"User with ID {data.user_id} was deleted", None, 200)

    async def add_role(self, user_id: int, role: str) -> Result | Error:
        user = await self.user_repo.get(user_id)
        if not user:
            return Error("NOT_FOUND", f"User with ID {user_id} was not found", 404)
        
        if role not in VALID_ROLES:
            return Error("INVALID_ROLE", f"Role {role} is not a valid role", 422)

        roles = str(user.roles)
        if role in roles.split(","):
            return Error("ROLE_EXISTS", f"User with ID {user_id} already has role {role}", 409)
        new_roles = add_item(roles, role)

        result = await self.user_repo.modify(user_id, {"roles": new_roles})
        return Result("SUCCESS", f"Roles for user with ID {user_id} was updated", result, 200)
        
        
    async def remove_role(self, user_id: int, role: str) -> Result | Error:
        user = await self.user_repo.get(user_id)
        if not user:
            return Error("NOT_FOUND", f"User with ID {user_id} was not found", 404)
        
        if role not in VALID_ROLES:
            return Error("INVALID_ROLE", f"Role {role} is not a valid role", 422)

        roles = str(user.roles)
        if role not in roles.split(","):
            return Error("ROLE_NOT_FOUND", f"User with ID {user_id} does not have role {role}", 404)
        new_roles = remove_item(roles, role)
        result = await self.user_repo.modify(user_id, {"roles": new_roles})
        return Result("SUCCESS", f"Role removed from user with ID {user_id}", result, 200)

    async def update_roles(self, user_id: int, new_roles: List[str]) -> Result | Error:
        user = await self.user_repo.get(user_id)
        if not user:
            return Error("NOT_FOUND", f"User with ID {user_id} was not found", 404)
        
        valid, illegal_keys = await validate_keys(VALID_ROLES, new_roles)
        if not valid:
            return Error("INVALID_ROLES", f"One or more roles are not valid: {illegal_keys}", 422)

        result = await self.user_repo.modify(user_id, {"roles": ",".join(new_roles)})
        return Result("SUCCESS", f"Roles for user with ID {user_id} was updated", result, 200)
    
    async def modify_user(self, data: ModifyUser) -> Result | Error:
        modify_dict = msgspec.structs.asdict(data)
        modifications = modify_dict.get("modifications")

        result = await validate_keys(MUTABLE_USER_KEYS, modifications.keys()) # type: ignore
        valid, illegal_keys = result.get("valid"), result.get("illegal_keys")

        if not valid:
            return Error("BAD_MODIFY", f"Failed to alter user due to illegal key changes: {illegal_keys}", 422) 

        result = await self.user_repo.modify(data.user_id, modifications)
        if not result:
            return Error("NOT_FOUND", f"User with ID {data.user_id} was not found", 404)
        
        user_data = await model_to_dict(result)
        return Result("SUCCESS", f"User with ID {data.user_id} was modified", user_data, 200)