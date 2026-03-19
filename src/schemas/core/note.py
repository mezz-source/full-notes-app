from typing import Dict, Any
from datetime import datetime
import msgspec

MUTABLE_USER_KEYS = {}

class Note(msgspec.Struct):
    author_id: int
    title: str
    content: str
    time_written: datetime
    flags: str