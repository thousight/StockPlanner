from typing import List, Dict, Any, TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

import operator

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    portfolio: List[Dict[str, Any]]
    high_level_plan: List[str]
    research_plan: List[str]
    research_data: str
    user_question: str
    current_datetime: str
    user_agent: str
    analysis_report: str
    next_agent: str
    debate_output: Dict[str, Any]
    analysis_cache_key: str
    revision_count: Annotated[int, operator.add]
