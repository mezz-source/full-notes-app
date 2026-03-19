from fastapi import APIRouter, Depends
from src.util.responses import handle_request
from fastapi.responses import PlainTextResponse

# Schema related
from src.schemas.user import CreateUser, ModifyUser

# Service/Core related
import src.schemas.core.user as UserCore
import src.core.services.user_service as UserService

router = APIRouter(prefix="/users")

DEFAULT_HEADER = "user"

@router.get("/")
async def root():
    """Root"""
    return PlainTextResponse("you've indeed hit the users api congratulations")

@router.get("/{user_id}")
async def get_user(user_id: int):
    return await handle_request(DEFAULT_HEADER, UserCore.GetUser, UserService.get_user, user_id=user_id)

@router.delete("/{user_id}")
async def delete_user(user_id: int):
    return await handle_request(DEFAULT_HEADER, UserCore.DeleteUser, UserService.delete_user, user_id=user_id)

@router.patch("/")
async def update_user(request: ModifyUser):
    return await handle_request(DEFAULT_HEADER, UserCore.ModifyUser, UserService.modify_user, **request.model_dump())

@router.post("/")
async def create_user(request: CreateUser): 
    return await handle_request(DEFAULT_HEADER, UserCore.CreateUser, UserService.create_user, **request.model_dump())