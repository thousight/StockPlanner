from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from src.database.session import AsyncSessionLocal
from src.database.models import ChatThread
from sqlalchemy import select
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

TITLER_PROMPT = """
Summarize the initial exchange between a user and a financial AI into a catchy, 3-5 word title.
Return ONLY the title text. No quotes, no prefix.

User: {user_msg}
AI: {ai_msg}

Title:"""

async def generate_thread_title(user_msg: str, ai_msg: str) -> str:
    """
    Generates a 3-5 word title for a chat thread based on the initial exchange.
    """
    try:
        # Using gpt-4o-mini as requested in RESEARCH.md for cost efficiency
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        prompt = TITLER_PROMPT.format(user_msg=user_msg, ai_msg=ai_msg)
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        title = response.content.strip().strip('"').strip("'")
        # Ensure it's not too long, though the prompt should handle it
        if len(title.split()) > 10:
            title = " ".join(title.split()[:5]) + "..."
        return title
    except Exception as e:
        logger.error(f"Error generating thread title: {e}")
        return "New Chat"

async def update_thread_title_background(thread_id: str, user_msg: str, ai_msg: str):
    """
    Background task to generate and update the thread title.
    """
    title = await generate_thread_title(user_msg, ai_msg)
    
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(ChatThread).where(ChatThread.id == thread_id))
            thread = result.scalar_one_or_none()
            if thread:
                thread.title = title
                thread.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
                await session.commit()
                logger.info(f"Updated title for thread {thread_id}: {title}")
            else:
                logger.warning(f"Thread {thread_id} not found when updating title.")
        except Exception as e:
            logger.error(f"Error updating thread title in DB: {e}")
            await session.rollback()
