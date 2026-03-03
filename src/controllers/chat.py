import asyncio
import logging
from uuid import uuid4
from datetime import datetime, timezone
from typing import AsyncGenerator, Optional
from langgraph.types import Command

from fastapi import APIRouter, Request, Header, Depends, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.session import get_db
from src.database.models import ChatThread
from src.schemas.chat import ChatRequest, ChatTokenEvent, ChatStatusEvent, ChatErrorEvent
from src.graph.graph import create_graph
from src.graph.persistence import get_checkpointer
from src.services.context_injection import get_user_context_data
from src.services.titler import update_thread_title_background

router = APIRouter(tags=["Chat"])
logger = logging.getLogger(__name__)

async def event_generator(
    request: Request, 
    user_id: str, 
    payload_message: str, 
    db: AsyncSession,
    background_tasks: BackgroundTasks,
    thread_id: str,
    is_new_thread: bool = False
) -> AsyncGenerator[str, None]:
    """
    Async generator that yields SSE-formatted strings from LangGraph events.
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    logger.info(f"Initiating chat stream for user {user_id}, thread {thread_id}")
    
    full_response_content = ""
    
    try:
        # 1. Prepare inputs
        user_context_data = await get_user_context_data(db, user_id)
        initial_state = {
            "session_context": {
                "messages": [("user", payload_message)],
                "current_datetime": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
                "user_agent": "StockPlanner-FastAPI",
                "revision_count": 0
            },
            "user_context": {
                "user_id": user_id,
                "portfolio_summary": user_context_data.get("portfolio_summary", "N/A"),
                "portfolio": []
            },
            "user_input": payload_message,
            "agent_interactions": [],
            "output": ""
        }
        
        # 2. Stream graph events
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
                        full_response_content += content
                        token_event = ChatTokenEvent(content=content)
                        yield f"data: {token_event.model_dump_json()}\n\n"
                
                # Node transitions
                elif kind == "on_chain_start":
                    node = event["metadata"].get("langgraph_node")
                    if node:
                        status_event = ChatStatusEvent(content=f"Agent {node.capitalize()} working...")
                        yield f"data: {status_event.model_dump_json()}\n\n"

        # 3. Trigger background titling if it's the first exchange
        if is_new_thread and full_response_content and payload_message:
            background_tasks.add_task(
                update_thread_title_background,
                thread_id,
                payload_message,
                full_response_content
            )

    except asyncio.CancelledError:
        logger.info(f"Chat stream cancelled for thread {thread_id}")
        raise
    except Exception as e:
        logger.error(f"Error in chat stream: {e}", exc_info=True)
        error_event = ChatErrorEvent(content="An unexpected error occurred during processing.")
        yield f"data: {error_event.model_dump_json()}\n\n"

@router.post("/chat")
async def chat(
    request: Request,
    payload: ChatRequest,
    background_tasks: BackgroundTasks,
    x_user_id: str = Header(..., alias="X-User-ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Streaming chat endpoint that provides real-time agent tokens and status updates using SSE.
    """
    # Determine thread_id
    thread_id = payload.thread_id or str(uuid4())
    
    # Ensure thread exists in database
    result = await db.execute(select(ChatThread).where(ChatThread.id == thread_id))
    thread = result.scalar_one_or_none()
    
    is_new_thread = False
    if not thread:
        is_new_thread = True
        thread = ChatThread(
            id=thread_id,
            user_id=x_user_id,
            title="New Conversation"
        )
        db.add(thread)
        await db.commit()
    
    return StreamingResponse(
        event_generator(
            request, 
            x_user_id, 
            payload.message, 
            db, 
            background_tasks, 
            thread_id, 
            is_new_thread
        ),
        media_type="text/event-stream",
        headers={"X-Thread-ID": thread_id}
    )
