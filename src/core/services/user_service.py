from src.schemas.core.user import MUTABLE_USER_KEYS, User, GetUser, CreateUser, UserResponse, DeleteUser, ModifyUser
from src.schemas.core.request import Error, Result
import msgspec

async def get_user(data: GetUser) -> Result | Error:
    # TODO: Implement database fetch here
    user_data = UserResponse(data.user_id, "RealUser123", "eyTYSYS89asuAJUS0a9s7a76y48uihEWIUy")
    return Result("SUCCESS", f"User found with ID {data.user_id}", user_data, 200)

async def create_user(data: CreateUser) -> Result | Error:
    user_data = UserResponse(1, "RealUser123", "eyTYSYS89asuAJUS0a9s7a76y48uihEWIUy")
    return Result("SUCCESS", f"User created with ID {1}", user_data, 201)

async def delete_user(data: DeleteUser) -> Result | Error:
    return Result("SUCCESS", f"User with ID {data.user_id} deleted", None, 200)

async def modify_user(data: ModifyUser) -> Result | Error:
    modify_dict = msgspec.structs.asdict(data)
    modifications = modify_dict.get("modifications")

    illegal_keys = []
    for key in modifications.keys(): # type: ignore
        if key not in MUTABLE_USER_KEYS:
            illegal_keys.insert(0, key)

    if len(illegal_keys) >= 1:
        return Error("BAD_MODIFY", f"Failed to alter user due to illegal key changes: {illegal_keys}", 403)
    
    user_data = UserResponse(data.user_id, "RealUser123", "eyTYSYS89asuAJUS0a9s7a76y48uihEWIUy")
    return Result("SUCCESS", f"User with ID {data.user_id} was modified", user_data, 200)