from datetime import datetime

from pydantic import BaseModel


class SearchBase(BaseModel):
    query: str
    database: bool = False


class SearchCreate(SearchBase):
    pass


class SearchOut(SearchBase):
    id: int
    response: str
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True
