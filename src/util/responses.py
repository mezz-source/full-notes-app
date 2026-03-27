from fastapi.responses import JSONResponse
from src.schemas.core.request import Error, Result
from typing import Any, Dict
from datetime import datetime, date, time
from decimal import Decimal
from uuid import UUID
from enum import Enum
from sqlalchemy.orm import Session
import msgspec

SENSITIVE_KEYS = {"password_hash", "password"}
COMMA_SEPARATED_FIELDS = {"flags", "roles"}

def _deserialize_comma_separated(field_name: str, value: str) -> list[str] | str:
    """Convert comma-separated string fields into lists for specific known fields.
    
    Only deserializes recognized fields to avoid splitting content bodies.
    """
    if field_name in COMMA_SEPARATED_FIELDS and isinstance(value, str):
        # Split and strip whitespace, filter out empty strings
        return [item.strip() for item in value.split(",") if item.strip()]
    return value

async def handle_response(result_head: str | None, response: Error | Result) -> JSONResponse:
    """Returns a JSON response with the response data returned from the core"""
    if isinstance(response, Error):
        return await error_response(
            response.code, response.message, status_code=response.status_code or 400)
    return await result_response(
        result_head, response.result, status_code=response.status_code or 200,
        code=response.code, message=response.message)
        
async def handle_request(request_head: str | None, current_user: dict | None, targetClass, targetServiceFunction, **kwargs):
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
    try:
        if targetClass:
            request = targetClass(**kwargs)
            result = await targetServiceFunction(request, acting_user=current_user) if current_user else await targetServiceFunction(request)
        else:
            result = await targetServiceFunction(**kwargs, acting_user=current_user) if current_user else await targetServiceFunction(**kwargs)
    except Exception as exc:
        print("Error:", str(exc))
        return await error_response("REQUEST_FAILED", str(exc), status_code=500)
    
    return await handle_response(request_head, result)

async def error_response(error_code: str, error_info: str, status_code: int = 400) -> JSONResponse:
    """Returns a JSON Response intended for errors in requests"""
    return JSONResponse(
        {"code": error_code, "info": error_info},
        status_code=status_code
    )

async def make_serializable(obj: Any) -> Any:
    """Recursively converts non-serializable objects to serializable types"""
    if obj is None:
        return None
    elif isinstance(obj, (str, int, float, bool)):
        return obj
    elif isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    elif isinstance(obj, (Decimal, UUID)):
        return str(obj)
    elif isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, dict):
        result_dict = {}
        for k, v in obj.items():
            # First deserialize comma-separated fields into lists
            v = _deserialize_comma_separated(k, v)
            # Then recursively serialize the value
            result_dict[k] = await make_serializable(v)
        return result_dict
    elif isinstance(obj, (list, tuple)):
        return [await make_serializable(item) for item in obj]
    elif isinstance(obj, msgspec.Struct):
        return await make_serializable(msgspec.structs.asdict(obj))
    else:
        # Fallback for unknown types
        try:
            return str(obj)
        except Exception:
            return None

async def create_dictionary(classObject: msgspec.Struct) -> dict[str, Any]:
    try:
        data = msgspec.structs.asdict(classObject)
        return await make_serializable(data)
    except Exception as exc:
        return {"error": str(exc)}

async def result_response(
        result_head: str | None = "result", result_class: msgspec.Struct | dict | None = dict(), status_code: int = 200,
        code: str = "SUCCESS", message: str = "The operation completed successfully") -> JSONResponse:
    """Returns a JSON Response intended for returning information"""
    
    

    if isinstance(result_class, msgspec.Struct):
        result = await create_dictionary(result_class)
    else:
        result = await make_serializable(result_class)

    response = dict(code=str(code), message=str(message), pagination=None)

    if isinstance(result, list) and result and isinstance(result[0], dict) and "pagination" in result[0]:
        # Checks to see if the result is a paginated query and includes it in the response dictionary
        del result[0]["pagination"]
        response["pagination"] = result[0] # type: ignore
        del result[0]

    # Include empty collections (e.g., []) so clients always receive a stable payload shape.
    if result_head and result is not None:
        response[result_head] = result # type: ignore

    return JSONResponse(response, status_code=int(status_code) or 500)

async def model_to_dict(model) -> dict:
        """Convert a SQLAlchemy model instance to a dictionary, converting datetime to ISO format."""
        result = {}
        for column in model.__table__.columns:
            if column.name in SENSITIVE_KEYS:
                continue

            value = getattr(model, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result