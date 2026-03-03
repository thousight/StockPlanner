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
    revision_count: Annotated[int, operator.add]

class UserContext(TypedDict):
    portfolio: List[Dict[str, Any]]
    portfolio_summary: NotRequired[str]
    user_id: NotRequired[str]

class AgentState(TypedDict):
    session_context: SessionContext
    user_context: UserContext
    user_input: str
    agent_interactions: Annotated[List[AgentInteraction], operator.add]
    output: str
