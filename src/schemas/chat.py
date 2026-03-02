from pydantic import BaseModel, Field
from typing import Optional, Literal, Union, Dict, Any

class ChatRequest(BaseModel):
    """
    Schema for incoming chat requests.
    """
    message: str = Field(..., description="The message from the user")
    thread_id: Optional[str] = Field(None, description="The unique thread ID for the conversation")

class ChatBaseEvent(BaseModel):
    """
    Base class for all SSE chat events.
    """
    type: str

class ChatTokenEvent(ChatBaseEvent):
    """
    Event containing a single token from the LLM.
    """
    type: Literal["token"] = "token"
    content: str

class ChatStatusEvent(ChatBaseEvent):
    """
    Event containing a status update from the graph.
    """
    type: Literal["status"] = "status"
    content: str

class ChatInterruptEvent(ChatBaseEvent):
    """
    Event indicating the graph is paused and waiting for user input.
    """
    type: Literal["interrupt"] = "interrupt"
    content: str
    data: Optional[Dict[str, Any]] = None

class ChatUpdateEvent(ChatBaseEvent):
    """
    Event for "Silent Updates" (e.g. background report commits).
    """
    type: Literal["update"] = "update"
    update_type: str
    thread_id: str
    report_id: Optional[int] = None
    data: Optional[Dict[str, Any]] = None

class ChatErrorEvent(ChatBaseEvent):
    """
    Event indicating an error during processing.
    """
    type: Literal["error"] = "error"
    content: str

class ChatResumeRequest(BaseModel):
    """
    Schema for resuming an interrupted chat.
    """
    user_response: str = Field(..., description="The user's response to the interrupt/checkpoint")

ChatSSEEvent = Union[ChatTokenEvent, ChatStatusEvent, ChatInterruptEvent, ChatUpdateEvent, ChatErrorEvent]
