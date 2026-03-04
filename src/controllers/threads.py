from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, update
from src.database.session import get_db
from src.database.models import ChatThread, ChatMessage, User
from src.schemas.threads import ThreadListResponse, ThreadBase, MessageSchema, HistoryResponse, CursorInfo, ThreadRunStreamRequest
from src.services.auth import set_user_context
from src.services.history import backfill_history_if_needed
import logging
from datetime import datetime, timezone
from typing import Optional

router = APIRouter(tags=["Threads"])
logger = logging.getLogger(__name__)

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
            ChatThread.deleted_at == None
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Fetch threads
        query = select(ChatThread).where(
            ChatThread.user_id == current_user.id,
            ChatThread.deleted_at == None
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
        ChatThread.deleted_at == None
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
        ChatMessage.deleted_at == None
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
            role=m.role,
            content=m.content,
            timestamp=m.created_at
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
            ChatThread.deleted_at == None
        )
        result = await db.execute(query)
        thread = result.scalar_one_or_none()

        if not thread:
            raise HTTPException(status_code=404, detail="Not Found")

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        thread.deleted_at = now
        
        # Optionally soft-delete all messages in thread too
        # To be clean, we should probably do this to ensure they don't show up in global searches if added later
        from sqlalchemy import update
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
        ChatMessage.deleted_at == None
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(set_user_context)
):
    """
    Streams events from a graph run.
    Follows official LangGraph pathing for SDK compatibility.
    """
    # 1. Verify thread ownership (Stealth 404)
    thread_res = await db.execute(select(ChatThread).where(
        ChatThread.id == thread_id,
        ChatThread.user_id == current_user.id,
        ChatThread.deleted_at == None
    ))
    thread = thread_res.scalar_one_or_none()
    if not thread:
        raise HTTPException(status_code=404, detail="Not Found")

    async def event_generator():
        # Empty generator for now. 
        # Future phases will integrate the agent graph here.
        if False:
            yield "data: {}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
