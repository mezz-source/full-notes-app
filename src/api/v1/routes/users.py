from fastapi import APIRouter, Query, Depends
from typing import List
from src.repositories.note_repo import NoteRepository
from src.repositories.user_repo import UserRepository
from src.util.responses import handle_request
from fastapi.responses import PlainTextResponse
from src.security.authentication import get_current_user

from src.db.session import get_db
from sqlalchemy.orm import Session

# Schema related
from src.schemas.user import CreateUser, ModifyUser, SearchUser, AddRole, RemoveRole, UpdateRoles, UserLogin

# Service/Core related
import src.schemas.core.user as UserCore
from src.core.services.user_service import UserService
from src.repositories.note_repo import NoteRepository

router = APIRouter(prefix="/users")

DEFAULT_HEADER = "user"
DEFAULT_QUERY_HEADER = "user_query"

async def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(
        user_repo=UserRepository(db),
        note_repo=NoteRepository(db),
    )

@router.get("/")
async def root():
    """Root"""
    return PlainTextResponse("you've indeed hit the users api congratulations")

@router.post("/login")
async def login(request: UserLogin, service: UserService = Depends(get_user_service)):
    return await handle_request(DEFAULT_HEADER, None, UserCore.Login, service.login, **request.model_dump())

@router.post("/")
async def create_user(request: CreateUser, service: UserService = Depends(get_user_service) 
                            ):
    return await handle_request(DEFAULT_HEADER, None, UserCore.CreateUser, service.create_user, **request.model_dump())

@router.post("/search")
async def search_users(
    user_query: SearchUser,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    service: UserService = Depends(get_user_service), 
    current_user: dict = Depends(get_current_user)
):
    return await handle_request(DEFAULT_QUERY_HEADER, current_user, UserCore.UserQuery, service.query_users, \
                                **user_query.model_dump(), offset=offset, limit=limit)

@router.put("/roles")
async def update_user_roles(request: UpdateRoles, service: UserService = Depends(get_user_service) \
                            , current_user: dict = Depends(get_current_user)):
    return await handle_request(DEFAULT_HEADER, current_user, UserCore.UpdateRoles, service.update_roles, **request.model_dump())

@router.post("/roles")
async def add_user_role(
    request: AddRole,
    service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    return await handle_request(DEFAULT_HEADER, current_user, UserCore.AddRole, service.add_role, **request.model_dump())

@router.delete("/roles")
async def remove_user_role(
    request: RemoveRole,
    service: UserService = Depends(get_user_service), 
    current_user: dict = Depends(get_current_user)
):
    return await handle_request(DEFAULT_HEADER, current_user, UserCore.RemoveRole, service.remove_role, **request.model_dump())

@router.get("/{user_id}")
async def get_user(
    user_id: int | str,
    service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    if user_id == "me":
        user_id = current_user.get("id")  # type: ignore
    elif isinstance(user_id, str):
        try:
            user_id = int(user_id)
        except ValueError:
            return PlainTextResponse("Only 'me' or integers are allowed for user IDs", status_code=400)
        
    return await handle_request(DEFAULT_HEADER, current_user, UserCore.GetUser, service.get_user, user_id=user_id)

@router.get("/{user_id}/username")
async def get_user_username(
    user_id: int | str,
    service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    if user_id == "me":
        user_id = current_user.get("id")  # type: ignore
    elif isinstance(user_id, str):
        try:
            user_id = int(user_id)
        except ValueError:
            return PlainTextResponse("Only 'me' or integers are allowed for user IDs", status_code=400)

    return await handle_request(DEFAULT_HEADER, current_user, UserCore.GetUserUsername, service.get_user_username, user_id=user_id)

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    return await handle_request(DEFAULT_HEADER, current_user, UserCore.DeleteUser, service.delete_user, user_id=user_id)

@router.patch("/")
async def update_user(request: ModifyUser, service: UserService = Depends(get_user_service) \
                            , current_user: dict = Depends(get_current_user)):
    return await handle_request(DEFAULT_HEADER, current_user, UserCore.ModifyUser, service.modify_user, **request.model_dump())
