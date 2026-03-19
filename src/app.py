from fastapi import FastAPI


def create_app() -> FastAPI:
    """Creates the main FastAPI App"""
    app = FastAPI()

    return app