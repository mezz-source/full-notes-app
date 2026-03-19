from fastapi.responses import JSONResponse

async def error_response(error_code: str, error_info: str) -> JSONResponse:
    return JSONResponse(
        {"error": {
            "code": error_code,
            "info": error_info}}
    )

async def result_response(result_head: str, result_object) -> JSONResponse:
    return JSONResponse(
        { result_head: {
            "id": 234382,
            "first_name": "caleb",
            "last_name": "not implemented" }
        }
    )