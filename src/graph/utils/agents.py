import inspect
import logging
import traceback
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from asgi_correlation_id import correlation_id
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

def get_llm(temperature: float = 0, model: str = "gpt-4o") -> ChatOpenAI:
    """
    Returns a configured ChatOpenAI instance.
    """
    return ChatOpenAI(model=model, temperature=temperature)

def get_session_info(state: Dict[str, Any]) -> Dict[str, str]:
    """
    Extracts common session metadata from state.
    """
    ctx = state.get("session_context", {})
    return {
        "user_agent": ctx.get("user_agent", "StockPlanner-FastAPI"),
        "thread_id": ctx.get("thread_id", "N/A"),
        "request_id": correlation_id.get() or "N/A"
    }

def get_next_interaction_id(state: Dict[str, Any]) -> int:
    """Returns the next sequential interaction ID."""
    return len(state.get("agent_interactions", [])) + 1

def create_interaction(
    state: Dict[str, Any], 
    agent: str, 
    answer: str, 
    next_agent: str, 
    **kwargs
) -> Dict[str, Any]:
    """
    Helper to create a standard AgentInteraction dictionary.
    """
    interaction = {
        "id": get_next_interaction_id(state),
        "agent": agent,
        "answer": answer,
        "next_agent": next_agent
    }
    interaction.update(kwargs)
    return interaction

def with_logging(func: Callable) -> Callable:
    """Decorator to catch, log, and re-throw exceptions in agent functions. Async-aware."""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        agent_name = func.__name__.replace('_agent', '').upper()
        state = args[0] if args else {}
        info = get_session_info(state)
        
        logger.info(f"[{agent_name}] [Thread: {info['thread_id']}] [Request: {info['request_id']}] Starting...")
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"[{agent_name}] [Thread: {info['thread_id']}] [Request: {info['request_id']}] Error: {e}\n{traceback.format_exc()}")
            raise

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        agent_name = func.__name__.replace('_agent', '').upper()
        logger.info(f"[{agent_name}] Starting (sync)...")
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"[{agent_name}] Error (sync): {e}\n{traceback.format_exc()}")
            raise

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
