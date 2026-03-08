from typing import List, Dict, Any, TypedDict, Annotated
from typing_extensions import NotRequired
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

import operator

class AgentInteraction(TypedDict):
    """
    Represents a single step in the multi-agent workflow.
    - id: A unique integer ID for this interaction.
    - agent: The agent that performed the work.
    - answer: The result or output produced by the CURRENT agent.
    - next_agent: The destination for the next step.
    - debate_output: Optional metadata for the Analyst agent.
    """
    id: int
    agent: str
    answer: str
    next_agent: str
    debate_output: NotRequired[Dict[str, Any]]

class SessionContext(TypedDict):
    current_datetime: str
    user_agent: str
    messages: Annotated[List[BaseMessage], add_messages]

class UserContext(TypedDict):
    portfolio: List[Dict[str, Any]]
    portfolio_summary: NotRequired[str]
    user_id: NotRequired[str]

def merge_session_context(left: SessionContext, right: SessionContext) -> SessionContext:
    """
    Custom merger for SessionContext.
    Ensures that messages are appended using add_messages,
    while other fields (current_datetime, user_agent) are updated if present in right.
    """
    if not left:
        return right
    if not right:
        return left
        
    res = {**left, **right}
    
    # Explicitly merge messages using LangGraph's add_messages logic
    res["messages"] = add_messages(left.get("messages", []), right.get("messages", []))
    
    return res

def merge_user_context(left: UserContext, right: UserContext) -> UserContext:
    """
    Custom merger for UserContext.
    Ensures that portfolio and other fields are merged.
    """
    if not left:
        return right
    if not right:
        return left
        
    res = {**left, **right}
    return res

class AgentState(TypedDict):
    session_context: Annotated[SessionContext, merge_session_context]
    user_context: Annotated[UserContext, merge_user_context]
    user_input: str
    agent_interactions: Annotated[List[AgentInteraction], operator.add]
    revision_count: int
    code_revision_count: int
    output: str
    market_context: NotRequired[str]
