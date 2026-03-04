from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ThreadBase(BaseModel):
    id: str
    title: Optional[str] = "New Conversation"
    created_at: datetime
    updated_at: datetime

class ThreadListResponse(BaseModel):
    threads: List[ThreadBase]
    total: int

class MessageSchema(BaseModel):
    id: str
    role: str
    content: str
    timestamp: datetime

class CursorInfo(BaseModel):
    next_cursor: Optional[str] = None
    has_more: bool

class HistoryResponse(BaseModel):
    messages: List[MessageSchema]
    thread_id: str
    cursor: CursorInfo

class ThreadHistoryResponse(BaseModel):
    messages: List[MessageSchema]
    thread_id: str

class ThreadRunStreamRequest(BaseModel):
    input: Optional[dict] = None
    stream_mode: List[str] = ["messages"]
    config: Optional[dict] = None
    checkpoint_id: Optional[str] = None
