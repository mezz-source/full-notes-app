from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, PlainTextResponse

router = APIRouter(prefix="users")

@router.get("/")
async def root():
    return PlainTextResponse("you've indeed hit the users api congratulations")

@router.get("/{user_id}")
async def get_user(user_id: int):
    return JSONResponse({"user": {"id": 1}})

@router.post("/")
async def create_user(request):
    pass

@router.delete("/")
async def delete_user(request):
    pass

@router.patch("/{user_id}")
async def update_user(user_id: int, request):
    return JSONResponse(
        {"error": "Not implemented"}
    )