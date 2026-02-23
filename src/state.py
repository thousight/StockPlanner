from typing import List, Dict, Any, TypedDict, Annotated, NotRequired
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

import operator

class AgentInteraction(TypedDict):
    """
    Represents a single step in the multi-agent workflow.
    - id: A unique integer ID for this interaction.
    - step_id: The ID of the high-level plan step this interaction fulfills.
    - agent: The agent that performed the work.
    - question: The instruction or task given to the CURRENT agent.
    - answer: The result or output produced by the CURRENT agent.
    - next_agent: The destination for the next step.
    - next_question: The instruction for the next agent.
    - debate_output: Structured metadata (only for Analyst agent).
    """
    id: int
    step_id: int
    agent: str
    question: str
    answer: str
    next_agent: str
    next_question: str
    debate_output: NotRequired[Dict[str, Any]]

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    portfolio: List[Dict[str, Any]]
    high_level_plan: List[Dict[str, Any]] # Changed from List[str] to List[Dict] to support IDs
    user_input: str
    current_datetime: str
    user_agent: str
    output: str
    analysis_cache_key: str
    revision_count: Annotated[int, operator.add]
    agent_interactions: Annotated[List[AgentInteraction], operator.add]
