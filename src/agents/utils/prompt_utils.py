import inspect
from typing import List, Callable, Dict, Any

def convert_state_to_prompt(state: Dict[str, Any]) -> str:
    """
    Converts AgentState or a similar dict into a readable string for inclusion in LLM prompts.
    """
    context = []
    
    # 1. User Question
    if "user_question" in state:
        context.append(f"User Question: {state['user_question']}")
    
    # 2. High-Level Plan
    plan = state.get("high_level_plan", [])
    if plan:
        context.append(f"High-Level Plan: {', '.join(plan)}")
        
    # 3. Research Data
    research_data = state.get("research_data", {})
    if research_data:
        context.append("--- RESEARCH DATA ---")
        context.append(str(research_data))
        context.append("--- END RESEARCH DATA ---")
    else:
        context.append("Research Data: No data gathered yet.")

    # 4. Revision Count
    if "revision_count" in state:
        context.append(f"Revision Count: {state['revision_count']}")
    
    return "\n".join(context)

def _get_function_signature(func: Callable) -> str:
    """
    Helper to extract a clean string representation of a function's signature.
    """
    try:
        sig = inspect.signature(func)
        return str(sig)
    except Exception:
        return "(...)"

def convert_agents_to_prompt(agents: Dict[str, Callable]) -> str:
    """
    Converts a list of agent functions into a list of agent names, signatures, and descriptions.
    """
    descriptions = []
    for name, agent in agents.items():
        doc = (agent.__doc__ or "No description available.").strip()
        descriptions.append(f"- {name}: {doc}")
    return "\n".join(descriptions)

def convert_tools_to_prompt(tools: List[Callable]) -> str:
    """
    Converts a list of utility functions into a list of tool names, signatures, and descriptions.
    """
    descriptions = []
    for tool in tools:
        sig = _get_function_signature(tool)
        doc = (tool.__doc__ or "No description available.").strip()
        # Keep only the first line of docstring for brevity in prompts
        doc_first_line = doc.split('\n')[0].strip()
        descriptions.append(f"- {tool.__name__}{sig}: {doc_first_line}")
    return "\n".join(descriptions)
