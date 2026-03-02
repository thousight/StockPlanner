from typing import Dict, Any, Callable
import traceback
from functools import wraps
import asyncio
import inspect

def with_logging(func: Callable) -> Callable:
    """Decorator to catch, log, and re-throw exceptions in agent functions. Async-aware."""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        agent_name = func.__name__.replace('_agent', '').upper()
        print(f"\n--- {agent_name}: Starting ---")
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}: {e}\n{traceback.format_exc()}")
            raise

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        agent_name = func.__name__.replace('_agent', '').upper()
        print(f"\n--- {agent_name}: Starting ---")
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}: {e}\n{traceback.format_exc()}")
            raise

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper

def get_next_interaction_id(state: Dict[str, Any]) -> int:
    """Returns the next sequential interaction ID."""
    return len(state.get("agent_interactions", [])) + 1
