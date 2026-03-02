import json
import asyncio
import logging
from uuid import uuid4
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import APIRouter, Request, Header, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db
from src.schemas.chat import ChatRequest, ChatTokenEvent, ChatStatusEvent, ChatErrorEvent
from src.graph.graph import create_graph
from src.graph.persistence import get_checkpointer
from src.services.context_injection import get_user_context_data

router = APIRouter(tags=["Chat"])
logger = logging.getLogger(__name__)

async def event_generator(
    request: Request, 
    user_id: str, 
    payload: ChatRequest, 
    db: AsyncSession
) -> AsyncGenerator[str, None]:
    """
    Async generator that yields SSE-formatted strings from LangGraph events.
    """
    thread_id = payload.thread_id or str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    logger.info(f"Initiating chat stream for user {user_id}, thread {thread_id}")
    
    try:
        # 1. Fetch user context
        user_context_data = await get_user_context_data(db, user_id)
        
        # 2. Prepare initial state
        initial_state = {
            "session_context": {
                "messages": [("user", payload.message)],
                "current_datetime": datetime.now(timezone.utc).isoformat(),
                "user_agent": "StockPlanner-FastAPI",
                "revision_count": 0
            },
            "user_context": {
                "user_id": user_id,
                "portfolio_summary": user_context_data.get("portfolio_summary", "N/A"),
                "portfolio": []
            },
            "user_input": payload.message,
            "agent_interactions": [],
            "output": ""
        }
        
        # 3. Stream graph events
        async with get_checkpointer() as checkpointer:
            graph = create_graph(checkpointer=checkpointer)
            
            async for event in graph.astream_events(
                initial_state,
                config,
                version="v2"
            ):
                # Handle client disconnect
                if await request.is_disconnected():
                    logger.info(f"Client disconnected for thread {thread_id}")
                    break
                
                kind = event["event"]
                
                # Token streaming
                if kind == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        token_event = ChatTokenEvent(content=content)
                        yield f"data: {token_event.model_dump_json()}

"
                
                # Node transitions
                elif kind == "on_chain_start":
                    node = event["metadata"].get("langgraph_node")
                    if node:
                        status_event = ChatStatusEvent(content=f"Agent {node.capitalize()} working...")
                        yield f"data: {status_event.model_dump_json()}

"

    except asyncio.CancelledError:
        logger.info(f"Chat stream cancelled for thread {thread_id}")
        # Note: Do not yield here as the connection is likely already closed
        raise
    except Exception as e:
        logger.error(f"Error in chat stream: {e}", exc_info=True)
        error_event = ChatErrorEvent(content="An unexpected error occurred during processing.")
        yield f"data: {error_event.model_dump_json()}

"

@router.post("/chat")
async def chat(
    request: Request,
    payload: ChatRequest,
    x_user_id: str = Header(..., alias="X-User-ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Streaming chat endpoint that provides real-time agent tokens and status updates using SSE.
    """
    return StreamingResponse(
        event_generator(request, x_user_id, payload, db),
        media_type="text/event-stream"
    )
