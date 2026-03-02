from pydantic import BaseModel, Field
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
    role: str
    content: str
    timestamp: datetime

class ThreadHistoryResponse(BaseModel):
    messages: List[MessageSchema]
    thread_id: str
