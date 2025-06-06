from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class SearchBase(BaseModel):
    query: str


class SearchCreate(SearchBase):
    pass


class SearchOut(SearchBase):
    id: int
    response: str
    owner_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True
