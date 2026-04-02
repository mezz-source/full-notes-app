from pydantic import BaseModel
from typing import Literal

class BanHammered(BaseModel):
    reason: str
    banned_username: str
    actor_username: str