from fastapi import APIRouter
from src.schemas.core.request import Error, Result
from starlette.responses import FileResponse, HTMLResponse, PlainTextResponse, JSONResponse
from random import choice
import json

router = APIRouter(prefix="/secrets")

@router.get("/homer")
async def homer_simpson(secret_key: str):
    if secret_key == "beer":
        return FileResponse(
            "resources/secrets/homer/beer.mp3",
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline"}
        )

    if secret_key == "donut":
        return PlainTextResponse("Mmm... Donuts!")
    elif secret_key == "quotes":
        with open("resources/secrets/homer/quotes.json", "r") as f:
            data = json.load(f)
        quotes = data.get("quotes")
        return PlainTextResponse(choice(quotes)) if quotes else PlainTextResponse("No quotes found.")
    else:
        return JSONResponse({"code": "INVALID_KEY", "info": "You are not authorized to access this resource."}, status_code=403)

@router.get("/coffee")
async def teapot():
    return JSONResponse({"code": "I_AM_A_TEAPOT", "info": "I'm a teapot, I cannot brew coffee."}, status_code=418)