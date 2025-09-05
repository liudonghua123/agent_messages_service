from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Union

class ChatCreate(BaseModel):
    session: str
    question: str
    answer: str
    datetime: datetime
    user: str
    fullfill: bool = False
    process_time: int = 0

class ChatResponse(BaseModel):
    id: int
    session: str
    question: str
    answer: str
    datetime: datetime
    user: str
    fullfill: bool
    process_time: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SearchCondition(BaseModel):
    field: str
    operator: str  # eq, ne, gt, ge, lt, le, like, between
    value: Union[str, int, float, datetime]
    value2: Optional[Union[str, int, float, datetime]] = None

class SearchRequest(BaseModel):
    conditions: List[SearchCondition] = []
    page: int = 1
    page_size: int = 20

class StatusResponse(BaseModel):
    status: str
    uptime: str
    version: str
    database_type: str
    total_chats: int