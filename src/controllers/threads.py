from fastapi import APIRouter, Depends, Query, HTTPException, BackgroundTasks, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, update
from src.database.session import get_db
from src.database.models import ChatThread, ChatMessage, User
from src.schemas.threads import ThreadListResponse, ThreadBase, MessageSchema, HistoryResponse, CursorInfo, ThreadRunStreamRequest, ThreadCreate
from src.services.auth import set_user_context
from src.services.history import backfill_history_if_needed, sync_conversation_background
from src.services.context_injection import get_user_context_data
from src.services.titler import update_thread_title_background
from src.graph.graph import create_graph
from src.graph.persistence import get_checkpointer
from langchain_core.messages import HumanMessage
import logging
import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Any

router = APIRouter(tags=["Threads"])
logger = logging.getLogger(__name__)

def default_serializer(obj: Any) -> Any:
    """
    Custom JSON serializer for LangChain/LangGraph objects.
    """
    if hasattr(obj, "to_json"):
        return obj.to_json()
    if hasattr(obj, "dict"):
        return obj.dict()
    return str(obj)

async def langgraph_event_generator(
    thread_id: str,
    initial_input: dict,
    request: ThreadRunStreamRequest,
    current_user: User,
    background_tasks: BackgroundTasks,
    thread_title: Optional[str],
    payload_message: Optional[str]
) -> Any:
    """
    Async generator that yields SSE-formatted strings from LangGraph events.
    Moved to module level to avoid re-initialization overhead.
    """
    full_response_content = ""
    try:
        async with get_checkpointer() as checkpointer:
            graph = create_graph(checkpointer=checkpointer)
            
            # Merge user config with mandatory thread_id
            config = (request.config or {}).copy()
            config["configurable"] = {
                **config.get("configurable", {}),
                "thread_id": thread_id
            }
            
            if request.checkpoint_id:
                config["configurable"]["checkpoint_id"] = request.checkpoint_id

            # Run graph stream
            async for mode, data in graph.astream(
                initial_input, 
                config, 
                stream_mode=request.stream_mode
            ):
                # Protocol specifies that 'data' lines must be JSON arrays
                payload = json.dumps([data], default=default_serializer)
                yield f"event: {mode}\ndata: {payload}\n\n"
                
                # Capture content for titling
                if mode == "messages":
                    if isinstance(data, list) and len(data) > 0:
                        chunk = data[0]
                        if hasattr(chunk, "content"):
                            full_response_content += str(chunk.content)
            
            # Success signal
            yield "event: end\ndata: {}\n\n"
            
            # 3. Background Sync & Titling
            # Use a fresh config with ONLY thread_id to ensure we get the LATEST state
            # (If config has checkpoint_id from request, aget_state returns the old snapshot)
            latest_config = {"configurable": {"thread_id": thread_id}}
            final_state = await graph.aget_state(latest_config)
            
            if final_state.values and "session_context" in final_state.values:
                final_messages = final_state.values["session_context"].get("messages", [])
                if final_messages:
                    background_tasks.add_task(
                        sync_conversation_background,
                        thread_id,
                        current_user.id,
                        final_messages
                    )
            
            if thread_title == "New Conversation" and full_response_content and payload_message:
                background_tasks.add_task(
                    update_thread_title_background,
                    thread_id,
                    payload_message,
                    full_response_content
                )

    except Exception as e:
        logger.error(f"Error in graph stream: {e}", exc_info=True)
        error_payload = json.dumps([{"detail": str(e)}])
        yield f"event: error\ndata: {error_payload}\n\n"

@router.post("/threads", response_model=ThreadBase, status_code=201)
async def create_thread(
    request: ThreadCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(set_user_context)
):
    """
    Creates a new chat thread for the current user.
    """
    try:
        thread_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        new_thread = ChatThread(
            id=thread_id,
            user_id=current_user.id,
            title=request.title or "New Conversation",
            created_at=now,
            updated_at=now
        )
        db.add(new_thread)
        await db.commit()
        await db.refresh(new_thread)
        
        return ThreadBase(
            id=new_thread.id,
            title=new_thread.title,
            created_at=new_thread.created_at,
            updated_at=new_thread.updated_at
        )
    except Exception as e:
        logger.error(f"Error creating thread for user {current_user.id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/threads", response_model=ThreadListResponse)
async def get_threads(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(set_user_context)
):
    """
    Returns a paginated list of chat threads for the current user.
    """
    try:
        # Count total threads for this user (not soft-deleted)
        count_query = select(func.count()).select_from(ChatThread).where(
            ChatThread.user_id == current_user.id,
            ChatThread.deleted_at.is_(None)
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Fetch threads
        query = select(ChatThread).where(
            ChatThread.user_id == current_user.id,
            ChatThread.deleted_at.is_(None)
        ).order_by(desc(ChatThread.updated_at)).offset(offset).limit(limit)
        
        result = await db.execute(query)
        threads = result.scalars().all()
        
        return ThreadListResponse(
            threads=[ThreadBase(
                id=t.id,
                title=t.title or "New Conversation",
                created_at=t.created_at,
                updated_at=t.updated_at
            ) for t in threads],
            total=total
        )
    except Exception as e:
        logger.error(f"Error fetching threads for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/threads/{thread_id}/history", response_model=HistoryResponse)
async def get_history(
    thread_id: str,
    limit: int = Query(20, ge=1, le=100),
    cursor: Optional[str] = Query(None, description="The ID of the last message seen (for pagination)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(set_user_context)
):
    """
    Returns paginated human-readable conversation history from PostgreSQL.
    Triggers on-the-fly backfill if relational history is missing.
    """
    # 1. Verify thread ownership (Stealth 404)
    thread_res = await db.execute(select(ChatThread).where(
        ChatThread.id == thread_id,
        ChatThread.user_id == current_user.id,
        ChatThread.deleted_at.is_(None)
    ))
    thread = thread_res.scalar_one_or_none()
    if not thread:
        raise HTTPException(status_code=404, detail="Not Found")

    # 2. Backfill if needed
    await backfill_history_if_needed(db, thread_id, current_user.id)

    # 3. Query messages with cursor-based pagination
    # Using keyset pagination on UUIDv7 (time-ordered)
    query = select(ChatMessage).where(
        ChatMessage.thread_id == thread_id,
        ChatMessage.deleted_at.is_(None)
    )
    
    if cursor:
        query = query.where(ChatMessage.id < cursor)
    
    # We fetch limit + 1 to check if there are more pages
    query = query.order_by(desc(ChatMessage.id)).limit(limit + 1)
    
    result = await db.execute(query)
    messages = result.scalars().all()
    
    has_more = len(messages) > limit
    if has_more:
        messages = messages[:limit]
        next_cursor = messages[-1].id
    else:
        next_cursor = None

    return HistoryResponse(
        thread_id=thread_id,
        messages=[MessageSchema(
            id=m.id,
            type=m.role.lower(),
            content=m.content,
            custom_id=m.langchain_msg_id
        ) for m in messages],
        cursor=CursorInfo(
            next_cursor=next_cursor,
            has_more=has_more
        )
    )

@router.delete("/threads/{thread_id}", status_code=204)
async def delete_thread(
    thread_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(set_user_context)
):
    """
    Soft-deletes a chat thread and all its messages.
    """
    try:
        query = select(ChatThread).where(
            ChatThread.id == thread_id,
            ChatThread.user_id == current_user.id,
            ChatThread.deleted_at.is_(None)
        )
        result = await db.execute(query)
        thread = result.scalar_one_or_none()

        if not thread:
            raise HTTPException(status_code=404, detail="Not Found")

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        thread.deleted_at = now
        
        # Soft-delete all messages in thread too
        await db.execute(
            update(ChatMessage)
            .where(ChatMessage.thread_id == thread_id)
            .values(deleted_at=now)
        )

        await db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting thread {thread_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/threads/{thread_id}/messages/{message_id}", status_code=204)
async def delete_message(
    thread_id: str,
    message_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(set_user_context)
):
    """
    Soft-deletes a specific message.
    """
    query = select(ChatMessage).where(
        ChatMessage.id == message_id,
        ChatMessage.thread_id == thread_id,
        ChatMessage.user_id == current_user.id,
        ChatMessage.deleted_at.is_(None)
    )
    result = await db.execute(query)
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(status_code=404, detail="Not Found")
        
    message.deleted_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await db.commit()
    return None

@router.post("/threads/{thread_id}/runs/stream")
async def stream_run(
    thread_id: str,
    request: ThreadRunStreamRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(set_user_context),
    user_agent: Optional[str] = Header(None)
):
    """
    Streams events from a graph run.
    Follows official LangGraph pathing for SDK compatibility.
    """
    # 1. Verify thread ownership (Stealth 404)
    thread_res = await db.execute(select(ChatThread).where(
        ChatThread.id == thread_id,
        ChatThread.user_id == current_user.id,
        ChatThread.deleted_at.is_(None)
    ))
    thread = thread_res.scalar_one_or_none()
    if not thread:
        raise HTTPException(status_code=404, detail="Not Found")

    # 2. Prepare inputs (Context Injection)
    initial_input = request.input or {}
    payload_message = None
    
    if "message" in initial_input:
        payload_message = initial_input.pop("message")
        user_context_data = await get_user_context_data(db, current_user.id)
        
        # We need a stable ID for the human message for idempotency in PostgreSQL
        human_msg_id = str(uuid.uuid4())
        
        # Build standard initial state
        initial_input = {
            "session_context": {
                "messages": [HumanMessage(content=payload_message, id=human_msg_id)],
                "current_datetime": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
                "user_agent": user_agent or "StockPlanner-FastAPI",
                "revision_count": 0
            },
            "user_context": {
                "user_id": current_user.id,
                "first_name": current_user.first_name,
                "risk_tolerance": current_user.risk_tolerance.value if hasattr(current_user.risk_tolerance, "value") else str(current_user.risk_tolerance),
                "base_currency": current_user.base_currency,
                "portfolio_summary": user_context_data.get("portfolio_summary", "N/A"),
                "portfolio": []
            },
            "user_input": payload_message,
            "agent_interactions": [],
            "output": ""
        }

    return StreamingResponse(
        langgraph_event_generator(
            thread_id=thread_id,
            initial_input=initial_input,
            request=request,
            current_user=current_user,
            background_tasks=background_tasks,
            thread_title=thread.title,
            payload_message=payload_message
        ), 
        media_type="text/event-stream"
    )
