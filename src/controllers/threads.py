from fastapi import APIRouter, Header, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.database.session import get_db
from src.database.models import ChatThread, RecordStatus
from src.schemas.threads import ThreadListResponse, ThreadBase, ThreadHistoryResponse, MessageSchema
from src.graph.persistence import get_checkpointer
from src.graph.graph import create_graph
import logging
from datetime import datetime, timezone

router = APIRouter(tags=["Threads"])
logger = logging.getLogger(__name__)

@router.get("/threads", response_model=ThreadListResponse)
async def get_threads(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    x_user_id: str = Header(..., alias="X-User-ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns a paginated list of chat threads for the current user.
    """
    try:
        # Count total threads for this user
        count_query = select(func.count()).select_from(ChatThread).where(
            ChatThread.user_id == x_user_id,
            ChatThread.status == RecordStatus.ACTIVE
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Fetch threads
        query = select(ChatThread).where(
            ChatThread.user_id == x_user_id,
            ChatThread.status == RecordStatus.ACTIVE
        ).order_by(ChatThread.updated_at.desc()).offset(offset).limit(limit)
        
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
        logger.error(f"Error fetching threads for user {x_user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/threads/{thread_id}")
async def delete_thread(
    thread_id: str,
    x_user_id: str = Header(..., alias="X-User-ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft-deletes a chat thread.
    """
    try:
        query = select(ChatThread).where(
            ChatThread.id == thread_id,
            ChatThread.user_id == x_user_id,
            ChatThread.status == RecordStatus.ACTIVE
        )
        result = await db.execute(query)
        thread = result.scalar_one_or_none()

        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        thread.status = RecordStatus.INACTIVE

        await db.commit()
        
        return {"status": "success", "message": "Thread deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting thread {thread_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/threads/{thread_id}/messages", response_model=ThreadHistoryResponse)
async def get_thread_history(
    thread_id: str,
    limit: int = Query(50, ge=1, le=100),
    # before_timestamp: Optional[datetime] = Query(None), # For future pagination
    x_user_id: str = Header(..., alias="X-User-ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns a simplified history of messages for a chat thread.
    """
    try:
        # Verify thread ownership
        result = await db.execute(select(ChatThread).where(
            ChatThread.id == thread_id,
            ChatThread.user_id == x_user_id,
            ChatThread.status == RecordStatus.ACTIVE
        ))
        thread = result.scalar_one_or_none()
        
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
            
        async with get_checkpointer() as checkpointer:
            graph = create_graph(checkpointer=checkpointer)
            config = {"configurable": {"thread_id": thread_id}}
            state = await graph.aget_state(config)
            
            messages = []
            if state.values and "session_context" in state.values:
                session_messages = state.values["session_context"].get("messages", [])
                
                # Filter/Map messages to Simplified UI Schema
                for m in session_messages:
                    # Determine role
                    role = getattr(m, 'type', 'unknown')
                    if role == 'chat': # Some older langchain messages
                        role = 'ai'
                    elif role == 'human':
                        role = 'user'
                    
                    content = getattr(m, 'content', str(m))
                    
                    # Try to find a timestamp, fallback to thread updated_at
                    # In real apps, we'd store timestamp in message metadata
                    timestamp = getattr(m, 'response_metadata', {}).get('created_at', thread.created_at)
                    if isinstance(timestamp, int): # Unix timestamp
                        timestamp = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                    elif not isinstance(timestamp, datetime):
                        timestamp = thread.created_at
                        
                    messages.append(MessageSchema(
                        role=role,
                        content=content,
                        timestamp=timestamp
                    ))
            
            # Simple pagination from the in-memory list (newest messages first)
            # Reversing so UI gets messages in chronological order but we might want newest first for pagination
            # Plan says "simplified UI schema", usually chronological order is preferred for display.
            # But pagination usually starts from newest.
            
            # Let's keep chronological order but limit to the last 'limit' messages.
            paged_messages = messages[-limit:] if limit < len(messages) else messages
            
            return ThreadHistoryResponse(
                thread_id=thread_id,
                messages=paged_messages
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching history for thread {thread_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
