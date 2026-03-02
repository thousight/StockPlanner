import inspect
from typing import List, Callable, Dict
from langchain_core.prompts import ChatPromptTemplate
from src.graph.state import AgentState

ARTICLE_SUMMARY_PROMPT = ChatPromptTemplate.from_template("""
Summarize the key financial insights from the following article. 
Focus on information relevant to stock analysis, market trends, and economic indicators.
Keep the summary concise (2-3 sentences).

Article Content:
{content}
""")

def convert_state_to_prompt(state: AgentState) -> str:
    """
    Converts AgentState or a similar dict into a readable string for inclusion in LLM prompts.
    """
    context = []
    
    if "user_input" in state:
        context.append(f"User Input: {state['user_input']}")
        
    session_ctx = state.get("session_context", {})
        
    # 2. Current Datetime
    if "current_datetime" in session_ctx:
        context.append(f"Current Date/Time: {session_ctx['current_datetime']}")
        
    # 3. Chat History
    messages = session_ctx.get("messages", [])
    if messages:
        context.append("--- CHAT HISTORY ---")
        for msg in messages:
            # Handle both BaseMessage objects and tuples
            if isinstance(msg, tuple):
                role, content = msg
                role_label = "User" if role in ["human", "user"] else "AI"
                context.append(f"{role_label}: {content}")
            else:
                role = getattr(msg, "type", "")
                content = getattr(msg, "content", str(msg))
                role_label = "User" if role in ["human", "user"] else "AI"
                context.append(f"{role_label}: {content}")
        context.append("--- END CHAT HISTORY ---")
    else:
        context.append("Chat History: None.")
        
    # 4. Agent Interactions
    interactions = state.get("agent_interactions", [])
    if interactions:
        context.append("--- AGENT INTERACTIONS ---")
        for itr in interactions:
            agent = itr.get("agent", "unknown")
            answer = itr.get("answer", "")
            dest = itr.get("next_agent", "end")
            context.append(f"[{agent} -> {dest}]: {answer}")
        context.append("--- END AGENT INTERACTIONS ---")
    else:
        context.append("Agent Interactions: None.")

    # 5. Revision Count
    if "revision_count" in session_ctx:
        context.append(f"Revision Count: {session_ctx['revision_count']}")

    # 6. User Portfolio Summary
    user_ctx = state.get("user_context", {})
    if "portfolio_summary" in user_ctx and user_ctx["portfolio_summary"]:
        context.append("--- USER PORTFOLIO SUMMARY ---")
        context.append(user_ctx["portfolio_summary"])
        context.append("--- END USER PORTFOLIO SUMMARY ---")
    
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
