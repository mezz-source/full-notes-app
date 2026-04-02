from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1.routes.users import router as v1_user_router
from src.api.v1.routes.notes import router as v1_note_router
from src.api.v1.routes.secrets import router as secret_router
from src.api.v1.routes.realtime import router as realtime_router

def create_app() -> FastAPI:
    """Creates the main FastAPI App"""
    app = FastAPI()
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
        allow_headers=["*"],  # Allow all headers
    )
    
    app.include_router(v1_user_router, prefix="/api/v1")
    app.include_router(v1_note_router, prefix="/api/v1")
    app.include_router(secret_router, prefix="/api/v1")
    app.include_router(realtime_router, prefix="/api/v1")
    return app
