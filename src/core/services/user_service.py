import msgspec
from typing import List
from sqlalchemy.exc import IntegrityError
from src.util.key import validate as validate_keys
from src.security.hash import hash_password
from src.schemas.core.user import MUTABLE_USER_KEYS, VALID_ROLES, GetUser, CreateUser, \
    DeleteUser, GetUserUsername, ModifyUser, UserQuery, AddRole, RemoveRole, UpdateRoles, Login
from src.schemas.core.request import Error, Result
from sqlalchemy.orm import Session
from src.security.authentication import create_access_token, get_user_dict, async_create_access_token
from src.security.hash import hash_password
from src.policy.policy import Permission, can_ban_user, can_manage_user, can_view_user, has_permission

from src.util.string_list import add_item, remove_item, add_many_items, remove_many_items, parse_string_list, filter_valid_items, remove_items_force
from src.util.responses import model_to_dict
class UserService():
    def __init__(self, user_repo, note_repo):
        self.user_repo = user_repo
        self.note_repo = note_repo

    async def query_users(self, data: UserQuery, acting_user: dict | None = None) -> Result | Error:
        if not acting_user:
            return Error("UNAUTHORIZED", "Authentication required to query users", 401)

        is_admin_view = await has_permission(acting_user, Permission.MANAGE_ANY_USER)
        safe_email_filter = data.email if is_admin_view else None

        results = await self.user_repo.query(
            offset=data.offset,
            limit=data.limit,
            username=data.username  or None,
            username_contains = data.username_contains or None,
            email=safe_email_filter,
        )

        response = []

        # Response head contains pagination info and total count of results for client convenience, but is not required for clients to function properly. Clients should be able to handle the absence of this head gracefully.
        response.append({
            "pagination": True,
            "count": len(results),
            "offset": data.offset,
            "limit": data.limit,
            "view_type": "admin" if is_admin_view else "standard",
            "query": {"username": data.username, "email": safe_email_filter, "username_contains": data.username_contains}
        })

        for result in results:
            user_dict = await model_to_dict(result)
            if await can_view_user(acting_user, user_dict):
                if not is_admin_view:
                    user_dict["email"] = None
                response.append(user_dict)
        
        return Result("SUCCESS", "Users retrieved successfully", response, 200)
    
    async def get_user_username(self, data: GetUserUsername, acting_user: dict | None = None) -> Result | Error:
        if not acting_user:
            return Error("UNAUTHORIZED", "Authentication required to get user", 401)
        
        result = await self.user_repo.get(data.user_id)
        if not result:
            return Error("NOT_FOUND", f"User with ID {data.user_id} was not found", 404)
        
        viewed_user = await model_to_dict(result)
        if not await can_view_user(acting_user, viewed_user):
            return Error("FORBIDDEN", "You do not have permission to view this user", 403)
        return Result("SUCCESS", f"User with ID {data.user_id} was found", {"username": viewed_user.get("username")}, 200)

    async def get_user(self, data: GetUser, acting_user: dict | None = None) -> Result | Error:
        if not acting_user:
            return Error("UNAUTHORIZED", "Authentication required to get user", 401)
        
        result = await self.user_repo.get(data.user_id)
        if not result:
            return Error("NOT_FOUND", f"User with ID {data.user_id} was not found", 404)
        
        viewed_user = await model_to_dict(result)
        if not await can_view_user(acting_user, viewed_user):
            return Error("FORBIDDEN", "You do not have permission to view this user", 403)

        return Result("SUCCESS", f"User with ID {data.user_id} was found", viewed_user, 200)

    async def create_user(self, data: CreateUser, acting_user: dict | None = None) -> Result | Error:
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
        token = await async_create_access_token(data={"sub": str(result.id)})
        user_data["token"] = token
    
        return Result("SUCCESS", f"User created with ID {1}", user_data, 201)
    
    async def delete_user(self, data: DeleteUser, acting_user: dict | None = None) -> Result | Error:
        if not acting_user:
            return Error("UNAUTHORIZED", "Authentication required to delete user", 401)

        target_user_model = await self.user_repo.get(data.user_id)
        if not target_user_model:
            return Error("NOT_FOUND", f"User with ID {data.user_id} was not found", 404)

        target_user = await model_to_dict(target_user_model)
        if not await can_manage_user(acting_user, target_user):
            return Error("FORBIDDEN", "You do not have permission to delete this user", 403)

        success = await self.user_repo.delete(data.user_id)
        if not success:
            return Error("INTERNAL_ERROR", f"Failed to delete user with ID {data.user_id}", 500)
        return Result("SUCCESS", f"User with ID {data.user_id} was deleted", None, 200)

    async def add_role(self, data: AddRole, acting_user: dict | None = None) -> Result | Error:
        if not acting_user:
            return Error("UNAUTHORIZED", "Authentication required to add role to user", 401)

        if not await has_permission(acting_user, Permission.MANAGE_ANY_USER):
            return Error("FORBIDDEN", "You do not have permission to add role to users", 403)

        user_id = data.user_id
        roles_to_add = data.roles

        user = await self.user_repo.get(user_id)
        if not user:
            return Error("NOT_FOUND", f"User with ID {user_id} was not found", 404)

        target_user = await model_to_dict(user)
        if not await can_manage_user(acting_user, target_user):
            return Error("FORBIDDEN", "You do not have permission to add role to this user", 403)
        
        # Validate all roles
        validation = await validate_keys(VALID_ROLES, roles_to_add)
        valid, illegal_keys = validation.get("valid"), validation.get("illegal_keys")
        if not valid:
            return Error("INVALID_ROLE", f"One or more roles are not valid: {illegal_keys}", 422)

        # Parse existing roles and add new ones
        existing_roles = await parse_string_list(user.roles)
        for role in roles_to_add:
            if role not in existing_roles:
                existing_roles.append(role)
        
        new_roles = ",".join(existing_roles)
        result = await self.user_repo.modify(user_id, {"roles": new_roles})
        user_data = await model_to_dict(result)
        return Result("SUCCESS", f"Roles added to user with ID {user_id}", user_data, 200)
        
        
    async def remove_role(self, data: RemoveRole, acting_user: dict | None = None) -> Result | Error:
        if not acting_user:
            return Error("UNAUTHORIZED", "Authentication required to remove role from user", 401)

        if not await has_permission(acting_user, Permission.MANAGE_ANY_USER):
            return Error("FORBIDDEN", "You do not have permission to remove roles from users", 403)

        user_id = data.user_id
        roles_to_remove = data.roles

        user = await self.user_repo.get(user_id)
        if not user:
            return Error("NOT_FOUND", f"User with ID {user_id} was not found", 404)

        target_user = await model_to_dict(user)
        if not await can_manage_user(acting_user, target_user):
            return Error("FORBIDDEN", "You do not have permission to remove role from this user", 403)
        
        # Validate all roles
        validation = await validate_keys(VALID_ROLES, roles_to_remove)
        valid, illegal_keys = validation.get("valid"), validation.get("illegal_keys")
        if not valid:
            return Error("INVALID_ROLE", f"One or more roles are not valid: {illegal_keys}", 422)

        # Parse existing roles and remove specified ones
        new_roles = await remove_many_items(user.roles, roles_to_remove)
        result = await self.user_repo.modify(user_id, {"roles": new_roles})
        user_data = await model_to_dict(result)
        return Result("SUCCESS", f"Roles removed from user with ID {user_id}", user_data, 200)

    async def update_roles(self, data: UpdateRoles, acting_user: dict | None = None) -> Result | Error:
        if not acting_user:
            return Error("UNAUTHORIZED", "Authentication required to update user roles", 401)

        if not await has_permission(acting_user, Permission.MANAGE_ANY_USER):
            return Error("FORBIDDEN", "You do not have permission to update user roles", 403)

        user_id = data.user_id
        new_roles = data.new_roles

        user = await self.user_repo.get(user_id)
        if not user:
            return Error("NOT_FOUND", f"User with ID {user_id} was not found", 404)

        target_user = await model_to_dict(user)
        if not await can_manage_user(acting_user, target_user):
            return Error("FORBIDDEN", "You do not have permission to update roles for this user", 403)
        
        validation = await validate_keys(VALID_ROLES, new_roles)
        valid, illegal_keys = validation.get("valid"), validation.get("illegal_keys")
        if not valid:
            return Error("INVALID_ROLES", f"One or more roles are not valid: {illegal_keys}", 422)

        if not await has_permission(acting_user, Permission.MANAGE_ANY_USER):
            return Error("FORBIDDEN", "You do not have permission to update user roles", 403)

        result = await self.user_repo.modify(user_id, {"roles": ",".join(new_roles)})
        user_data = await model_to_dict(result)
        return Result("SUCCESS", f"Roles for user with ID {user_id} was updated", user_data, 200)
    
    async def modify_user(self, data: ModifyUser, acting_user: dict | None = None) -> Result | Error:
        if not acting_user:
            return Error("UNAUTHORIZED", "Authentication required to modify user", 401)

        target_user_model = await self.user_repo.get(data.user_id)
        if not target_user_model:
            return Error("NOT_FOUND", f"User with ID {data.user_id} was not found", 404)

        if not await has_permission(acting_user, Permission.MANAGE_ANY_USER):
            return Error("FORBIDDEN", "You do not have permission to modify users", 403)

        target_user = await model_to_dict(target_user_model)
        if not await can_manage_user(acting_user, target_user):
            return Error("FORBIDDEN", "You do not have permission to modify this user", 403)

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
    
    async def login(self, data: Login, acting_user: dict | None = None) -> Result | Error:
        if not data.username and not data.email:
            return Error("BAD_REQUEST", "Username or email must be provided for login", 400)
        
        user = None
        if data.username:
            user = await self.user_repo.get_by_username(data.username)
        if data.email:
            user = await self.user_repo.get_by_email(data.email)

        if not user:
            return Error("NOT_FOUND", f"User with username {data.username} was not found", 404)
        
        print("Person tryna login:", await model_to_dict(user))

        password_hash = await hash_password(data.password)
        if password_hash != user.password_hash:
            return Error("UNAUTHORIZED", "Invalid credentials", 401)
        
        token = create_access_token(data={"sub": str(user.id)}) # REPLACE WITH ACTUAL USER ID
        return Result("SUCCESS", f"User with ID {user.id} authenticated successfully", {"token": token}, 200)