from typing import Dict, Any, Callable
import traceback
from functools import wraps

def with_logging(func: Callable) -> Callable:
    """Decorator to catch, log, and re-throw exceptions in agent functions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        agent_name = func.__name__.replace('_agent', '').upper()
        print(f"--- {agent_name}: Starting ---")
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}: {e}\n{traceback.format_exc()}")
            raise
    return wrapper

def get_next_interaction_id(state: Dict[str, Any]) -> int:
    """Returns the next sequential interaction ID."""
    return len(state.get("agent_interactions", [])) + 1

def format_interactions_as_text(state: Dict[str, Any]) -> str:
    """Standardizes the text representation of agent interactions for prompts."""
    interactions_text = ""
    for idx, interaction in enumerate(state.get("agent_interactions", [])):
        agent = interaction.get('agent', 'unknown')
        interactions_text += f"--- Interaction {idx + 1} ({agent} agent) ---\n"
        interactions_text += f"Answer/Output from {agent}: {interaction.get('answer', '')}\n\n"
    return interactions_text
