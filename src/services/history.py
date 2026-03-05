import hashlib
import logging
from typing import List
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from src.database.models import ChatMessage, ChatThread
from src.database.session import AsyncSessionLocal
from src.graph.persistence import get_checkpointer
from src.graph.graph import create_graph

logger = logging.getLogger(__name__)

async def backfill_history_if_needed(db: AsyncSession, thread_id: str, user_id: str):
    """
    Checks if relational history exists for a thread. If not, attempts to backfill
    from the LangGraph checkpointer.
    """
    # 1. Check if any messages exist in relational DB
    stmt = select(func.count()).select_from(ChatMessage).where(
        ChatMessage.thread_id == thread_id,
        ChatMessage.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    count = result.scalar()
    
    if count > 0:
        # History already exists in relational DB, no backfill needed
        return

    logger.info(f"Relational history missing for thread {thread_id}. Attempting backfill from checkpointer.")
    
    # 2. Fetch state from LangGraph
    async with get_checkpointer() as checkpointer:
        graph = create_graph(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": thread_id}}
        state = await graph.aget_state(config)
        
        if state.values and "session_context" in state.values:
            messages = state.values["session_context"].get("messages", [])
            if messages:
                # 3. Sync to Postgres
                await sync_conversation_to_postgres(db, thread_id, user_id, messages)

async def sync_conversation_background(
    thread_id: str, 
    user_id: str, 
    new_messages: List[BaseMessage]
):
    """
    Wrapper for sync_conversation_to_postgres that manages its own database session.
    Suitable for use with FastAPI BackgroundTasks.
    """
    async with AsyncSessionLocal() as db:
        await sync_conversation_to_postgres(db, thread_id, user_id, new_messages)

async def sync_conversation_to_postgres(
    db: AsyncSession, 
    thread_id: str, 
    user_id: str, 
    new_messages: List[BaseMessage]
):
    """
    Promotes LangGraph state messages to PostgreSQL ChatMessage table.
    Uses langchain_msg_id for idempotency (upsert).
    
    Args:
        db: AsyncSession for database operations.
        thread_id: The thread ID to sync.
        user_id: The user ID owning the thread.
        new_messages: A list of LangChain messages (HumanMessage, AIMessage, etc.).
    """
    if not new_messages:
        return

    try:
        # 1. Check if thread exists and is not soft-deleted
        # We use a subquery or join if needed, but here simple select is enough.
        result = await db.execute(
            select(ChatThread).where(
                ChatThread.id == thread_id,
                ChatThread.user_id == user_id,
                ChatThread.deleted_at.is_(None)
            )
        )
        thread = result.scalar_one_or_none()
        if not thread:
            logger.warning(f"Thread {thread_id} not found or deleted for user {user_id}. Skipping sync.")
            return

        sync_count = 0
        for msg in new_messages:
            # Map roles
            if isinstance(msg, HumanMessage) or getattr(msg, 'type', None) == 'human':
                role = "Human"
            elif isinstance(msg, AIMessage) or getattr(msg, 'type', None) == 'ai':
                role = "AI"
            elif isinstance(msg, SystemMessage) or getattr(msg, 'type', None) == 'system':
                continue
            else:
                continue

            # Check if message already exists by langchain_msg_id
            msg_id = getattr(msg, "id", None)
            
            # If ID is missing, generate a deterministic one based on content to prevent duplicates
            if not msg_id:
                content_str = str(msg.content)
                msg_id = f"gen-{hashlib.sha256(f'{thread_id}-{role}-{content_str}'.encode()).hexdigest()[:16]}"
                logger.debug(f"Generated deterministic ID {msg_id} for message in thread {thread_id}")

            # Upsert logic
            stmt = select(ChatMessage).where(
                ChatMessage.thread_id == thread_id,
                ChatMessage.langchain_msg_id == msg_id
            )
            existing_msg_res = await db.execute(stmt)
            existing_msg = existing_msg_res.scalar_one_or_none()

            if existing_msg:
                # Update content if it changed (rare but good for idempotency)
                if existing_msg.content != msg.content:
                    existing_msg.content = msg.content
                    sync_count += 1
            else:
                # Create new record
                new_chat_msg = ChatMessage(
                    user_id=user_id,
                    thread_id=thread_id,
                    role=role,
                    content=msg.content,
                    langchain_msg_id=msg_id
                )
                db.add(new_chat_msg)
                sync_count += 1
        
        if sync_count > 0:
            await db.commit()
            logger.info(f"Successfully synced {sync_count} messages to Postgres for thread {thread_id}")
        else:
            logger.debug(f"No new messages to sync for thread {thread_id}")

    except Exception as e:
        await db.rollback()
        logger.error(f"Error syncing conversation to Postgres for thread {thread_id}: {str(e)}", exc_info=True)
        # We don't re-raise as this is intended to be used in background tasks
