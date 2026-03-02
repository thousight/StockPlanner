from typing import List, Dict, Any, TypedDict, Annotated, NotRequired
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

class PendingReport(TypedDict):
    """
    Represents a report that is ready to be committed to the database.
    - title: Explicit title for the report.
    - category: Explicit category (e.g. STOCK, REAL_ESTATE, MACRO, FUND, GENERAL).
    - topic: Unified subject field (e.g. 'NVDA', 'Seattle Housing').
    - symbol: Optional ticker symbol.
    - tags: List of generated tags (e.g. #growth, #risk).
    - content: The full Markdown content of the report.
    - complexity_score: Normalized score (0-100) indicating text depth/risk.
    """
    title: str
    category: str
    topic: str
    symbol: NotRequired[str]
    tags: List[str]
    content: str
    complexity_score: float

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
    pending_report: NotRequired[PendingReport]
    last_report_id: NotRequired[int]
