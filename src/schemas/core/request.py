import msgspec
from typing import Any

class Result(msgspec.Struct):
    code: str
    message: str
    result: Any
    status_code: int

class Error(msgspec.Struct):
    code: str
    message: str
    status_code: int