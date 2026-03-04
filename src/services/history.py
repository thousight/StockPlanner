from typing import List, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from src.database.models import ChatMessage, ChatThread
import logging

logger = logging.getLogger(__name__)

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
                ChatThread.deleted_at == None
            )
        )
        thread = result.scalar_one_or_none()
        if not thread:
            logger.warning(f"Thread {thread_id} not found or deleted for user {user_id}. Skipping sync.")
            return

        sync_count = 0
        for msg in new_messages:
            # Map roles
            if isinstance(msg, HumanMessage):
                role = "Human"
            elif isinstance(msg, AIMessage):
                role = "AI"
            elif isinstance(msg, SystemMessage):
                # We skip System messages for UI history usually
                continue
            else:
                # Generic fallback for other message types (ToolMessage etc.)
                # For now, we only sync Human and AI roles as per requirement.
                continue

            # Check if message already exists by langchain_msg_id
            # Note: msg.id is where LangChain stores the unique message ID
            msg_id = getattr(msg, "id", None)
            if not msg_id:
                logger.warning(f"Message in thread {thread_id} missing ID. Content: {msg.content[:50]}...")
                continue

            # Upsert logic
            stmt = select(ChatMessage).where(ChatMessage.langchain_msg_id == msg_id)
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
