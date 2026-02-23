import inspect
from typing import List, Callable, Dict, Any
from langchain_core.prompts import ChatPromptTemplate

ARTICLE_SUMMARY_PROMPT = ChatPromptTemplate.from_template("""
Summarize the key financial insights from the following article. 
Focus on information relevant to stock analysis, market trends, and economic indicators.
Keep the summary concise (2-3 sentences).

Article Content:
{content}
""")

def convert_state_to_prompt(state: Dict[str, Any]) -> str:
    """
    Converts AgentState or a similar dict into a readable string for inclusion in LLM prompts.
    """
    context = []
    
    if "user_input" in state:
        context.append(f"User Input: {state['user_input']}")
        
    # 2. Current Datetime
    if "current_datetime" in state:
        context.append(f"Current Date/Time: {state['current_datetime']}")
        
    # 3. High-Level Plan
    plan = state.get("high_level_plan", [])
    if plan:
        # Compatibility check: if it's a list of dicts (new) or list of strings (old)
        if plan and isinstance(plan[0], dict):
            plan_str = ", ".join([f"{item.get('id', '?')}. {item.get('description', '')}" for item in plan])
        else:
            plan_str = ", ".join(plan)
        context.append(f"High-Level Plan: {plan_str}")
        
    # 4. Chat History
    messages = state.get("messages", [])
    if messages:
        context.append("--- CHAT HISTORY ---")
        for msg in messages:
            # Determine role based on message type
            role = "User" if msg.type in ["human", "user"] else "AI"
            context.append(f"{role}: {msg.content}")
        context.append("--- END CHAT HISTORY ---")
    else:
        context.append("Chat History: None.")
        
    # 5. Research Data (from interactions)
    research_interaction = next((i for i in reversed(state.get("agent_interactions", [])) if i.get("agent") == "research"), None)
    if research_interaction:
        context.append("--- RESEARCH DATA ---")
        context.append(str(research_interaction.get("answer", "No data gathered.")))
        context.append("--- END RESEARCH DATA ---")
    else:
        context.append("Research Data: No data gathered yet.")

    # 6. Revision Count
    if "revision_count" in state:
        context.append(f"Revision Count: {state['revision_count']}")
    
    return "\n".join(context)

def _get_function_signature(func: Callable) -> str:
    """Extracts a clean string representing the function's signature, skipping kwargs."""
    sig = inspect.signature(func)
    
    # Filter out **kwargs so the LLM doesn't see them
    filtered_params = []
    for name, param in sig.parameters.items():
        if param.kind != inspect.Parameter.VAR_KEYWORD:
            filtered_params.append(param)
            
    # Reconstruct signature
    new_sig = sig.replace(parameters=filtered_params)
    return str(new_sig)

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
        sig_str = _get_function_signature(tool)
        doc = (tool.__doc__ or "No description available.").strip()
        # Keep only the first line of docstring for brevity in prompts
        doc_first_line = doc.split('\n')[0].strip()
        descriptions.append(f"- {tool.__name__}{sig_str}: {doc_first_line}")
    return "\n".join(descriptions)
