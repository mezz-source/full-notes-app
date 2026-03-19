from fastapi.responses import JSONResponse
from src.schemas.core.request import Error, Result
from typing import Any, Dict
import msgspec

async def handle_response(result_head: str | None, response: Error | Result) -> JSONResponse:
    """Returns a JSON response with the response data returned from the core"""
    if isinstance(response, Error):
        return await error_response(
            response.code, response.message, status_code=response.status_code or 400)
    return await result_response(
        result_head, response.result, status_code=response.status_code or 200,
        code=response.code, message=response.message)

async def create_dictionary(classObject: msgspec.Struct) -> dict[str, Any]:
    print(classObject, type(classObject))
    try:
        return msgspec.structs.asdict(classObject)
    except Exception as exc:
        return {"error": str(exc)}
        
async def handle_request(request_head: str | None, targetClass, targetServiceFunction, **kwargs):
    """
    Generic handler for API requests.
    
    EXAMPLE:
    targetClass = GetUser
    targetServiceFunction = UserService.get_user
    
    # For path params or simple args
    return await handle_request("user", UserCore.GetUser, UserService.get_user, user_id=user_id)
    
    # For request bodies (Pydantic models)
    return await handle_request("user", UserCore.CreateUser, UserService.create_user, **request.model_dump())
    """
    request = targetClass(**kwargs)
    result = await targetServiceFunction(request)
    return await handle_response(request_head, result)

async def error_response(error_code: str, error_info: str, status_code: int = 400) -> JSONResponse:
    """Returns a JSON Response intended for errors in requests"""
    return JSONResponse(
        {"error": {
            "code": error_code,
            "info": error_info}},
        status_code=status_code
    )

async def result_response(
        result_head: str | None = "result", result_class: msgspec.Struct | dict | None = dict(), status_code: int = 200,
        code: str = "SUCCESS", message: str = "The operation completed successfully") -> JSONResponse:
    """Returns a JSON Response intended for returning information"""
    
    if isinstance(result_class, msgspec.Struct):
        result = await create_dictionary(result_class)
    elif isinstance(result_class, dict):
        result = result_class
    else:
        result = None

    response = dict(code=str(code), message=str(message))
    # Add a result/response header if we have a result and head
    if result_head and result:
        response[result_head] = result # type: ignore

    return JSONResponse(response, status_code=int(status_code) or 500)
