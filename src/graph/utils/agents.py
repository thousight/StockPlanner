from typing import Dict, Any, Callable
import traceback
from functools import wraps
import inspect
import logging
from asgi_correlation_id import correlation_id

logger = logging.getLogger(__name__)

def with_logging(func: Callable) -> Callable:
    """Decorator to catch, log, and re-throw exceptions in agent functions. Async-aware."""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        agent_name = func.__name__.replace('_agent', '').upper()
        thread_id = "N/A"
        
        # Try to extract thread_id from config if available in kwargs
        config = kwargs.get("config")
        if config and isinstance(config, dict):
            thread_id = config.get("configurable", {}).get("thread_id", "N/A")
        
        request_id = correlation_id.get() or "N/A"
        
        logger.info(f"[{agent_name}] [Thread: {thread_id}] [Request: {request_id}] Starting...")
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"[{agent_name}] [Thread: {thread_id}] [Request: {request_id}] Error: {e}\n{traceback.format_exc()}")
            raise

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        agent_name = func.__name__.replace('_agent', '').upper()
        # Note: sync wrapper is legacy and doesn't easily access context headers
        logger.info(f"[{agent_name}] Starting (sync)...")
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"[{agent_name}] Error (sync): {e}\n{traceback.format_exc()}")
            raise

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper

def get_next_interaction_id(state: Dict[str, Any]) -> int:
    """Returns the next sequential interaction ID."""
    return len(state.get("agent_interactions", [])) + 1
