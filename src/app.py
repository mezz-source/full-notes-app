from fastapi import FastAPI
from src.api.v1.routes.users import router as v1_user_router
from src.api.v1.routes.notes import router as v1_note_router
from src.api.v1.routes.secrets import router as secret_router

def create_app() -> FastAPI:
    """Creates the main FastAPI App"""
    app = FastAPI()
    app.include_router(v1_user_router, prefix="/api/v1")
    app.include_router(v1_note_router, prefix="/api/v1")
    app.include_router(secret_router, prefix="/api/v1")
    return app
